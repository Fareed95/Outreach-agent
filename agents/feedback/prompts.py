"""
agents/feedback/prompts.py
---------------------------
Prompt templates for the Feedback Agent.
"""

# System prompt for the feedback LLM
FEEDBACK_SYSTEM_PROMPT = """You are a campaign analytics expert.
Your task is to analyze cold email campaign performance data
and generate actionable insights to improve future outreach."""

# Prompt template for analyzing campaign performance
ANALYZE_CAMPAIGN_PROMPT = """Analyze the following cold email campaign results and provide insights.

Campaign Details:
- Name: {campaign_name}
- Niche: {niche}
- Target Location: {location}

Performance Metrics:
- Total Sent: {total_sent}
- Total Opened: {total_opened}
- Total Replied: {total_replied}
- Total Bounced: {total_bounced}
- Open Rate: {open_rate}%
- Reply Rate: {reply_rate}%

Provide:
1. Key observations about the campaign performance
2. Specific recommendations to improve open rates
3. Specific recommendations to improve reply rates
4. Suggested email subject line improvements
5. Suggested targeting improvements for next batch"""

# Prompt template for generating optimization recommendations
GENERATE_OPTIMIZATIONS_PROMPT = """Based on the following email performance data, generate optimization recommendations
for the next outreach batch.

Best Performing Subject Lines: {best_subjects}
Worst Performing Subject Lines: {worst_subjects}
Best Performing Email Variant: {best_variant}
Reply Patterns: {reply_patterns}

Generate 3 concrete optimization recommendations for the next batch."""