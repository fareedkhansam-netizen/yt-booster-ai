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
#  CUSTOM CSS  (dark cinematic theme)
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
    }

    /* Background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 50%, #0a0f0a 100%);
        color: #e8e8f0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(15, 15, 30, 0.95) !important;
        border-right: 1px solid rgba(100, 220, 120, 0.15);
    }
    section[data-testid="stSidebar"] * {
        color: #c8c8e0 !important;
    }

    /* Header */
    .hero-header {
        background: linear-gradient(90deg, rgba(100,220,120,0.08), rgba(60,180,255,0.08));
        border: 1px solid rgba(100,220,120,0.2);
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 28px;
        text-align: center;
    }
    .hero-header h1 {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #64dc78, #3cb4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 6px 0;
    }
    .hero-header p {
        color: #8888aa;
        font-size: 1rem;
        margin: 0;
        font-family: 'DM Mono', monospace;
    }

    /* Cards */
    .info-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #64dc78, #3cb4ff) !important;
        color: #0a0a0f !important;
        font-weight: 700 !important;
        font-family: 'Syne', sans-serif !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 28px !important;
        font-size: 1rem !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover {
        opacity: 0.88 !important;
    }

    /* Text areas and inputs */
    .stTextArea textarea, .stTextInput input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(100,220,120,0.2) !important;
        color: #e8e8f0 !important;
        border-radius: 8px !important;
        font-family: 'DM Mono', monospace !important;
    }

    /* Select boxes */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(100,220,120,0.2) !important;
        color: #e8e8f0 !important;
        border-radius: 8px !important;
    }

    /* File uploader */
    .stFileUploader {
        background: rgba(255,255,255,0.02) !important;
        border: 2px dashed rgba(100,220,120,0.3) !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.03) !important;
        border-radius: 8px !important;
        color: #e8e8f0 !important;
    }

    /* Result box */
    .result-box {
        background: rgba(100,220,120,0.04);
        border: 1px solid rgba(100,220,120,0.2);
        border-radius: 12px;
        padding: 24px 28px;
        margin-top: 20px;
        font-family: 'DM Mono', monospace;
        font-size: 0.93rem;
        line-height: 1.75;
        color: #d8d8f0;
        white-space: pre-wrap;
    }

    /* Status badges */
    .badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        font-family: 'DM Mono', monospace;
    }
    .badge-green { background: rgba(100,220,120,0.15); color: #64dc78; border: 1px solid rgba(100,220,120,0.3); }
    .badge-blue  { background: rgba(60,180,255,0.15);  color: #3cb4ff; border: 1px solid rgba(60,180,255,0.3); }
    .badge-red   { background: rgba(255,80,80,0.15);   color: #ff5050; border: 1px solid rgba(255,80,80,0.3); }

    /* Divider */
    hr { border-color: rgba(255,255,255,0.06) !important; }

    /* Spinner override */
    .stSpinner > div { border-top-color: #64dc78 !important; }

    /* Hide Streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
GEMINI_MODELS = {
    "gemini-2.0-flash":          "Gemini 2.0 Flash  ⚡ (Fastest, multimodal)",
    "gemini-2.0-flash-lite":     "Gemini 2.0 Flash-Lite 🪶 (Lightweight & cheap)",
    "gemini-1.5-pro":            "Gemini 1.5 Pro 🧠 (2M context, best quality)",
    "gemini-1.5-flash":          "Gemini 1.5 Flash ⚡ (Fast & versatile)",
    "gemini-1.5-flash-8b":       "Gemini 1.5 Flash-8B 🔬 (Smallest 1.5 model)",
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

SUPPORTED_VIDEO = ["mp4", "mov", "avi", "mkv", "webm", "flv", "3gp", "wmv"]
SUPPORTED_IMAGE = ["jpg", "jpeg", "png", "gif", "webp", "bmp"]
MAX_FILE_MB = 500

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
for key, default in {
    "api_configured": False,
    "chat_history": [],
    "last_result": "",
    "uploaded_file_uri": None,
    "uploaded_mime": None,
    "uploaded_name": "",
    "file_type": None,          # "video" or "image"
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def configure_api(api_key: str) -> bool:
    try:
        genai.configure(api_key=api_key.strip())
        # Quick validation
        genai.GenerativeModel("gemini-1.5-flash").generate_content("ping")
        return True
    except Exception:
        return False


def upload_to_gemini(file_bytes: bytes, mime_type: str, display_name: str):
    """Upload file bytes to Gemini Files API and wait until active."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(display_name).suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        gfile = genai.upload_file(path=tmp_path, mime_type=mime_type, display_name=display_name)
        # Wait for processing
        bar = st.progress(0, text="⏳ Processing file on Gemini servers…")
        step = 0
        while gfile.state.name == "PROCESSING":
            time.sleep(2)
            gfile = genai.get_file(gfile.name)
            step = min(step + 8, 90)
            bar.progress(step, text=f"⏳ Processing… ({step}%)")
        bar.progress(100, text="✅ File ready!")
        time.sleep(0.4)
        bar.empty()
        if gfile.state.name == "FAILED":
            raise RuntimeError("Gemini file processing failed.")
        return gfile
    finally:
        os.unlink(tmp_path)


def run_analysis(model_id: str, mode: str, custom_prompt: str, gfile, system_hint: str = "") -> str:
    """Send analysis request to Gemini and return text."""
    if mode == "✏️ Custom Prompt":
        prompt = custom_prompt.strip() or "Describe this media file in detail."
    else:
        prompts_map = {
            "📝 General Summary":            "Provide a comprehensive summary of this video/image. Cover the main topic, key events, people, and overall message.",
            "🎭 Scene-by-Scene Breakdown":   "Break down this video scene by scene. For each scene describe: timestamp range (if applicable), what happens visually, what is said or heard, and the significance.",
            "😊 Sentiment & Emotion Analysis":"Analyze the emotional tone and sentiment throughout this media. Identify moments of joy, tension, sadness, excitement, etc. and explain what triggers them.",
            "🔑 Key Moments & Highlights":   "Identify and list the most important moments, turning points, or highlights in this video/image. Explain why each is significant.",
            "📊 Content & Topic Analysis":   "Analyze the topics, themes, and subject matter. Categorize the content and provide insights into its purpose and target audience.",
            "🗣️ Speech Transcription":       "Transcribe all spoken words in this video as accurately as possible. Format with timestamps if possible. Note any unclear audio.",
            "👁️ Visual Description & Objects":"Describe in detail all visual elements: people, objects, text on screen, colors, environment, and visual style.",
            "🛡️ Content Safety Review":      "Review this content for safety. Identify any potentially sensitive, harmful, or age-restricted elements. Provide an overall safety rating.",
            "🎬 Cinematic / Production Analysis": "Analyze the production quality: camera work, lighting, editing, sound design, graphics, pacing, and overall production value.",
        }
        prompt = prompts_map.get(mode, "Describe this media file.")

    model = genai.GenerativeModel(model_id)
    response = model.generate_content([gfile, prompt])
    return response.text


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 12px 0 20px 0;">
            <div style="font-size:2.4rem;">🎬</div>
            <div style="font-size:1.1rem; font-weight:800; background:linear-gradient(90deg,#64dc78,#3cb4ff);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                Gemini Video Analyst Pro
            </div>
            <div style="font-size:0.75rem; color:#555577; font-family:'DM Mono',monospace; margin-top:4px;">
                powered by Google Gemini AI
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ── API Key ──────────────────────────────
    st.markdown("### 🔑 API Configuration")
    api_key_input = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="AIza...",
        value="AIzaSyAlGN0e_4bYuxCgXADqGbqfnxC-5vHkvMg",
        help="Get your key from https://aistudio.google.com/",
    )

    col_btn, col_status = st.columns([1.5, 1])
    with col_btn:
        if st.button("Connect", use_container_width=True):
            with st.spinner("Connecting…"):
                ok = configure_api(api_key_input)
            if ok:
                st.session_state.api_configured = True
                st.success("Connected ✓")
            else:
                st.session_state.api_configured = False
                st.error("Invalid key or quota error.")

    if st.session_state.api_configured:
        st.markdown('<span class="badge badge-green">● API Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-red">○ Not Connected</span>', unsafe_allow_html=True)

    st.divider()

    # ── Model Selection ──────────────────────
    st.markdown("### 🤖 Model Selection")
    selected_model = st.selectbox(
        "Choose Gemini Model",
        options=list(GEMINI_MODELS.keys()),
        format_func=lambda m: GEMINI_MODELS[m],
        index=0,
    )
    st.markdown(
        f'<span class="badge badge-blue">▸ {selected_model}</span>',
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Analysis Mode ────────────────────────
    st.markdown("### 🔍 Analysis Mode")
    analysis_mode = st.selectbox("Select Mode", ANALYSIS_MODES, index=0)

    custom_prompt_text = ""
    if analysis_mode == "✏️ Custom Prompt":
        custom_prompt_text = st.text_area(
            "Your Custom Prompt",
            placeholder="Ask anything about the video or image…",
            height=120,
        )

    st.divider()

    # ── Settings ─────────────────────────────
    st.markdown("### ⚙️ Settings")
    show_raw = st.checkbox("Show raw response", value=False)
    auto_clear = st.checkbox("Clear history on new upload", value=True)

    st.divider()
    st.markdown(
        '<div style="font-size:0.72rem; color:#444466; text-align:center; font-family:\'DM Mono\',monospace;">'
        "Gemini Video Analyst Pro<br>© 2024 — All rights reserved"
        "</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
#  MAIN AREA
# ─────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-header">
        <h1>🎬 Gemini Video Analyst Pro</h1>
        <p>Upload a video or image → choose a model & mode → get AI-powered analysis instantly</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.api_configured:
    st.info("👈 Please enter your **Google Gemini API Key** in the sidebar and click **Connect** to get started.")
    # Auto-try with hardcoded key
    with st.spinner("Auto-connecting with saved key…"):
        ok = configure_api(api_key_input)
    if ok:
        st.session_state.api_configured = True
        st.success("✅ Auto-connected with saved key!")
        st.rerun()

# ── Upload Section ───────────────────────────
col_upload, col_info = st.columns([2, 1])

with col_upload:
    st.markdown("#### 📁 Upload Media File")
    uploaded = st.file_uploader(
        "Drag & drop or browse",
        type=SUPPORTED_VIDEO + SUPPORTED_IMAGE,
        help=f"Supported: {', '.join(SUPPORTED_VIDEO + SUPPORTED_IMAGE)} | Max {MAX_FILE_MB} MB",
    )

with col_info:
    st.markdown("#### 📋 Supported Formats")
    st.markdown(
        f"""
        <div class="info-card">
        <b>🎥 Video</b><br>
        <span style="font-family:'DM Mono',monospace; font-size:0.82rem; color:#888899;">
        {', '.join(f'.{e}' for e in SUPPORTED_VIDEO)}</span><br><br>
        <b>🖼️ Image</b><br>
        <span style="font-family:'DM Mono',monospace; font-size:0.82rem; color:#888899;">
        {', '.join(f'.{e}' for e in SUPPORTED_IMAGE)}</span><br><br>
        <b>📦 Max Size:</b> {MAX_FILE_MB} MB
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Process Upload ───────────────────────────
if uploaded and st.session_state.api_configured:
    ext = uploaded.name.rsplit(".", 1)[-1].lower()
    file_type = "video" if ext in SUPPORTED_VIDEO else "image"
    mime_map = {
        "mp4": "video/mp4", "mov": "video/quicktime", "avi": "video/x-msvideo",
        "mkv": "video/x-matroska", "webm": "video/webm", "flv": "video/x-flv",
        "3gp": "video/3gpp", "wmv": "video/x-ms-wmv",
        "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
        "gif": "image/gif", "webp": "image/webp", "bmp": "image/bmp",
    }
    mime_type = mime_map.get(ext, "application/octet-stream")
    file_bytes = uploaded.read()
    file_mb = len(file_bytes) / (1024 * 1024)

    if file_mb > MAX_FILE_MB:
        st.error(f"❌ File too large ({file_mb:.1f} MB). Max allowed: {MAX_FILE_MB} MB.")
    else:
        st.markdown("---")
        col_prev, col_meta = st.columns([1.6, 1])

        with col_prev:
            st.markdown("#### 👁️ Preview")
            if file_type == "image":
                st.image(file_bytes, use_container_width=True)
            else:
                st.video(file_bytes)

        with col_meta:
            st.markdown("#### ℹ️ File Details")
            st.markdown(
                f"""
                <div class="info-card">
                <b>📄 Name:</b> {uploaded.name}<br>
                <b>📦 Size:</b> {file_mb:.2f} MB<br>
                <b>🎞️ Type:</b> {'🎥 Video' if file_type == 'video' else '🖼️ Image'}<br>
                <b>🔧 MIME:</b> <span style="font-family:'DM Mono',monospace;font-size:0.82rem;">{mime_type}</span><br>
                <b>🤖 Model:</b> <span style="font-family:'DM Mono',monospace;font-size:0.82rem;">{selected_model}</span><br>
                <b>🔍 Mode:</b> {analysis_mode}
                </div>
                """,
                unsafe_allow_html=True,
            )
            if auto_clear and uploaded.name != st.session_state.uploaded_name:
                st.session_state.chat_history = []
                st.session_state.last_result = ""
                st.session_state.uploaded_file_uri = None

        st.markdown("---")

        # ── Analyze Button ───────────────────
        if st.button("🚀 Analyse Now", use_container_width=True):
            if analysis_mode == "✏️ Custom Prompt" and not custom_prompt_text.strip():
                st.warning("⚠️ Please enter a custom prompt in the sidebar.")
            else:
                with st.spinner("📤 Uploading to Gemini Files API…"):
                    try:
                        gfile = upload_to_gemini(file_bytes, mime_type, uploaded.name)
                        st.session_state.uploaded_name = uploaded.name
                    except Exception as e:
                        st.error(f"❌ Upload failed: {e}")
                        st.stop()

                with st.spinner(f"🧠 {selected_model} is analysing…"):
                    try:
                        result = run_analysis(
                            selected_model,
                            analysis_mode,
                            custom_prompt_text,
                            gfile,
                        )
                        st.session_state.last_result = result
                        st.session_state.chat_history.append({
                            "mode": analysis_mode,
                            "model": selected_model,
                            "result": result,
                            "file": uploaded.name,
                        })
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {e}")
                        st.stop()

        # ── Show Result ──────────────────────
        if st.session_state.last_result:
            st.markdown("#### 📊 Analysis Result")
            st.markdown(
                f'<div class="result-box">{st.session_state.last_result}</div>',
                unsafe_allow_html=True,
            )
            col_dl, col_copy = st.columns(2)
            with col_dl:
                st.download_button(
                    "⬇️ Download Result (.txt)",
                    data=st.session_state.last_result,
                    file_name=f"gemini_analysis_{uploaded.name}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            if show_raw:
                with st.expander("🔍 Raw Response"):
                    st.code(st.session_state.last_result, language="markdown")

elif uploaded and not st.session_state.api_configured:
    st.warning("⚠️ Please connect your Gemini API key first (sidebar).")

# ── Chat History ─────────────────────────────
if st.session_state.chat_history:
    st.markdown("---")
    st.markdown("#### 🗂️ Analysis History")
    for idx, item in enumerate(reversed(st.session_state.chat_history), 1):
        with st.expander(f"#{idx} — {item['mode']} | {item['file']} | {item['model']}"):
            st.markdown(
                f'<div class="result-box">{item["result"]}</div>',
                unsafe_allow_html=True,
            )
            st.download_button(
                "⬇️ Download",
                data=item["result"],
                file_name=f"analysis_{idx}_{item['file']}.txt",
                mime="text/plain",
                key=f"dl_{idx}",
            )
    if st.button("🗑️ Clear History"):
        st.session_state.chat_history = []
        st.session_state.last_result = ""
        st.rerun()

# ── Empty State ───────────────────────────────
if not uploaded:
    st.markdown(
        """
        <div style="text-align:center; padding: 60px 20px; color:#444466;">
            <div style="font-size:4rem;">🎞️</div>
            <div style="font-size:1.2rem; font-weight:600; color:#666688; margin-top:12px;">
                No file uploaded yet
            </div>
            <div style="font-size:0.88rem; font-family:'DM Mono',monospace; margin-top:8px; color:#333355;">
                Upload a video or image above to begin AI-powered analysis
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
