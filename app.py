import json
import os
import requests
import streamlit as st
from google import genai
from tensorlake.applications import run_local_application
from main import crawl
from dotenv import load_dotenv

load_dotenv()


# -------------------------
# PAGE CONFIG
# -------------------------

st.set_page_config(
    page_title="Article to Podcast Generator",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------
# CUSTOM CSS (Reference Image Style)
# -------------------------

st.markdown(
    """
<style>
    /* Dark theme background */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    
    /* Mode Cards styling */
    .feature-card {
        background-color: #1A1C23;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #333;
        min-height: 250px;
        margin-bottom: 20px;
    }
    
    /* Banner/Header card */
    .banner {
        background: linear-gradient(90deg, #1E1E2F 0%, #2D2D44 100%);
        padding: 30px;
        border-radius: 12px;
        border-left: 5px solid #6C5CE7;
        margin-bottom: 30px;
    }


</style>
""",
    unsafe_allow_html=True,
)

# -------------------------
# SIDEBAR
# -------------------------

with st.sidebar:
    st.image(
        "https://mintcdn.com/tensorlake-35e9e726/fVE8-oNRlpqs-U2A/logo/TL-Dark.svg?fit=max&auto=format&n=fVE8-oNRlpqs-U2A&q=85&s=33578bd4a1a4952a009f923081d6056e",
        width=250,
    )

    st.subheader("🔑 API Configuration")

    # Store keys in session state for persistence
    if "gemini_api_key" not in st.session_state:
        st.session_state.gemini_api_key = os.getenv("GEMINI_API_KEY") or ""
    if "elevenlabs_api_key" not in st.session_state:
        st.session_state.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY") or ""

    gemini_key = st.text_input(
        "Gemini API Key",
        value=st.session_state.gemini_api_key,
        type="password",
        help="Paste your Google Gemini API key",
    )

    eleven_key = st.text_input(
        "ElevenLabs API Key",
        value=st.session_state.elevenlabs_api_key,
        type="password",
        help="Paste your ElevenLabs API key",
    )

    if st.button("💾 Save API Keys"):
        st.session_state.gemini_api_key = gemini_key
        st.session_state.elevenlabs_api_key = eleven_key
        st.success("API Keys Saved!")

    # Slider for depth instead of number input
    max_depth = st.slider("Crawl Depth", min_value=0, max_value=3, value=1, step=1)

    st.markdown("---")
    # Key Capabilities (Bullet points from image)
    st.subheader("🎯 Key Capabilities")
    st.markdown(
        """
    - **Google AI Research**: Gemini 3 Pro for logic.
    - **Extraction Analysis**: Tensorlake crawler logic.
    - **Voice Synthesis**: ElevenLabs natural voice engine.
    - **Smart Optimization**: AI-powered content refinement.
    """
    )

    st.markdown("---")
    st.markdown("Developed with ❤️ by [Arindam](https://github.com/arindam)")

# -------------------------
# MAIN HEADER
# -------------------------

# Create title with embedded images using live links
title_html = """
<div style="display: flex; width: 100%; align-items: center;">
    <h1 style="margin: 0; padding: 0; font-size: 2.5rem; font-weight: bold;">
        <span style="font-size:2.5rem;">🎙️</span> Article to Podcast with 
        <img src="https://registry.npmmirror.com/@lobehub/icons-static-png/latest/files/dark/gemini-color.png" style="height: 50px; vertical-align: middle; margin: 0 5px;"/>
        <span style="font-size:3rem">Gemini</span> & 
        <img src="https://registry.npmmirror.com/@lobehub/icons-static-png/1.75.0/files/dark/elevenlabs-text.png" style="height: 40px; vertical-align: middle; margin: 0 5px;"/>
    </h1>
</div>
"""
st.markdown(title_html, unsafe_allow_html=True)
st.markdown(
    """
        <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%); padding: 25px; border-radius: 15px; color: white; margin: 20px 0; border: 1px solid rgba(255, 255, 255, 0.1);">
            <h3 style="color: #ffffff; margin-top: 0;">✨ Transform Your Articles into Podcasts</h3>
            <p style="font-size: 16px; margin-bottom: 0; color: #e0e0e0;"> Generate professional podcast audio from your articles.
                Get comprehensive article summarization, podcast script generation, and natural voice synthesis.
            </p>
        </div>
        """,
    unsafe_allow_html=True,
)

# -------------------------
# MODE SELECTION CARDS
# -------------------------

col_left, col_right = st.columns(2)

with col_left:
    st.markdown(
        """
    <div class="feature-card">
        <h3>🔍 Extraction Mode</h3>
        <p style='color: #8B949E;'>Smart crawling and content cleaning.</p>
        <ul style='color: #C9D1D9;'>
            <li><b>Deep Crawl</b>: Extract text from any website URL.</li>
            <li><b>Tensorlake Logic</b>: Handles JS-heavy content.</li>
            <li><b>Clean Extraction</b>: Removes ads and clutter.</li>
            <li><b>Metadata Parsing</b>: Captures titles and context.</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col_right:
    st.markdown(
        """
    <div class="feature-card">
        <h3>🎙️ Generation Mode</h3>
        <p style='color: #8B949E;'>AI Scripting and Voice Synthesis.</p>
        <ul style='color: #C9D1D9;'>
            <li><b>Gemini Summarization</b>: Professional podcast scripts.</li>
            <li><b>Natural Voices</b>: ElevenLabs high-quality synthesis.</li>
            <li><b>Stability Control</b>: AI voice parameter tuning.</li>
            <li><b>Instant Audio</b>: Direct MP3 download ready.</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------
# INPUT SECTION
# -------------------------

article_url = st.text_input(
    "Enter the article URL:", placeholder="https://www.tensorlake.ai/blog/toon-vs-json"
)


# Generate Button (Red like the reference image)
if st.button("🚀 Generate Podcast Audio"):
    # Retrieve keys from session state
    g_key = st.session_state.get("gemini_api_key")
    e_key = st.session_state.get("elevenlabs_api_key")

    if not article_url:
        st.error("❌ Please provide an article URL.")
    elif not g_key or not e_key:
        st.error("❌ Please configure your API keys in the sidebar.")
    else:
        # Modern Status Container
        with st.status("🎬 Running pipeline...", expanded=True) as status:

            # STEP 1: CRAWL
            st.write("🕷️ Running Tensorlake crawler...")
            request = run_local_application(
                crawl, {"url": article_url, "max_depth": max_depth, "max_links": 1}
            )
            crawl_result = request.output()

            # STEP 2: EXTRACT
            st.write("📄 Extracting clean text...")
            clean_text_parts = []
            pages = crawl_result.get("pages", {})
            for page in pages.values():
                text = page.get("text_content")
                if isinstance(text, str) and text.strip():
                    clean_text_parts.append(text.strip())
            clean_text = "\n\n---\n\n".join(clean_text_parts)

            # STEP 3: GEMINI
            st.write("🤖 Generating script with Gemini...")
            client = genai.Client(api_key=g_key)
            prompt = f"Create a short podcast-style summary of this article:\n\n{clean_text[:6000]}"
            response = client.models.generate_content(
                model="gemini-3-flash-preview", contents=prompt
            )
            podcast_script = response.text

            # STEP 4: ELEVENLABS
            st.write("🎤 Generating audio with ElevenLabs...")
            voice_id = "21m00Tcm4TlvDq8ikWAM"
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {"xi-api-key": e_key, "Content-Type": "application/json"}
            payload = {
                "text": podcast_script,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
            }
            audio_response = requests.post(url, json=payload, headers=headers)

            if audio_response.status_code == 200:
                audio_bytes = audio_response.content
                status.update(label="✅ Processing complete!", state="complete")

                # Output Results
                st.markdown("---")
                st.success("🎉 Processing complete! Your podcast is ready.")

                res_col1, res_col2 = st.columns([2, 1])
                with res_col1:
                    st.subheader("🎧 Podcast Audio")
                    st.audio(audio_bytes, format="audio/mp3")
                with res_col2:
                    st.subheader("📥 Actions")
                    st.download_button(
                        label="Download MP3",
                        data=audio_bytes,
                        file_name="podcast.mp3",
                        mime="audio/mpeg",
                        type="primary",
                    )

                with st.expander("📄 View Generated Script"):
                    st.write(podcast_script)
            else:
                status.update(label="❌ Generation failed", state="error")
                st.error(f"ElevenLabs error: {audio_response.text}")
