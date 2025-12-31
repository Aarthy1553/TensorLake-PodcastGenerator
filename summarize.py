import os
from dotenv import load_dotenv

load_dotenv()

from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

with open("clean_text.txt","r", encoding="utf-8")as f:
    article_text = f.read()

article_text = article_text[:6000]

prompt = f"""
Create a short podcast-style summary of the following article.
Keep the tone clear, neutral, and easy to listen to.

Article:
{article_text}
"""

response = client.models.generate_content(
    model="models/gemini-2.5-flash",
    contents=prompt
)

summary = response.text

with open("podcast_script.txt","w", encoding="utf-8")as f:
    f.write(summary)

print("Podcast script saved to podcast_script.txt")