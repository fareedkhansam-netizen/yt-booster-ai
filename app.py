import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Page Styling for a Professional Look
st.set_page_config(page_title="Gemini Video Analyst Pro", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; background-color: #FF0000; color: white; border-radius: 10px; height: 3em; font-weight: bold; }
    .stTextInput>div>div>input { background-color: #1e1e1e; color: white; border-radius: 10px; }
    .reportview-container .main .subtitle { color: #aaaaaa; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 Gemini Video Analyst Pro")
st.markdown("### YouTube Content & CTR Optimization Tool")

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/ef/Youtube_logo.png", width=100)
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    st.info("Tip: Use a video with CC enabled for best results.")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Main Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        video_url = st.text_input("Paste YouTube Video URL here:")
    with col2:
        ctr_target = st.select_slider("Target CTR Increase:", options=["5%", "10%", "15%", "20%+"])

    if video_url and st.button("🚀 Analyze & Boost CTR"):
        try:
            # Better Video ID Extraction
            if "v=" in video_url:
                v_id = video_url.split("v=")[1].split("&")[0]
            elif "be/" in video_url:
                v_id = video_url.split("be/")[1].split("?")[0]
            else:
                v_id = video_url

            # High-Res Thumbnail Preview
            st.image(f"https://img.youtube.com/vi/{v_id}/maxresdefault.jpg", caption="Current Thumbnail Preview", use_column_width=True)

            with st.spinner('🔄 Gemini is deep-scanning the video...'):
                # ADVANCED TRANSCRIPT FETCHING
                try:
                    # Sab se pehle manual ya auto-generated transcript ki list nikalna
                    transcript_list = YouTubeTranscriptApi.list_transcripts(v_id)
                    # Har tarah ki language check karna (English, Urdu, Hindi, etc.)
                    transcript_obj = transcript_list.find_transcript(['en', 'ur', 'hi', 'pa'])
                    final_transcript = " ".join([t['text'] for t in transcript_obj.fetch()])
                except:
                    # Agar transcript na mile to error message ko handle karna
                    final_transcript = "No Transcript Available. Analyzing based on Metadata."

                # AI PROMPT (Professional Format)
                prompt = f"""
                You are a world-class YouTube Strategist (like MrBeast's team). 
                Analyze this video content: {final_transcript[:10000]}
                
                Provide the output in a BEAUTIFUL, professional format with emojis:
                
                1. 📑 CONTENT SUMMARY: 3 sentences about what the video is about.
                2. 🎯 KEY MOMENTS: 3 points that keep the viewer watching.
                3. 🚀 VIRAL TITLES (CTR 10%+): 5 explosive titles using curiosity gaps, extreme benefits, or fear of missing out.
                4. 🎨 THUMBNAIL MASTERPLAN: 
                   - Background: What colors/environment?
                   - Subject: What facial expression or object close-up?
                   - Text: What 2-3 words should be on it?
                   - Hook: What visual element makes them click?
                """
                
                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.subheader("📊 Optimization Report")
                st.success("Analysis Complete!")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"❌ Could not process this video. Reason: {str(e)}")
            st.warning("Hint: Some videos (like Shorts or music) block transcript access. Try a standard long-form video.")
else:
    st.warning("👈 Please enter your Gemini API Key in the sidebar to unlock the tool.")
