"""
agents/research/agent.py
------------------------
Research Agent: Takes niche + location as input.
Uses Serper.dev to find target businesses via Google search.
Extracts business info and infers pain points using LLM.
Returns list[Business].
"""

from openai import AsyncOpenAI
from config.settings import settings
from utils.logger import logger
from utils.retry import async_retry
from .schema import Business


client = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url=settings.OPENROUTER_BASE_URL,
)


class ResearchAgent:
    """
    Research Agent
    Input  : niche (str), location (str)
    Output : list[Business]
    """

    def __init__(self) -> None:
        """Initialize the Research Agent with OpenRouter client."""
        self.model = settings.OPENROUTER_MODEL

    @async_retry
    async def run(self, niche: str, location: str) -> list[Business]:
        """Main entry point. Searches for businesses in the given niche and location.

        Args:
            niche: The industry or business niche to search for.
            location: Geographic location to target.

        Returns:
            List of Business objects discovered.
        """
        # TODO: implement Serper.dev search + LLM extraction
        logger.info(f"ResearchAgent.run() called | niche={niche} | location={location}")
        return []

    async def as_langgraph_node(self, state: dict) -> dict:
        """LangGraph node wrapper. Reads from state, writes back to state.

        Args:
            state: The current OutreachState dictionary.

        Returns:
            Updated state with businesses populated.
        """
        # TODO: implement state-based execution
        return state