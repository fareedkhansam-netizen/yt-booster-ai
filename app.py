import streamlit as st
import google.generativeai as genai
import youtube_transcript_api

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
            # Video ID Extract logic
            if "v=" in video_url:
                video_id = video_url.split("v=")[1].split("&")[0]
            elif "be/" in video_url:
                video_id = video_url.split("be/")[1].split("?")[0]
            else:
                video_id = video_url

            with st.spinner('AI analysis kar raha hai...'):
                # Sahi tareeqa function call karne ka
                transcript_data = youtube_transcript_api.YouTubeTranscriptApi.get_transcript(video_id)
                transcript = " ".join([i['text'] for i in transcript_data])

                prompt = f"""
                You are a YouTube viral growth expert. 
                Transcript: {transcript[:7000]}
                Current Title: {current_title}
                Current CTR: {ctr_level}
                
                Please provide:
                1. A brief summary of the video.
                2. 5 high-CTR, viral-style titles.
                3. A detailed thumbnail redesign plan (focusing on visual hooks and high-contrast elements).
                """
                
                response = model.generate_content(prompt)
                st.subheader("✅ Analysis Results:")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"Error Message: {str(e)}")
            st.info("Check karein ke video public hai aur uske captions (Subtitles) ON hain.")
else:
    st.warning("Pehle Sidebar mein Gemini API Key enter karein.")
