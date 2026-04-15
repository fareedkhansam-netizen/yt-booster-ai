import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Page Configuration
st.set_page_config(page_title="Gemini Video Booster", page_icon="🚀")
st.title("🎥 YouTube Video & CTR Booster")

# Sidebar for API Key
api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    # Using Gemini 1.5 Flash for speed and efficiency
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    video_url = st.text_input("YouTube Video Link Paste Karein:")

    if video_url and st.button("Analyze & Redesign"):
        try:
            # Video ID extraction logic
            if "v=" in video_url:
                v_id = video_url.split("v=")[1].split("&")[0]
            elif "be/" in video_url:
                v_id = video_url.split("be/")[1].split("?")[0]
            else:
                v_id = video_url

            with st.spinner('AI data nikal raha hai aur analysis kar raha hai...'):
                # Transcript nikalna
                transcript_list = YouTubeTranscriptApi.list_transcripts(v_id)
                # Koshish karein ke English, Urdu, ya Hindi transcript mile
                transcript_obj = transcript_list.find_transcript(['en', 'ur', 'hi'])
                final_transcript = " ".join([t['text'] for t in transcript_obj.fetch()])

                # --- YE WAHI DETAILED PROMPT HAI JO MERE JAISE OUTPUT DEGA ---
                prompt = f"""
                App aik YouTube Viral Growth Expert hain. Niche diye gaye video transcript ko boht ghaur se parhein:
                
                Transcript: {final_transcript[:10000]}
                
                Ab mujhe theek is format mein analysis dein (Roman Urdu/English mix mein):

                # 🎬 Video Analysis (Based on Transcript)
                * **Summary:** Video ka aik brief summary dein (kis bare mein hai).
                * **Key Takeaways:** Video ke 3-5 sab se zaroori points list karein.
                * **Viewer Hook:** Video ke pehle 30 seconds ko analyze karein aur batayein ke viewer ko rokne ke liye ye kitna strong hai.

                # 💡 High-Converting Title Redesign
                Mujhe 5 naye titles dein jinka CTR (Click-Through Rate) 10% se zyada hone ka chance ho. Har title ke sath batayein ke wo kyun chalega (kis psychology par base karta hai).

                # 🎨 Thumbnail Redesign Plan
                Aik detailed visual roadmap dein takay thumbnail ko redesigned kiya ja sake (agar CTR low hai). Is mein batayein:
                * **Visual Composition:** Screen par kya dikhana chahiye (kis cheez ka split screen, ya close-up).
                * **Color Scheme:** Kaunse colors "Pop" karenge (contrast tricks).
                * **Text Overlay:** Thumbnail par kya text likhna chahiye aur kaise font mein.
                * **Action Elements:** Kaunse visual hooks (maslan facial expressions, arrows, motion lines) add karne hain.
                """
                
                response = model.generate_content(prompt)
                
                # Output dikhana
                st.subheader("✅ Aapka Detailed Analysis Haazir Hai:")
                st.write(response.text)
                
        except Exception as e:
            # Agar koi error aaye (jaise subtitles na hon)
            st.error(f"Galti: {str(e)}")
            st.info("Tip: Ye tool sirf aisi videos par kaam karta hai jin par Subtitles (CC) ON hon.")
else:
    st.warning("Pehle Sidebar mein apni Gemini API Key enter karein.")
