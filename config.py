import os
import json
import shutil
from pathlib import Path
import gradio as gr

# Automatically acknowledge Coqui CPML terms for non-interactive / automated environments
os.environ["COQUI_TOC_ACK"] = "1"
os.environ["COQUI_TOS_AGREED"] = "1"

# ---------------------------------------------------------
# Base Directories
# ---------------------------------------------------------
BASE_DIR = Path(__file__).parent.resolve()
VOICES_DIR = BASE_DIR / "voices"
OUTPUTS_DIR = BASE_DIR / "outputs"
DEFAULT_PROJECT_NAME = "Default_Project"

VOICES_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

NEW_CHAR_OPTION = "➕ [Create New Character...]"

# FFmpeg binary resolution
FFMPEG_BIN = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"

# ---------------------------------------------------------
# Voice Presets & 10 Emotion Profiles
# ---------------------------------------------------------
PRESET_VOICES = {
    "Man - Deep & Authoritative (Damien)": "Damien Black",
    "Man - Warm Storyteller (Viktor)": "Viktor Eka",
    "Man - Young & Energetic (Gilberto)": "Gilberto Mathias",
    "Man - Calm & Grounded (Andrew)": "Andrew Chipper",
    "Woman - Clear & Expressive (Claribel)": "Claribel Dervla",
    "Woman - Warm & Narrative (Daisy)": "Daisy Studious",
    "Woman - Soft & Calm (Gracie)": "Gracie Wise",
    "Woman - Bright & Engaging (Tammie)": "Tammie Ema",
}

# ---------------------------------------------------------
# 15 Categorized Emotion & Delivery Taxonomies (121 Emotions)
# ---------------------------------------------------------
EMOTIONS_DATA_FILE = BASE_DIR / "emotions_data.json"
if EMOTIONS_DATA_FILE.exists():
    try:
        with open(EMOTIONS_DATA_FILE, "r", encoding="utf-8") as _f:
            _raw_data = json.load(_f)
            EMOTION_CATEGORIES = _raw_data.get("categories", [])
            EMOTIONS = _raw_data.get("emotions", {})
            CORE_EMOTIONS = _raw_data.get("core_emotions", [])
            EMOTION_TO_ANCHOR_MAP = _raw_data.get("anchor_map", {})
    except Exception:
        EMOTION_CATEGORIES = []
        EMOTIONS = {}
        CORE_EMOTIONS = []
        EMOTION_TO_ANCHOR_MAP = {}
else:
    EMOTION_CATEGORIES = []
    EMOTIONS = {}
    CORE_EMOTIONS = []
    EMOTION_TO_ANCHOR_MAP = {}

CORE_EMOTION_CHOICES = [(c["badge"], c["id"]) for c in CORE_EMOTIONS]
EMOTION_CHOICES = [(data["badge"], key) for key, data in EMOTIONS.items()]


def get_emotion_anchor(emotion_key: str) -> str:
    """Returns the core anchor take (neutral, happy, sad, angry, whisper, dramatic) for any of the 121 emotions."""
    if not emotion_key:
        return "neutral"
    clean = emotion_key.strip().lower()
    return EMOTION_TO_ANCHOR_MAP.get(clean, "neutral")

# ---------------------------------------------------------
# Professional Tailwind Admin Styling
# ---------------------------------------------------------
CUSTOM_CSS = """
/* Professional Studio & Admin Panel Styling */
.gradio-container {
    max-width: 1440px !important;
    margin: 0 auto !important;
    padding-top: 0.75rem !important;
}

/* Studio Top Navigation Bar */
.studio-navbar {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 16px 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
}

/* Project Badge Pill */
.project-pill {
    background: #0284c7;
    color: #ffffff;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.85rem;
    display: inline-block;
}

/* Dedicated Voice Studio Drawer */
.studio-drawer {
    background: #0b1329 !important;
    border: 1px solid #38bdf8 !important;
    border-radius: 14px !important;
    padding: 20px !important;
    margin-top: 14px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 10px 30px -5px rgba(2, 132, 199, 0.18) !important;
}

/* Media Admin Table & Cards */
.media-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 14px;
}

/* Primary Action Buttons */
button.primary {
    background: #0284c7 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    transition: all 0.15s ease-in-out !important;
}
button.primary:hover {
    background: #0369a1 !important;
    transform: translateY(-1px);
}
"""

TAILWIND_THEME = gr.themes.Soft(
    primary_hue=gr.themes.colors.sky,
    secondary_hue=gr.themes.colors.slate,
    neutral_hue=gr.themes.colors.slate,
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
).set(
    body_background_fill="#0b0f19",
    body_background_fill_dark="#0b0f19",
    block_background_fill="#111827",
    block_background_fill_dark="#111827",
    block_border_color="#1f2937",
    block_border_color_dark="#1f2937",
    block_label_text_color="#94a3b8",
    block_label_text_color_dark="#94a3b8",
    input_background_fill="#0f172a",
    input_background_fill_dark="#0f172a",
    input_border_color="#334155",
    input_border_color_dark="#334155",
    button_primary_background_fill="#0284c7",
    button_primary_background_fill_dark="#0284c7",
    button_primary_background_fill_hover="#0369a1",
    button_primary_background_fill_hover_dark="#0369a1",
    button_primary_text_color="#ffffff",
    button_secondary_background_fill="#1e293b",
    button_secondary_background_fill_dark="#1e293b",
    button_secondary_border_color="#334155",
    button_secondary_border_color_dark="#334155",
    button_secondary_text_color="#e2e8f0",
)

