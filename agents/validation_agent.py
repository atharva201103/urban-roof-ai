from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def run_validation_agent(report):

    prompt = f"""
You are a quality control reviewer for building inspection reports.

Check the DDR report for:

1 Hallucinated facts
2 Missing information
3 Conflicting data not mentioned

Rules:

- If information missing ensure "Not Available"
- If conflict exists ensure it is clearly mentioned
- Do not add new technical claims

Return corrected report if needed.

DDR Report:
{report}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content