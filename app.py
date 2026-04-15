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

    if video_url and st.button("Analyze & Redesign"):
        try:
            # Video ID extraction
            if "v=" in video_url:
                v_id = video_url.split("v=")[1].split("&")[0]
            elif "be/" in video_url:
                v_id = video_url.split("be/")[1].split("?")[0]
            else:
                v_id = video_url

            with st.spinner('AI data nikal raha hai...'):
                # Is tareeqay se error nahi ayega
                transcript_list = YouTubeTranscriptApi.list_transcripts(v_id)
                transcript_obj = transcript_list.find_transcript(['en', 'hi', 'ur'])
                final_transcript = " ".join([t['text'] for t in transcript_obj.fetch()])

                prompt = f"Analyze this YouTube transcript and suggest 5 viral titles and a thumbnail strategy: {final_transcript[:7000]}"
                
                response = model.generate_content(prompt)
                st.subheader("✅ Suggestions:")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Tip: Agar transcript ka error hai, to aisi video try karein jis mein subtitles hon.")
else:
    st.warning("Sidebar mein API key dalein.")
