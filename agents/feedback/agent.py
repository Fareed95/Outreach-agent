"""
agents/feedback/agent.py
-------------------------
Feedback Agent: Analyzes campaign results.
Generates insights and recommendations for optimizing the next outreach batch.
Returns Campaign with updated metrics and insights.
"""

from openai import AsyncOpenAI
from config.settings import settings
from utils.logger import logger
from utils.retry import async_retry
from .schema import Campaign


client = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url=settings.OPENROUTER_BASE_URL,
)


class FeedbackAgent:
    """
    Feedback Agent
    Input  : campaign data, email results
    Output : Campaign with insights
    """

    def __init__(self) -> None:
        """Initialize the Feedback Agent with OpenRouter client."""
        self.model = settings.OPENROUTER_MODEL

    @async_retry
    async def run(self, campaign: Campaign, email_results: list[dict]) -> Campaign:
        """Main entry point. Analyzes campaign results and generates insights.

        Args:
            campaign: The campaign to analyze.
            email_results: List of email tracking results.

        Returns:
            Updated Campaign with calculated metrics and AI-generated insights.
        """
        # TODO: implement analytics + LLM-based insight generation
        logger.info(f"FeedbackAgent.run() called | campaign_id={campaign.id} | emails={len(email_results)}")
        return campaign

    async def as_langgraph_node(self, state: dict) -> dict:
        """LangGraph node wrapper. Reads from state, writes back to state.

        Args:
            state: The current OutreachState dictionary.

        Returns:
            Updated state with feedback results populated.
        """
        # TODO: implement state-based execution
        return state