import requests
import os
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID ="21m00Tcm4TlvDq8ikWAM"
OUTPUT_FILE ="podcast_audio.mp3"

with open("podcast_script.txt","r", encoding="utf-8")as f:
    text = f.read()

url =f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

headers = {
"xi-api-key": ELEVENLABS_API_KEY,
"Content-Type":"application/json"
}

payload = {
"text": text,
"model_id":"eleven_v3",
"voice_settings": {
"stability":0.5,
"similarity_boost":0.5
    }
}

print("Generating audio using ElevenLabs...")

response = requests.post(url, json=payload, headers=headers)

if response.status_code !=200:
    print("Error:", response.status_code, response.text)
    exit(1)

with open(OUTPUT_FILE,"wb")as f:
    f.write(response.content)

print(f"Podcast audio saved to {OUTPUT_FILE}")