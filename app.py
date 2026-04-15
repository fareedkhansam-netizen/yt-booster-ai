import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Professional Page Setup
st.set_page_config(page_title="Gemini Video Analyst Pro", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; background-color: #FF0000; color: white; border-radius: 10px; height: 3em; font-weight: bold; border: none; }
    .stTextInput>div>div>input { background-color: #1e1e1e; color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 Gemini Video Analyst Pro")

# Sidebar
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    st.markdown("---")
    st.info("Tip: Use a video that has Captions/Subtitles enabled.")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # Fix: Using 'gemini-1.5-flash' which is the standard name
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        video_url = st.text_input("Paste YouTube Video URL here:")

        if video_url and st.button("🚀 Analyze & Boost CTR"):
            # Extract Video ID
            if "v=" in video_url:
                v_id = video_url.split("v=")[1].split("&")[0]
            elif "be/" in video_url:
                v_id = video_url.split("be/")[1].split("?")[0]
            else:
                v_id = video_url

            # Show Thumbnail Preview
            st.image(f"https://img.youtube.com/vi/{v_id}/maxresdefault.jpg", use_column_width=True)

            with st.spinner('🔄 Gemini is analyzing the video content...'):
                try:
                    # Advanced Transcript Fetching
                    transcript_list = YouTubeTranscriptApi.list_transcripts(v_id)
                    transcript_obj = transcript_list.find_transcript(['en', 'ur', 'hi'])
                    final_transcript = " ".join([t['text'] for t in transcript_obj.fetch()])
                    
                    # AI Analysis Prompt
                    prompt = f"""
                    You are a YouTube viral growth expert. Analyze this transcript:
                    {final_transcript[:8000]}
                    
                    Provide:
                    1. 📑 CONTENT SUMMARY (Short)
                    2. 🚀 5 VIRAL TITLES (High CTR)
                    3. 🎨 THUMBNAIL REDESIGN PLAN (Colors, Text, Visuals)
                    """
                    
                    response = model.generate_content(prompt)
                    st.markdown("---")
                    st.subheader("📊 Optimization Report")
                    st.markdown(response.text)
                    
                except Exception as transcript_error:
                    st.error("❌ Transcript Error: Is video par subtitles available nahi hain.")
                    st.info("Koshish karein aisi video use karein jis mein 'CC' (Captions) ka button on ho.")

    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        st.info("Check karein ke aapki API key sahi hai aur model access enabled hai.")
else:
    st.warning("👈 Please enter your Gemini API Key in the sidebar.")
