"""
agents/email_writer/pipeline.py
--------------------------------
LangGraph node definitions for the Email Writer Agent pipeline.
"""

from utils.logger import logger


def email_writer_node(state: dict) -> dict:
    """LangGraph node for the email writing phase.

    Args:
        state: The current OutreachState dictionary.

    Returns:
        Updated state after email generation.
    """
    # TODO: implement email writer node logic
    logger.info("email_writer_node called")
    return state