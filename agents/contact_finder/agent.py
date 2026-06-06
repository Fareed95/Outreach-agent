"""
agents/contact_finder/agent.py
-------------------------------
Contact Finder Agent: Takes list of businesses.
Searches for email contacts via website scraping, search, or email discovery APIs.
Returns list[Contact].
"""

from openai import AsyncOpenAI
from config.settings import settings
from utils.logger import logger
from utils.retry import async_retry
from .schema import Contact


client = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url=settings.OPENROUTER_BASE_URL,
)


class ContactFinderAgent:
    """
    Contact Finder Agent
    Input  : list[Business]
    Output : list[Contact]
    """

    def __init__(self) -> None:
        """Initialize the Contact Finder Agent with OpenRouter client."""
        self.model = settings.OPENROUTER_MODEL

    @async_retry
    async def run(self, businesses: list[dict]) -> list[Contact]:
        """Main entry point. Finds email contacts for a list of businesses.

        Args:
            businesses: List of business dictionaries with at minimum 'id', 'name', 'website'.

        Returns:
            List of Contact objects found.
        """
        # TODO: implement website scraping + email discovery
        logger.info(f"ContactFinderAgent.run() called | businesses={len(businesses)}")
        return []

    async def as_langgraph_node(self, state: dict) -> dict:
        """LangGraph node wrapper. Reads from state, writes back to state.

        Args:
            state: The current OutreachState dictionary.

        Returns:
            Updated state with contacts populated.
        """
        # TODO: implement state-based execution
        return state