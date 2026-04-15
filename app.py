import streamlit as st
import google.generativeai as genai
import os
import time
import tempfile
from pathlib import Path

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Gemini Video Analyst Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 50%, #0a0f0a 100%);
    color: #e8e8f0;
}

section[data-testid="stSidebar"] {
    background: rgba(15,15,30,0.97) !important;
    border-right: 1px solid rgba(100,220,120,0.15);
}
section[data-testid="stSidebar"] * { color: #c8c8e0 !important; }

.hero-header {
    background: linear-gradient(90deg, rgba(100,220,120,0.08), rgba(60,180,255,0.08));
    border: 1px solid rgba(100,220,120,0.2);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 28px;
    text-align: center;
}
.hero-header h1 {
    font-size: 2.6rem; font-weight: 800;
    background: linear-gradient(90deg, #64dc78, #3cb4ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0 0 6px 0;
}
.hero-header p { color: #8888aa; font-size: 1rem; margin: 0; font-family: 'DM Mono', monospace; }

.info-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 20px 24px; margin-bottom: 16px;
}

.stButton > button {
    background: linear-gradient(90deg, #64dc78, #3cb4ff) !important;
    color: #0a0a0f !important; font-weight: 700 !important;
    font-family: 'Syne', sans-serif !important; border: none !important;
    border-radius: 8px !important; padding: 10px 28px !important; font-size: 1rem !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

.stTextArea textarea, .stTextInput input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(100,220,120,0.2) !important;
    color: #e8e8f0 !important; border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
}

.stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(100,220,120,0.2) !important;
    color: #e8e8f0 !important; border-radius: 8px !important;
}

.result-box {
    background: rgba(100,220,120,0.04);
    border: 1px solid rgba(100,220,120,0.2);
    border-radius: 12px; padding: 24px 28px; margin-top: 20px;
    font-family: 'DM Mono', monospace; font-size: 0.93rem;
    line-height: 1.75; color: #d8d8f0; white-space: pre-wrap;
}

.badge { display:inline-block; padding:3px 12px; border-radius:20px; font-size:0.78rem; font-weight:600; font-family:'DM Mono',monospace; }
.badge-green { background:rgba(100,220,120,0.15); color:#64dc78; border:1px solid rgba(100,220,120,0.3); }
.badge-blue  { background:rgba(60,180,255,0.15);  color:#3cb4ff; border:1px solid rgba(60,180,255,0.3); }
.badge-red   { background:rgba(255,80,80,0.15);   color:#ff5050; border:1px solid rgba(255,80,80,0.3); }

.yt-box {
    background: rgba(255,0,0,0.05); border: 1px solid rgba(255,80,80,0.25);
    border-radius: 12px; padding: 16px 20px; margin-bottom: 16px;
}

hr { border-color: rgba(255,255,255,0.06) !important; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
GEMINI_MODELS = {
    "gemini-2.0-flash":      "Gemini 2.0 Flash ⚡ (Fastest, multimodal)",
    "gemini-2.0-flash-lite": "Gemini 2.0 Flash-Lite 🪶 (Lightweight)",
    "gemini-1.5-pro":        "Gemini 1.5 Pro 🧠 (Best quality, 2M context)",
    "gemini-1.5-flash":      "Gemini 1.5 Flash ⚡ (Fast & versatile)",
    "gemini-1.5-flash-8b":   "Gemini 1.5 Flash-8B 🔬 (Smallest 1.5)",
}

ANALYSIS_MODES = [
    "📝 General Summary",
    "🎭 Scene-by-Scene Breakdown",
    "😊 Sentiment & Emotion Analysis",
    "🔑 Key Moments & Highlights",
    "📊 Content & Topic Analysis",
    "🗣️ Speech Transcription",
    "👁️ Visual Description & Objects",
    "🛡️ Content Safety Review",
    "🎬 Cinematic / Production Analysis",
    "✏️ Custom Prompt",
]

PROMPTS_MAP = {
    "📝 General Summary":              "Provide a comprehensive summary of this video/image. Cover the main topic, key events, people, and overall message.",
    "🎭 Scene-by-Scene Breakdown":     "Break down this video scene by scene. For each scene: timestamp range, what happens visually, what is said, and its significance.",
    "😊 Sentiment & Emotion Analysis": "Analyze the emotional tone and sentiment. Identify moments of joy, tension, sadness, excitement and what triggers them.",
    "🔑 Key Moments & Highlights":     "Identify the most important moments or highlights and explain why each is significant.",
    "📊 Content & Topic Analysis":     "Analyze the topics, themes, and subject matter. Categorize the content and provide insights into its purpose and target audience.",
    "🗣️ Speech Transcription":         "Transcribe all spoken words as accurately as possible with timestamps. Note any unclear audio.",
    "👁️ Visual Description & Objects": "Describe all visual elements in detail: people, objects, text on screen, colors, environment, and visual style.",
    "🛡️ Content Safety Review":        "Review this content for safety. Identify any sensitive or age-restricted elements and provide an overall safety rating.",
    "🎬 Cinematic / Production Analysis": "Analyze production quality: camera work, lighting, editing, sound design, graphics, pacing, and overall production value.",
}

SUPPORTED_VIDEO = ["mp4", "mov", "avi", "mkv", "webm", "flv", "3gp", "wmv"]
SUPPORTED_IMAGE = ["jpg", "jpeg", "png", "gif", "webp", "bmp"]

MIME_MAP = {
    "mp4":"video/mp4","mov":"video/quicktime","avi":"video/x-msvideo",
    "mkv":"video/x-matroska","webm":"video/webm","flv":"video/x-flv",
    "3gp":"video/3gpp","wmv":"video/x-ms-wmv",
    "jpg":"image/jpeg","jpeg":"image/jpeg","png":"image/png",
    "gif":"image/gif","webp":"image/webp","bmp":"image/bmp",
}

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
for key, default in {
    "api_configured": False,
    "chat_history": [],
    "last_result": "",
    "uploaded_name": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def configure_api(api_key: str):
    """Returns (True, '') on success or (False, error_msg)."""
    key = api_key.strip()
    if not key:
        return False, "API key is empty."
    try:
        genai.configure(api_key=key)
        # Lightweight check — list_models doesn't consume quota
        list(genai.list_models())
        return True, ""
    except Exception as e:
        msg = str(e)
        if "API_KEY_INVALID" in msg or "invalid" in msg.lower():
            return False, "Invalid API key."
        if "quota" in msg.lower():
            return False, "Quota exceeded. Try again later."
        return False, msg[:150]


def is_youtube(url: str) -> bool:
    u = url.strip().lower()
    return "youtube.com/watch" in u or "youtu.be/" in u


def analyse_youtube(model_id: str, yt_url: str, mode: str, custom: str) -> str:
    prompt = custom.strip() if mode == "✏️ Custom Prompt" else PROMPTS_MAP.get(mode, "Summarize this video.")
    model  = genai.GenerativeModel(model_id)
    # Gemini natively supports YouTube URLs via file_data part
    response = model.generate_content([
        {
            "role": "user",
            "parts": [
                {"file_data": {"mime_type": "video/mp4", "file_uri": yt_url.strip()}},
                {"text": prompt},
            ],
        }
    ])
    return response.text


def upload_and_analyse(file_bytes: bytes, mime_type: str, name: str, model_id: str, mode: str, custom: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(name).suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        bar = st.progress(0, text="📤 Uploading to Gemini…")
        gfile = genai.upload_file(path=tmp_path, mime_type=mime_type, display_name=name)
        step = 0
        while gfile.state.name == "PROCESSING":
            time.sleep(2)
            gfile = genai.get_file(gfile.name)
            step  = min(step + 10, 90)
            bar.progress(step, text=f"⏳ Processing… {step}%")
        bar.progress(100, text="✅ Ready!")
        time.sleep(0.3)
        bar.empty()
        if gfile.state.name == "FAILED":
            raise RuntimeError("Gemini processing failed.")
        prompt   = custom.strip() if mode == "✏️ Custom Prompt" else PROMPTS_MAP.get(mode, "Describe this media.")
        model_obj = genai.GenerativeModel(model_id)
        return model_obj.generate_content([gfile, prompt]).text
    finally:
        os.unlink(tmp_path)


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:12px 0 20px 0;">
        <div style="font-size:2.4rem;">🎬</div>
        <div style="font-size:1.1rem;font-weight:800;background:linear-gradient(90deg,#64dc78,#3cb4ff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            Gemini Video Analyst Pro
        </div>
        <div style="font-size:0.75rem;color:#555577;font-family:'DM Mono',monospace;margin-top:4px;">
            powered by Google Gemini AI
        </div>
    </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🔑 API Configuration")

    api_key_input = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="AIza...",
        value="AIzaSyAlGN0e_4bYuxCgXADqGbqfnxC-5vHkvMg",
    )

    if st.button("🔌 Connect API", use_container_width=True):
        with st.spinner("Connecting…"):
            ok, err = configure_api(api_key_input)
        if ok:
            st.session_state.api_configured = True
            st.success("✅ Connected!")
        else:
            st.session_state.api_configured = False
            st.error(f"❌ {err}")

    if st.session_state.api_configured:
        st.markdown('<span class="badge badge-green">● API Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-red">○ Not Connected</span>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🤖 Model Selection")
    selected_model = st.selectbox(
        "Choose Gemini Model",
        list(GEMINI_MODELS.keys()),
        format_func=lambda m: GEMINI_MODELS[m],
        index=0,
    )
    st.markdown(f'<span class="badge badge-blue">▸ {selected_model}</span>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🔍 Analysis Mode")
    analysis_mode = st.selectbox("Select Mode", ANALYSIS_MODES, index=0)

    custom_prompt_text = ""
    if analysis_mode == "✏️ Custom Prompt":
        custom_prompt_text = st.text_area("Your Custom Prompt", placeholder="Ask anything…", height=120)

    st.divider()
    st.markdown("### ⚙️ Settings")
    show_raw   = st.checkbox("Show raw response",           value=False)
    auto_clear = st.checkbox("Clear result on new upload",  value=True)

    st.divider()
    st.markdown(
        '<div style="font-size:0.72rem;color:#444466;text-align:center;font-family:\'DM Mono\',monospace;">'
        'Gemini Video Analyst Pro<br>© 2024</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1>🎬 Gemini Video Analyst Pro</h1>
    <p>YouTube Link  OR  Upload File → pick Model & Mode → instant AI analysis</p>
</div>
""", unsafe_allow_html=True)

# Auto-connect on first load
if not st.session_state.api_configured:
    ok, _ = configure_api(api_key_input)
    if ok:
        st.session_state.api_configured = True

if not st.session_state.api_configured:
    st.warning("👈 Enter your **Gemini API Key** in the sidebar and click **Connect API**.")

# ── Tabs ─────────────────────────────────────
tab_yt, tab_file = st.tabs(["▶️  YouTube Link", "📁  Upload File (Video / Image)"])

# ══════════════════════════════
#  TAB 1 — YouTube
# ══════════════════════════════
with tab_yt:
    st.markdown("#### 🔗 Paste YouTube URL")
    st.markdown("""
    <div class="yt-box">
    <b>💡 How it works:</b> Gemini reads public YouTube videos directly — no download needed.
    Paste any YouTube link and click Analyse.
    </div>""", unsafe_allow_html=True)

    yt_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...", label_visibility="collapsed")

    if st.button("🚀 Analyse YouTube Video", use_container_width=True, key="yt_btn"):
        if not st.session_state.api_configured:
            st.error("❌ Connect your API key first.")
        elif not yt_url.strip():
            st.warning("⚠️ Paste a YouTube URL.")
        elif not is_youtube(yt_url):
            st.error("❌ Not a valid YouTube URL.")
        elif analysis_mode == "✏️ Custom Prompt" and not custom_prompt_text.strip():
            st.warning("⚠️ Enter a custom prompt in the sidebar.")
        else:
            with st.spinner(f"🧠 {selected_model} is analysing the YouTube video…"):
                try:
                    result = analyse_youtube(selected_model, yt_url, analysis_mode, custom_prompt_text)
                    st.session_state.last_result = result
                    st.session_state.chat_history.append({
                        "type": "YouTube", "mode": analysis_mode,
                        "model": selected_model, "result": result, "file": yt_url.strip()[:80],
                    })
                    st.success("✅ Done!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    if st.session_state.last_result and tab_yt:
        st.markdown("#### 📊 Result")
        st.markdown(f'<div class="result-box">{st.session_state.last_result}</div>', unsafe_allow_html=True)
        st.download_button("⬇️ Download (.txt)", st.session_state.last_result,
                           "yt_analysis.txt", "text/plain", key="dl_yt")
        if show_raw:
            with st.expander("🔍 Raw"): st.code(st.session_state.last_result)

# ══════════════════════════════
#  TAB 2 — File Upload
# ══════════════════════════════
with tab_file:
    col_up, col_fmt = st.columns([2, 1])

    with col_up:
        st.markdown("#### 📁 Upload Video or Image")
        uploaded = st.file_uploader(
            "Drag & drop or browse",
            type=SUPPORTED_VIDEO + SUPPORTED_IMAGE,
            help="Max 500 MB",
        )

    with col_fmt:
        st.markdown("#### 📋 Formats")
        st.markdown(f"""
        <div class="info-card">
        <b>🎥 Video</b><br>
        <span style="font-family:'DM Mono',monospace;font-size:0.8rem;color:#888899;">{', '.join(f'.{e}' for e in SUPPORTED_VIDEO)}</span><br><br>
        <b>🖼️ Image</b><br>
        <span style="font-family:'DM Mono',monospace;font-size:0.8rem;color:#888899;">{', '.join(f'.{e}' for e in SUPPORTED_IMAGE)}</span><br><br>
        <b>Max:</b> 500 MB
        </div>""", unsafe_allow_html=True)

    if uploaded and st.session_state.api_configured:
        ext        = uploaded.name.rsplit(".", 1)[-1].lower()
        file_type  = "video" if ext in SUPPORTED_VIDEO else "image"
        mime_type  = MIME_MAP.get(ext, "application/octet-stream")
        file_bytes = uploaded.read()
        file_mb    = len(file_bytes) / (1024 * 1024)

        if file_mb > 500:
            st.error(f"❌ File too large ({file_mb:.1f} MB). Max: 500 MB.")
        else:
            st.markdown("---")
            c1, c2 = st.columns([1.6, 1])
            with c1:
                st.markdown("#### 👁️ Preview")
                if file_type == "image": st.image(file_bytes, use_container_width=True)
                else:                    st.video(file_bytes)
            with c2:
                st.markdown("#### ℹ️ Details")
                st.markdown(f"""
                <div class="info-card">
                <b>Name:</b> {uploaded.name}<br>
                <b>Size:</b> {file_mb:.2f} MB<br>
                <b>Type:</b> {'🎥 Video' if file_type=='video' else '🖼️ Image'}<br>
                <b>Model:</b> {selected_model}<br>
                <b>Mode:</b> {analysis_mode}
                </div>""", unsafe_allow_html=True)
                if auto_clear and uploaded.name != st.session_state.uploaded_name:
                    st.session_state.last_result = ""

            st.markdown("---")
            if st.button("🚀 Analyse File", use_container_width=True, key="file_btn"):
                if analysis_mode == "✏️ Custom Prompt" and not custom_prompt_text.strip():
                    st.warning("⚠️ Enter a custom prompt in the sidebar.")
                else:
                    with st.spinner(f"🧠 {selected_model} is analysing…"):
                        try:
                            result = upload_and_analyse(
                                file_bytes, mime_type, uploaded.name,
                                selected_model, analysis_mode, custom_prompt_text
                            )
                            st.session_state.last_result  = result
                            st.session_state.uploaded_name = uploaded.name
                            st.session_state.chat_history.append({
                                "type": file_type.capitalize(), "mode": analysis_mode,
                                "model": selected_model, "result": result, "file": uploaded.name,
                            })
                            st.success("✅ Done!")
                        except Exception as e:
                            st.error(f"❌ {e}")

            if st.session_state.last_result:
                st.markdown("#### 📊 Result")
                st.markdown(f'<div class="result-box">{st.session_state.last_result}</div>', unsafe_allow_html=True)
                st.download_button("⬇️ Download (.txt)", st.session_state.last_result,
                                   f"analysis_{uploaded.name}.txt", "text/plain", key="dl_file")
                if show_raw:
                    with st.expander("🔍 Raw"): st.code(st.session_state.last_result)

    elif uploaded and not st.session_state.api_configured:
        st.warning("⚠️ Connect your API key first.")
    else:
        st.markdown("""
        <div style="text-align:center;padding:50px;color:#444466;">
            <div style="font-size:3.5rem;">🎞️</div>
            <div style="font-size:1rem;font-weight:600;color:#666688;margin-top:10px;">Upload a file to begin</div>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HISTORY
# ─────────────────────────────────────────────
if st.session_state.chat_history:
    st.markdown("---")
    st.markdown("#### 🗂️ Analysis History")
    for idx, item in enumerate(reversed(st.session_state.chat_history), 1):
        with st.expander(f"#{idx} [{item.get('type','?')}] {item['mode']} | {item['file'][:55]} | {item['model']}"):
            st.markdown(f'<div class="result-box">{item["result"]}</div>', unsafe_allow_html=True)
            st.download_button("⬇️ Download", item["result"], f"analysis_{idx}.txt", "text/plain", key=f"h_{idx}")
    if st.button("🗑️ Clear History"):
        st.session_state.chat_history = []
        st.session_state.last_result  = ""
        st.rerun()
