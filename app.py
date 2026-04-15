import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# --- Professional UI Setup ---
st.set_page_config(page_title="Gemini Video Analyst Pro", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; background-color: #FF0000; color: white; border-radius: 10px; height: 3em; font-weight: bold; border: none; }
    .stTextInput>div>div>input { background-color: #1e1e1e; color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 Gemini Video Analyst Pro")
st.markdown("##### AI-Powered Content Strategy & CTR Optimization")

# Sidebar
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    st.info("Tip: Use standard YouTube links (not shorts) for best results.")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # Fix: Using standard model name to avoid 404 errors
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        video_url = st.text_input("Paste YouTube Video URL here:")

        if video_url and st.button("🚀 Analyze & Boost CTR"):
            # Extract Video ID
            v_id = ""
            if "v=" in video_url:
                v_id = video_url.split("v=")[1].split("&")[0]
            elif "be/" in video_url:
                v_id = video_url.split("be/")[1].split("?")[0]

            if v_id:
                st.image(f"https://img.youtube.com/vi/{v_id}/maxresdefault.jpg", use_column_width=True)

                with st.spinner('🔄 Gemini is analyzing the video...'):
                    try:
                        # Fetch Transcript
                        transcript_list = YouTubeTranscriptApi.list_transcripts(v_id)
                        transcript_obj = transcript_list.find_transcript(['en', 'ur', 'hi'])
                        final_transcript = " ".join([t['text'] for t in transcript_obj.fetch()])
                        
                        # Professional Analysis Prompt
                        prompt = f"""
                        You are a viral content expert. Analyze this transcript: {final_transcript[:8000]}
                        Provide a professional report in Roman Urdu/English mix with:
                        1. 📑 SUMMARY
                        2. 🚀 5 VIRAL TITLES (Target 10% CTR)
                        3. 🎨 THUMBNAIL MASTERPLAN (Colors, Visuals, Text)
                        """
                        
                        response = model.generate_content(prompt)
                        st.success("Analysis Complete!")
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"❌ Transcript Error: Is video ke captions available nahi hain.")
            else:
                st.warning("Please enter a valid YouTube URL.")

    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
else:
    st.warning("👈 Please enter your Gemini API Key in the sidebar.")
