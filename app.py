import json
import requests
import streamlit as st
from google import genai
from tensorlake.applications import run_local_application

# Import crawl function from your existing crawler file
from main import crawl

# -------------------------
# BRANDING HEADER
# -------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.image(
        "https://avatars.githubusercontent.com/u/151702035?s=200&v=4",
        width=100
    )

with col2:
    st.image(
        "https://registry.npmmirror.com/@lobehub/icons-static-png/latest/files/dark/gemini-color.png",
        width=100
    )

with col3:
    st.image(
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBVNpGHzjV-JkT1ekBJqayI93p42HDiK2XSw&s",
        width=100
    )

st.markdown("---")


st.set_page_config(
    page_title="Article to Podcast Generator",
    layout="centered"
)

st.title("Article to Podcast Generator")
st.write("Convert an article into a podcast using Tensorlake, Gemini, and ElevenLabs.")

# -------------------------
# USER INPUTS
# -------------------------

article_url = st.text_input(
    "Article URL",
    placeholder="https://example.com/article"
)

gemini_api_key = st.text_input(
    "Gemini API Key",
    type="password"
)

elevenlabs_api_key = st.text_input(
    "ElevenLabs API Key",
    type="password"
)

max_depth = st.number_input(
    "Crawl Depth",
    min_value=0,
    max_value=3,
    value=1
)

# -------------------------
# MAIN ACTION
# -------------------------

if st.button("Generate Podcast"):
    if not article_url or not gemini_api_key or not elevenlabs_api_key:
        st.error("Please provide the article URL and both API keys.")
        st.stop()

    # -------------------------
    # STEP 1: CRAWL ARTICLE
    # -------------------------

    st.info("Running Tensorlake crawler...")

    request = run_local_application(
        crawl,
        {
            "url": article_url,
            "max_depth": max_depth,
            "max_links": 1
        }
    )

    crawl_result = request.output()

    with open("crawler_output.json", "w", encoding="utf-8") as f:
        json.dump(crawl_result, f, indent=2, ensure_ascii=False)

    st.success("Crawling completed.")

    # -------------------------
    # STEP 2: EXTRACT CLEAN TEXT
    # -------------------------

    st.info("Extracting clean text...")

    clean_text_parts = []
    pages = crawl_result.get("pages", {})

    for page in pages.values():
        text = page.get("text_content")
        if isinstance(text, str) and text.strip():
            clean_text_parts.append(text.strip())

    clean_text = "\n\n---\n\n".join(clean_text_parts)

    with open("clean_text.txt", "w", encoding="utf-8") as f:
        f.write(clean_text)

    st.success("Clean text extracted.")

    # -------------------------
    # STEP 3: GEMINI SUMMARY
    # -------------------------

    st.info("Generating podcast script with Gemini...")

    client = genai.Client(api_key=gemini_api_key)

    prompt = f"""
Create a short podcast-style summary of the following article.
Keep the tone clear, neutral, and easy to listen to.

Article:
{clean_text[:6000]}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    podcast_script = response.text

    with open("podcast_script.txt", "w", encoding="utf-8") as f:
        f.write(podcast_script)

    st.success("Podcast script generated.")

    st.subheader("Podcast Script")
    st.text_area("Generated Script", podcast_script, height=300)

    # -------------------------
    # STEP 4: ELEVENLABS AUDIO
    # -------------------------

    st.info("Generating audio with ElevenLabs...")

    voice_id = "21m00Tcm4TlvDq8ikWAM"

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": elevenlabs_api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "text": podcast_script,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        st.error(f"ElevenLabs error: {response.text}")
        st.stop()

    audio_bytes = response.content

    with open("podcast_audio.mp3", "wb") as f:
        f.write(audio_bytes)

    st.success("Podcast audio generated.")

    # -------------------------
    # OUTPUT
    # -------------------------

    st.subheader("Podcast Audio")

    st.audio(audio_bytes, format="audio/mp3")

    st.download_button(
        label="Download Podcast Audio",
        data=audio_bytes,
        file_name="podcast_audio.mp3",
        mime="audio/mpeg"
    )
