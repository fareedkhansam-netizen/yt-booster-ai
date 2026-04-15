import streamlit as st
from gradio_client import Client

st.title("🤖 Custom Talking Head App")

img = st.file_uploader("Upload Image", type=['jpg','png'])
aud = st.file_uploader("Upload Audio", type=['mp3','wav'])

if st.button("Generate Video"):
    if img and aud:
        with st.spinner("Peeche se free server use ho raha hai... Thora sabar karein."):
            try:
                # Ye hai asli jugar: Hum kisi bhi free public space ka rasta use kar rahe hain
                client = Client("vinthony/SadTalker")
                result = client.predict(
                    img,	# Image file
                    aud,	# Audio file
                    api_name="/predict"
                )
                st.video(result) # Video result yahan show ho jayega
            except Exception as e:
                st.error("Server busy hai, thori der baad try karein.")
