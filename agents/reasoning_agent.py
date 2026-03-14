from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def run_reasoning_agent(merged_data):

    prompt = f"""
You are a structural diagnostics expert.

Based on the merged observations:

For each issue determine:

- Probable Root Cause
- Severity Level (Low / Medium / High / Critical)
- Reason for severity

Rules:
- Only use information from the observations
- If root cause unclear write "Not Available"

Merged Observations:
{merged_data}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content