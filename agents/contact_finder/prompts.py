"""
agents/contact_finder/prompts.py
---------------------------------
Prompt templates for the Contact Finder Agent.
"""

# System prompt for the contact finder LLM
CONTACT_FINDER_SYSTEM_PROMPT = """You are a contact discovery assistant.
Your task is to find or infer email addresses and contact information
for decision-makers at target businesses."""

# Prompt template for extracting contact info from a website
EXTRACT_CONTACTS_PROMPT = """Extract contact information from the following business website content.
Business Name: {business_name}
Website: {website_url}

Website Content:
{website_content}

Return any found email addresses, names, and job titles.
Focus on decision-makers like owners, founders, directors, and managers."""

# Prompt template for generating likely email patterns
GENERATE_EMAIL_PROMPT = """Based on the business name and domain, generate the most likely email
address for the contact.

Business: {business_name}
Domain: {domain}
Contact Name: {first_name} {last_name}
Job Title: {job_title}

Consider common email patterns like:
- firstname@domain.com
- firstname.lastname@domain.com
- firstinitial.lastname@domain.com
- firstname@domain.co.in

Return the most likely email address."""