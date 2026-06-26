"""
utils/search_provider.py
------------------------
Pluggable search provider abstraction.
Supports: SearXNG (self-hosted, free) | Serper.dev (paid)
Switch via SEARCH_PROVIDER env var — no code change needed.
"""

import httpx
from enum import Enum
from utils.logger import logger
from utils.retry import async_retry
from config.settings import settings
from pydantic import BaseModel


class SearchProvider(str, Enum):
    SEARXNG = "searxng"
    SERPER = "serper"


class SearchResult(BaseModel):  # Use Pydantic
    title: str
    url: str
    snippet: str
    source: str = ""  # domain name


async def web_search(
    query: str,
    num_results: int = 10,
    search_type: str = "general"  # general | news | maps
) -> list[SearchResult]:
    """
    Main search function. Routes to correct provider.
    Returns standardized list of SearchResult objects.
    """
    provider = settings.SEARCH_PROVIDER
    logger.info(f"Search | provider={provider} | query={query}")

    if provider == SearchProvider.SEARXNG:
        return await _searxng_search(query, num_results, search_type)
    elif provider == SearchProvider.SERPER:
        return await _serper_search(query, num_results, search_type)
    else:
        raise ValueError(f"Unknown search provider: {provider}")


@async_retry
async def _searxng_search(query: str, num: int, search_type: str) -> list[SearchResult]:
    """SearXNG self-hosted search."""
    base_url = settings.SEARXNG_BASE_URL
    
    # Map search_type to SearXNG categories
    category_map = {
        "general": "general",
        "news": "news",
        "maps": "general"  # SearXNG doesn't have maps — fallback
    }
    
    params = {
        "q": query,
        "format": "json",
        "categories": category_map.get(search_type, "general"),
        "engines": "google,bing,duckduckgo",
        "language": "en",
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{base_url}/search", params=params)
        response.raise_for_status()
    
    data = response.json()
    results = data.get("results", [])
    
    return [
        SearchResult(
            title=r.get("title", ""),
            url=r.get("url", ""),
            snippet=r.get("content", ""),
            source=_extract_domain(r.get("url", ""))
        )
        for r in results[:num]
        if r.get("url") and r.get("title")
    ]


@async_retry
async def _serper_search(query: str, num: int, search_type: str) -> list[SearchResult]:
    """Serper.dev Google Search API."""
    endpoint_map = {
        "general": "https://google.serper.dev/search",
        "news": "https://google.serper.dev/news",
        "maps": "https://google.serper.dev/places"
    }
    url = endpoint_map.get(search_type, endpoint_map["general"])
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            headers={
                "X-API-KEY": settings.SERPER_API_KEY or "",
                "Content-Type": "application/json"
            },
            json={"q": query, "num": num, "gl": "in", "hl": "en"}
        )
        response.raise_for_status()
    
    data = response.json()
    
    # Handle different response formats
    if search_type == "maps":
        results = data.get("places", [])
        return [
            SearchResult(
                title=r.get("title", ""),
                url=r.get("website", ""),
                snippet=r.get("address", ""),
                source="google_maps"
            )
            for r in results[:num]
        ]
    else:
        results = data.get("organic", [])
        return [
            SearchResult(
                title=r.get("title", ""),
                url=r.get("link", ""),
                snippet=r.get("snippet", ""),
                source=_extract_domain(r.get("link", ""))
            )
            for r in results[:num]
        ]


def _extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc
    except Exception:
        return ""
