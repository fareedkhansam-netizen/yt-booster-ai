import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

st.set_page_config(page_title="Gemini Video Booster", page_icon="📈")
st.title("🚀 YouTube Video & CTR Booster")

api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    video_url = st.text_input("YouTube Video Link:")
    current_title = st.text_input("Current Title (Optional):")
    ctr_level = st.selectbox("Current CTR:", ("Low", "Medium", "High"))

    if video_url and st.button("Analyze & Redesign"):
        try:
            video_id = video_url.split("=")[-1]
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join([i['text'] for i in transcript_data])

            prompt = f"Analyze this YT transcript for a {ctr_level} CTR video. Suggest 5 viral titles and a thumbnail redesign strategy: {transcript[:5000]}"
            
            response = model.generate_content(prompt)
            st.write(response.text)
        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.warning("Please enter API Key in sidebar")