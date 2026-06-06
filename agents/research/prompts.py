"""
agents/research/prompts.py
---------------------------
Prompt templates for the Research Agent.
"""

# System prompt for the research LLM
RESEARCH_SYSTEM_PROMPT = """You are a business research assistant.
Given a niche and location, your task is to extract structured business information
from search results and identify potential pain points each business might have."""

# Prompt template for extracting business info from search results
EXTRACT_BUSINESSES_PROMPT = """Extract business information from the following search results.
Focus on the niche: {niche}
Location: {location}

Search Results:
{search_results}

Return a structured list of businesses with name, website, description, and potential pain points."""

# Prompt template for inferring pain points
INFER_PAIN_POINTS_PROMPT = """Based on the business description and industry, infer likely pain points
that {business_name} might be facing. Consider common challenges in the {industry} industry.

Business Description: {description}

Return a list of 3-5 specific pain points this business likely faces."""