"""
agents/research/prompts.py
--------------------------
All LLM prompts for the Research Agent.
Covers: niche suggestion, search query generation,
        business extraction, pain point analysis.
"""


NICHE_SUGGESTER_PROMPT = """
You are a business development expert helping identify the best target niches for outreach.

USER'S GOAL:
{user_goal}

ABOUT THE USER / THEIR SERVICE:
{about_user}

Based on this information, suggest exactly 5 niches that would be perfect targets for outreach.
Each niche should:
- Have clear software/technology needs that match the user's service
- Be reachable via cold email
- Have decision makers who respond to outreach
- Be common in Indian cities (Mumbai, Delhi, Bangalore, etc.)

Return ONLY a valid JSON array. No explanation, no markdown, no preamble:

[
  {{
    "niche": "CA firms",
    "reasoning": "CA firms in India struggle with manual GST filing and client document management",
    "potential_pain_points": ["manual GST filing", "no client portal", "manual billing"],
    "estimated_market_size": "50,000+ CA firms across India"
  }},
  ...4 more niches
]
"""


SEARCH_QUERY_GENERATOR_PROMPT = """
You are an expert at crafting Google search queries to find business contact information.

TARGET NICHE: {niche}
TARGET LOCATION: {location}

Generate exactly 5 different Google search queries to find businesses in this niche.
Each query should approach from a different angle to maximize coverage:
- Query 1: Direct business listing search
- Query 2: Directory/listing site search (JustDial, IndiaMart)
- Query 3: Location + niche variation
- Query 4: Contact/email focused search
- Query 5: Professional association or industry search

Return ONLY a valid JSON array of strings. No explanation, no markdown:

[
  "CA firms Mumbai contact email",
  "chartered accountant Mumbai site:justdial.com",
  "top CA offices Mumbai India list",
  "CA firm Mumbai email address website",
  "ICAI registered CA firms Mumbai"
]
"""


BUSINESS_EXTRACTOR_PROMPT = """
You are extracting business information from search results.

NICHE: {niche}
LOCATION: {location}

SEARCH RESULTS:
{search_results}

Extract all unique businesses from these results. For each business:
- name: Official business name
- website: Website URL (if available)
- location: City/area
- description: What the business does (1-2 sentences)
- source_url: Where you found this info

Filter out:
- Non-businesses (directories, articles, government sites)
- Duplicate businesses
- Businesses clearly outside the target location

Return ONLY valid JSON array. No explanation, no markdown:

[
  {{
    "name": "Sharma & Associates CA Firm",
    "website": "https://sharmaassociates.com",
    "location": "Andheri, Mumbai",
    "city": "Mumbai",
    "description": "CA firm specializing in GST filing, tax consulting and audit services for SMBs",
    "source_url": "https://justdial.com/..."
  }}
]

If no valid businesses found, return empty array: []
"""


PAIN_POINT_ANALYZER_PROMPT = """
You are a business analyst specializing in identifying software and technology pain points.

NICHE: {niche}

RESEARCH DATA FROM WEB:
{research_content}

Based on this research, identify the top pain points businesses in this niche face that 
could be solved with custom software, automation, or AI tools.

Return ONLY valid JSON. No explanation, no markdown:

{{
  "pain_points": [
    "Manual GST filing takes 2-3 days every month",
    "No centralized client document management system",
    "Manual billing and invoice tracking",
    "No client communication portal",
    "Difficulty tracking deadlines across multiple clients"
  ],
  "software_gaps": [
    "No affordable GST automation software",
    "Expensive enterprise tools not suitable for small CA firms",
    "No India-specific client portal solutions"
  ],
  "decision_maker_role": "Managing Partner or Owner",
  "raw_research": "Summary of key findings from the research..."
}}
"""