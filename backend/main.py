from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai_client import generate_email_openai, generate_ai_cta

app = FastAPI()

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- REQUEST MODEL --------------------
class EmailRequest(BaseModel):
    company_name: str
    company_url: str | None = None
    industry: str | None = None
    department: str
    custom_department: str | None = None
    subject: str | None = None


# -------------------- CLEAN LLM OUTPUT --------------------
def clean_llm_body(text: str) -> str:
    banned = [
        "subject:",
        "dear",
        "regards",
        "sincerely",
        "thank you",
        "click",
        "continue",
        "best",
    ]

    lines = text.splitlines()
    cleaned = []

    for line in lines:
        l = line.lower().strip()
        if not l:
            continue
        if any(b in l for b in banned):
            continue
        cleaned.append(line.strip())

    return " ".join(cleaned)


# -------------------- HTML WRAPPER (AI CTA) --------------------
def wrap_html(subject, body, company, department):
    action_text = generate_ai_cta(
        company=company,
        department=department,
        subject=subject,
        body=body
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{subject}</title>
</head>

<body style="font-family:Arial, sans-serif; line-height:1.6;">

<p>Hello {{target.first_name}},</p>

<p>{body}</p>

<p style="margin:22px 0;">
<a href="{{click_url}}" style="
background:#007bff;
color:#ffffff;
padding:10px 20px;
text-decoration:none;
border-radius:5px;
font-weight:600;
display:inline-block;">
{action_text}
</a>
</p>

<p style="font-size:12px;color:#666;">
If you believe this message was sent in error,
<a href="{{report_url}}" style="color:#007bff;">report this message</a>.
</p>

<p>
Regards,<br>
{department} Team<br>
{company}
</p>

<img src="{{pixel_url}}" width="1" height="1" style="display:none;">
</body>
</html>"""


# -------------------- API ENDPOINT --------------------
@app.post("/generate-email")
def generate_email(req: EmailRequest):

    department = (
        req.custom_department
        if req.department == "Other" and req.custom_department
        else req.department
    )

    subject = req.subject or "Important Update"

    raw_body = generate_email_openai(
        company=req.company_name,
        department=department,
        subject=subject,
        industry=req.industry
    )

    body = clean_llm_body(raw_body)

    html = wrap_html(
        subject=subject,
        body=body,
        company=req.company_name,
        department=department
    )

    return {"html": html}
