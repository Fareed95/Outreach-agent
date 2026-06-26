"""
agents/research/agent.py
------------------------
Research Agent — Two responsibilities:

1. NicheSuggester: Takes user goal + about → suggests 5 niches
2. NicheResearchAgent: Takes niche + location → finds 10 businesses
   - Generates 5 search queries via LLM
   - Runs all queries via SearXNG/Serper
   - Deduplicates results
   - Extracts business info via LLM
   - Researches niche pain points
   - Caches niche research in DB (niche_research table)
   - Saves businesses to DB (businesses table)
"""

import json
import asyncio
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from config.settings import settings
from utils.logger import logger
from utils.retry import async_retry
from utils.search_provider import web_search, SearchResult
from db.database import get_async_session
from db.models import NicheResearchModel, BusinessModel  # SQLAlchemy models
from agents.research.schema import (
    NicheResearch, Business, NicheSuggestion,
    ResearchAgentInput, ResearchAgentOutput
)
from agents.research.prompts import (
    NICHE_SUGGESTER_PROMPT,
    SEARCH_QUERY_GENERATOR_PROMPT,
    BUSINESS_EXTRACTOR_PROMPT,
    PAIN_POINT_ANALYZER_PROMPT
)


# OpenRouter client — openai-compatible
client = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url=settings.OPENROUTER_BASE_URL,
)


async def _llm_call(prompt: str, temperature: float = 0.3) -> str:
    """Single LLM call via OpenRouter. Returns raw text response."""
    response = await client.chat.completions.create(
        model=settings.OPENROUTER_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=2000,
    )
    return response.choices[0].message.content.strip()


def _parse_json_response(raw: str) -> any:
    """
    Safely parse LLM JSON response.
    Strips markdown code blocks if present.
    """
    # Remove markdown code blocks if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1])  # Remove first and last line
    cleaned = cleaned.strip()
    return json.loads(cleaned)


class NicheSuggester:
    """
    Takes user goal + about → suggests 5 niches via LLM.
    Used when user doesn't specify a niche.
    """

    async def suggest(self, user_goal: str, about_user: str) -> list[NicheSuggestion]:
        """Returns 5 niche suggestions with reasoning."""
        logger.info("NicheSuggester: Generating niche suggestions...")

        prompt = NICHE_SUGGESTER_PROMPT.format(
            user_goal=user_goal,
            about_user=about_user
        )

        raw = await _llm_call(prompt, temperature=0.7)

        try:
            data = _parse_json_response(raw)
            suggestions = [NicheSuggestion(**item) for item in data]
            logger.info(f"NicheSuggester: Generated {len(suggestions)} suggestions")
            return suggestions
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"NicheSuggester: Failed to parse response | error={e}")
            logger.debug(f"Raw response: {raw}")
            raise


class NicheResearchAgent:
    """
    Core Research Agent.
    Input  : niche + location + campaign_id
    Output : NicheResearch (pain points) + list[Business]

    Flow:
    1. Check DB cache for niche research
    2. If not cached → research niche pain points
    3. Generate 5 search queries via LLM
    4. Run all queries via search provider (parallel)
    5. Deduplicate + extract businesses via LLM
    6. Save everything to DB
    """

    async def run(self, input: ResearchAgentInput) -> ResearchAgentOutput:
        """Main entry point."""
        logger.info(
            f"NicheResearchAgent.run() | "
            f"niche={input.niche} | location={input.location} | "
            f"campaign_id={input.campaign_id}"
        )

        async with get_async_session() as session:
            # Step 1: Get or create niche research (cached)
            niche_research = await self._get_or_create_niche_research(
                session, input.niche
            )

            # Step 2: Generate search queries
            search_queries = await self._generate_search_queries(
                input.niche, input.location
            )
            logger.info(f"Generated {len(search_queries)} search queries")

            # Step 3: Run all queries in parallel
            all_results = await self._run_searches_parallel(search_queries)
            logger.info(f"Total raw search results: {len(all_results)}")

            # Step 4: Extract businesses via LLM
            businesses = await self._extract_businesses(
                all_results, input.niche, input.location,
                input.campaign_id, input.target_count
            )
            logger.info(f"Extracted {len(businesses)} unique businesses")

            # Step 5: Save businesses to DB
            await self._save_businesses(session, businesses)
            await session.commit()

        return ResearchAgentOutput(
            niche_research=niche_research,
            businesses=businesses,
            search_queries_used=search_queries,
            total_found=len(businesses)
        )

    async def _get_or_create_niche_research(
        self, session: AsyncSession, niche: str
    ) -> NicheResearch:
        """Check DB cache. If exists → return. If not → research + save."""

        # Check cache
        result = await session.execute(
            select(NicheResearchModel).where(NicheResearchModel.niche == niche)
        )
        cached = result.scalar_one_or_none()

        if cached:
            logger.info(f"Niche research cache HIT for: {niche}")
            return NicheResearch(
                id=str(cached.id),
                niche=cached.niche,
                pain_points=cached.pain_points or [],
                software_gaps=cached.software_gaps or [],
                decision_maker_role=cached.decision_maker_role,
                raw_research=cached.raw_research,
                created_at=cached.created_at,
            )

        logger.info(f"Niche research cache MISS for: {niche} — researching...")

        # Research this niche
        niche_data = await self._research_niche_pain_points(niche)

        # Save to DB
        db_record = NicheResearchModel(
            niche=niche_data.niche,
            pain_points=niche_data.pain_points,
            software_gaps=niche_data.software_gaps,
            decision_maker_role=niche_data.decision_maker_role,
            raw_research=niche_data.raw_research,
        )
        session.add(db_record)
        await session.flush()  # Get the ID

        logger.info(f"Niche research saved to DB for: {niche}")
        return niche_data

    async def _research_niche_pain_points(self, niche: str) -> NicheResearch:
        """Search web for niche info → LLM extracts pain points."""

        # Search for niche pain points
        queries = [
            f"{niche} software problems challenges India 2024",
            f"{niche} technology gaps digital transformation India",
            f"what software do {niche} use India problems",
        ]

        all_content = []
        for query in queries:
            results = await web_search(query, num_results=5)
            for r in results:
                all_content.append(f"Title: {r.title}\nSnippet: {r.snippet}\nURL: {r.url}")

        research_content = "\n\n---\n\n".join(all_content)

        # LLM analysis
        prompt = PAIN_POINT_ANALYZER_PROMPT.format(
            niche=niche,
            research_content=research_content[:4000]  # Limit tokens
        )

        raw = await _llm_call(prompt)
        data = _parse_json_response(raw)

        return NicheResearch(
            niche=niche,
            pain_points=data.get("pain_points", []),
            software_gaps=data.get("software_gaps", []),
            decision_maker_role=data.get("decision_maker_role"),
            raw_research=data.get("raw_research", ""),
        )

    async def _generate_search_queries(self, niche: str, location: str) -> list[str]:
        """LLM generates 5 targeted search queries for this niche + location."""

        prompt = SEARCH_QUERY_GENERATOR_PROMPT.format(
            niche=niche,
            location=location
        )

        raw = await _llm_call(prompt)
        queries = _parse_json_response(raw)

        if not isinstance(queries, list):
            raise ValueError(f"Expected list of queries, got: {type(queries)}")

        return queries[:5]  # Max 5 queries

    async def _run_searches_parallel(
        self, queries: list[str]
    ) -> list[SearchResult]:
        """Run all search queries in parallel. Deduplicate by URL."""

        tasks = [web_search(q, num_results=10) for q in queries]
        results_nested = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten + deduplicate by URL
        seen_urls = set()
        unique_results = []

        for batch in results_nested:
            if isinstance(batch, Exception):
                logger.warning(f"Search query failed: {batch}")
                continue
            for result in batch:
                if result.url not in seen_urls and result.url:
                    seen_urls.add(result.url)
                    unique_results.append(result)

        return unique_results

    async def _extract_businesses(
        self,
        search_results: list[SearchResult],
        niche: str,
        location: str,
        campaign_id: str,
        target_count: int
    ) -> list[Business]:
        """LLM extracts structured business info from raw search results."""

        # Format results for LLM
        formatted = []
        for r in search_results[:30]:  # Limit to avoid token overflow
            formatted.append(
                f"Title: {r.title}\nURL: {r.url}\nSnippet: {r.snippet}\nSource: {r.source}"
            )
        results_text = "\n\n---\n\n".join(formatted)

        prompt = BUSINESS_EXTRACTOR_PROMPT.format(
            niche=niche,
            location=location,
            search_results=results_text
        )

        raw = await _llm_call(prompt, temperature=0.1)
        data = _parse_json_response(raw)

        if not isinstance(data, list):
            logger.warning("Business extractor returned non-list — returning empty")
            return []

        businesses = []
        seen_names = set()

        for item in data[:target_count]:
            name = item.get("name", "").strip()
            if not name or name.lower() in seen_names:
                continue
            seen_names.add(name.lower())

            businesses.append(Business(
                campaign_id=campaign_id,
                niche=niche,
                name=name,
                website=item.get("website"),
                location=item.get("location"),
                city=item.get("city"),
                description=item.get("description"),
                source_url=item.get("source_url"),
            ))

        return businesses

    async def _save_businesses(
        self, session: AsyncSession, businesses: list[Business]
    ) -> None:
        """Save list of Business objects to DB."""
        for biz in businesses:
            db_record = BusinessModel(
                id=biz.id,
                campaign_id=biz.campaign_id,
                niche=biz.niche,
                name=biz.name,
                website=biz.website,
                location=biz.location,
                city=biz.city,
                description=biz.description,
                pain_points=biz.pain_points,
                source_url=biz.source_url,
            )
            session.add(db_record)

    async def as_langgraph_node(self, state: dict) -> dict:
        """LangGraph node wrapper."""
        input_data = ResearchAgentInput(
            campaign_id=state["campaign_id"],
            niche=state["niche"],
            location=state["location"],
            target_count=state.get("target_count", 10)
        )
        output = await self.run(input_data)
        state["businesses"] = [b.model_dump() for b in output.businesses]
        state["niche_research"] = output.niche_research.model_dump()
        state["current_step"] = "research_complete"
        return state