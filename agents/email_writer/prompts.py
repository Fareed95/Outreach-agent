"""
agents/email_writer/prompts.py
-------------------------------
Prompt templates for the Email Writer Agent.
"""

# System prompt for the email writer LLM
EMAIL_WRITER_SYSTEM_PROMPT = """You are an expert cold email copywriter for a software agency powered by Syntrase.
You write hyper-personalized, concise, and effective cold emails that get replies.
Each email must be tailored to the specific business and contact.
Keep emails under 150 words. Focus on value proposition and relevance."""

# Prompt template for writing a personalized cold email
WRITE_EMAIL_PROMPT = """Write a personalized cold email from a software development agency (powered by Syntrase)
to a potential client.

Contact Details:
- Name: {contact_name}
- Job Title: {job_title}
- Company: {business_name}
- Industry: {industry}

Business Context:
- Description: {business_description}
- Location: {location}
- Identified Pain Points: {pain_points}

Agency Services:
- Custom software development
- Web and mobile app development
- AI/ML solutions
- Cloud infrastructure
- Digital transformation consulting

Write a personalized email that:
1. References something specific about their business
2. Addresses one of their likely pain points
3. Offers a relevant solution from the agency
4. Has a clear, low-friction call to action
5. Is concise (under 150 words)

Return both subject line and body."""

# Prompt template for creating email variants (A/B testing)
CREATE_VARIANT_PROMPT = """Create a variant of the following cold email.
Change the approach: {variant_approach}

Original Subject: {original_subject}
Original Body: {original_body}

Contact: {contact_name} at {business_name}

Return the new subject line and body."""