import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------- EMAIL BODY GENERATOR --------------------
def generate_email_openai(company, department, subject, industry=None):
    prompt = f"""
You are writing a REAL internal corporate email.

Company: {company}
Department: {department}
Industry: {industry or "General"}
Scenario (Subject): {subject}

STRICT RULES:
- Sound like a real internal business email
- No awareness, no education, no warnings
- No greetings like "Dear Team"
- No sign-offs
- No button text
- One short paragraph (2–4 sentences)
- Neutral, professional, and believable
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()


# -------------------- AI CTA GENERATOR --------------------
def generate_ai_cta(company, department, subject, body):
    prompt = f"""
Generate a SHORT call-to-action button label (2–4 words).

Context:
Company: {company}
Department: {department}
Subject: {subject}
Email content: {body}

RULES:
- Do NOT use login, sign in, password, verify
- Neutral and professional
- Generic but action-oriented
- Examples: View Details, Read More, Open Message
- Return ONLY the button text
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
    )

    return response.choices[0].message.content.strip()
