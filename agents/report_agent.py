from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def run_report_agent(analysis, images):

    prompt = f"""
Generate a Detailed Diagnostic Report (DDR).

Structure:

1 Property Issue Summary
2 Area-wise Observations
3 Probable Root Cause
4 Severity Assessment
5 Recommended Actions
6 Additional Notes
7 Missing or Unclear Information

Use simple client friendly language.

Available Images:
{images}

Analysis Data:
{analysis}

Rules:
- Place images under relevant observations
- If image missing write "Image Not Available"
- Do not invent information
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content