from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def run_merge_agent(observations):

    prompt = f"""
You are responsible for merging inspection observations and thermal observations.

Tasks:
- Remove duplicate issues
- Combine related issues
- Keep evidence from both sources
- If two findings conflict, clearly mention the conflict

Return clean JSON.

Observations:
{observations}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content