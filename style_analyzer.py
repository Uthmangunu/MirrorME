# style_analyzer.py
import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_user_style(user_messages):
    if not user_messages:
        return "neutral and default"

    text_block = "\n".join(user_messages[-10:])
    prompt = [
        {"role": "system", "content": "You are a writing style analyst."},
        {"role": "user", "content": f"Analyze the user's tone and phrasing in these messages and describe it briefly:\n\n{text_block}"}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=prompt,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "neutral and default"
