"""
agents/email_writer/agent.py
-----------------------------
Email Writer Agent: Takes contact + business info.
Uses OpenRouter LLM to write hyper-personalized cold emails.
Returns list[EmailRecord].
"""

from openai import AsyncOpenAI
from config.settings import settings
from utils.logger import logger
from utils.retry import async_retry
from .schema import EmailRecord


client = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url=settings.OPENROUTER_BASE_URL,
)


class EmailWriterAgent:
    """
    Email Writer Agent
    Input  : contact (dict), business (dict)
    Output : list[EmailRecord]
    """

    def __init__(self) -> None:
        """Initialize the Email Writer Agent with OpenRouter client."""
        self.model = settings.OPENROUTER_MODEL

    @async_retry
    async def run(self, contacts: list[dict], businesses: list[dict], campaign_id: str) -> list[EmailRecord]:
        """Main entry point. Writes personalized emails for each contact.

        Args:
            contacts: List of contact dictionaries with contact info.
            businesses: List of business dictionaries for context.
            campaign_id: The campaign ID to associate emails with.

        Returns:
            List of EmailRecord objects with generated subject and body.
        """
        # TODO: implement LLM-based email generation
        logger.info(f"EmailWriterAgent.run() called | contacts={len(contacts)} | campaign_id={campaign_id}")
        return []

    async def as_langgraph_node(self, state: dict) -> dict:
        """LangGraph node wrapper. Reads from state, writes back to state.

        Args:
            state: The current OutreachState dictionary.

        Returns:
            Updated state with emails_written populated.
        """
        # TODO: implement state-based execution
        return state