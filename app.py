import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

st.set_page_config(page_title="Gemini Video Booster", page_icon="📈")
st.title("🚀 YouTube Video & CTR Booster")

# Sidebar for API Key
api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    video_url = st.text_input("YouTube Video Link Paste Karein:")
    current_title = st.text_input("Current Title (Optional):")
    ctr_level = st.selectbox("Current CTR Level:", ("Low", "Medium", "High"))

    if video_url and st.button("Analyze & Redesign"):
        try:
            # Video ID nikalne ka behtar tareeqa
            if "v=" in video_url:
                video_id = video_url.split("v=")[1].split("&")[0]
            elif "be/" in video_url:
                video_id = video_url.split("be/")[1].split("?")[0]
            else:
                video_id = video_url

            with st.spinner('AI Video ko parh raha hai...'):
                # Sahi function call: YouTubeTranscriptApi.get_transcript(video_id)
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcript = " ".join([i['text'] for i in transcript_list])

                # Gemini Analysis Prompt
                prompt = f"""
                Role: Expert YouTube Content Strategist.
                Video Context: {current_title if current_title else "YouTube Video"}
                Current CTR: {ctr_level}
                
                Transcript: {transcript[:8000]}
                
                Task:
                1. Video ki short summary dein.
                2. 5 aise Titles likhein jinka CTR 10% se zyada ho.
                3. Thumbnail redesign ka plan batayein (Colors, Text, aur Visuals).
                """
                
                response = model.generate_content(prompt)
                st.subheader("✅ Analysis & Recommendations:")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Tip: Check karein ke video ke Captions/Subtitles on hain ya nahi.")
else:
    st.warning("Please enter Gemini API Key in sidebar to start.")
