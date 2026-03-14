from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def run_extraction_agent(text):

    prompt = f"""
You are a building inspection analyst.

Extract structured observations from the report text.

Return JSON format:

[
  {{
    "area": "",
    "issue": "",
    "temperature": "",
    "evidence": ""
  }}
]

Rules:
- Do not invent information
- If temperature not available write "Not Available"
- Keep the issue description short
- Only extract relevant issues

Report Text:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content