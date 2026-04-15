import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi as yta

st.set_page_config(page_title="Gemini Video Booster", page_icon="📈")
st.title("🚀 YouTube Video & CTR Booster")

api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    video_url = st.text_input("YouTube Video Link Paste Karein:")
    current_title = st.text_input("Current Title (Optional):")
    ctr_level = st.selectbox("Current CTR Level:", ("Low", "Medium", "High"))

    if video_url and st.button("Analyze & Redesign"):
        try:
            # Video ID nikalne ka sahi tareeqa
            if "v=" in video_url:
                video_id = video_url.split("v=")[1].split("&")[0]
            elif "be/" in video_url:
                video_id = video_url.split("be/")[1]
            else:
                video_id = video_url

            with st.spinner('AI analysis kar raha hai...'):
                # Error Fix: Direct class method call
                data = yta.get_transcript(video_id)
                transcript = " ".join([i['text'] for i in data])

                prompt = f"""
                App aik viral video expert hain. Is video ka transcript parhein: {transcript[:7000]}
                Current Title: {current_title}
                Current CTR: {ctr_level}
                
                Mujhe ye batayein:
                1. Video ki Summary.
                2. 5 Viral Titles (High CTR).
                3. Thumbnail redesign ka mukammal mashwara.
                """
                
                response = model.generate_content(prompt)
                st.subheader("✅ Gemini Results:")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"Galti: {e}")
            st.info("Subtitles check karein ke video mein on hain ya nahi.")
else:
    st.warning("Sidebar mein API Key dalein.")
