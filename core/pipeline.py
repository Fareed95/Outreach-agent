"""
core/pipeline.py
-----------------
Master LangGraph pipeline.
Connects: research → contact_finder → email_writer → sender → feedback
"""

from langgraph.graph import StateGraph, END
from core.state import OutreachState
from agents.research.agent import ResearchAgent
from agents.contact_finder.agent import ContactFinderAgent
from agents.email_writer.agent import EmailWriterAgent
from agents.feedback.agent import FeedbackAgent


def build_pipeline() -> StateGraph:
    """Build and compile the full outreach pipeline.

    Returns:
        A compiled LangGraph StateGraph ready for execution.
    """
    graph = StateGraph(OutreachState)

    # Register nodes (TODO: wire actual agent logic)
    graph.add_node("research", ResearchAgent().as_langgraph_node)
    graph.add_node("contact_finder", ContactFinderAgent().as_langgraph_node)
    graph.add_node("email_writer", EmailWriterAgent().as_langgraph_node)
    graph.add_node("feedback", FeedbackAgent().as_langgraph_node)

    # Define flow
    graph.set_entry_point("research")
    graph.add_edge("research", "contact_finder")
    graph.add_edge("contact_finder", "email_writer")
    graph.add_edge("email_writer", "feedback")
    graph.add_edge("feedback", END)

    return graph.compile()


pipeline = build_pipeline()