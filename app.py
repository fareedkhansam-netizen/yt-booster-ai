import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Page Styling
st.set_page_config(page_title="Gemini Video Analyst Pro", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; background-color: #FF0000; color: white; border-radius: 10px; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 Gemini Video Analyst Pro")

# Sidebar
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    # --- MODEL NAME FIXED HERE ---
    # Hum 'gemini-1.5-flash-latest' use kar rahe hain jo sab se updated hai
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
    except:
        model = genai.GenerativeModel('gemini-pro')

    video_url = st.text_input("Paste YouTube Video URL here:")

    if video_url and st.button("🚀 Analyze & Boost CTR"):
        try:
            if "v=" in video_url:
                v_id = video_url.split("v=")[1].split("&")[0]
            elif "be/" in video_url:
                v_id = video_url.split("be/")[1].split("?")[0]
            else:
                v_id = video_url

            st.image(f"https://img.youtube.com/vi/{v_id}/maxresdefault.jpg", use_column_width=True)

            with st.spinner('🔄 Analysis in progress...'):
                # Transcript Logic
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(v_id)
                    transcript_obj = transcript_list.find_transcript(['en', 'ur', 'hi'])
                    final_transcript = " ".join([t['text'] for t in transcript_obj.fetch()])
                except:
                    final_transcript = "Transcript not available, please analyze based on topic."

                prompt = f"Analyze this YouTube video transcript and provide 5 viral titles and a thumbnail strategy: {final_transcript[:8000]}"
                
                response = model.generate_content(prompt)
                st.markdown("---")
                st.subheader("📊 Optimization Report")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
else:
    st.warning("👈 Please enter your Gemini API Key in the sidebar.")
