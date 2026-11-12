import os
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

EMOTIONS = {
    "neutral": {
        "title": "Neutral / Storyteller",
        "badge": "Neutral / Storyteller (शांत / कथावाचक)",
        "tip": (
            "🎯 **Vocal Coach Tip**: Sit tall with relaxed shoulders. Keep your pitch in a comfortable mid-range "
            "with a calm, steady cadence. Breathe from your diaphragm. Enunciate each word clearly without rushing."
        ),
        "hindi": (
            "पुराने जमाने की बात है, जब घने जंगलों के बीच एक शांत नदी बहती थी। वहां के लोग कहते थे कि उस नदी के "
            "पानी में एक अनोखा जादू है, जो हर सच्चे इंसान के दिल की बात समझ लेता था। उस रात, हवा में एक अजीब सी ठंडक थी।"
        ),
        "english": (
            "Deep within the ancient mountains, where the mist never seemed to clear, an old traveler began his long "
            "journey toward the silent valley. He knew the road ahead was filled with unexpected turns, yet he took a "
            "steady breath and stepped forward into the unknown."
        ),
    },
    "sad": {
        "title": "Sad & Grieving",
        "badge": "Sad & Grieving (उदास / गमगीन)",
        "tip": (
            "🎯 **Vocal Coach Tip**: Drop your physical energy and drop your chin slightly. Allow a lower pitch with "
            "gentle downward pitch inflections at sentence ends. Speak with heavy, prolonged exhalations and solemn pauses."
        ),
        "hindi": (
            "सब कुछ इतनी जल्दी खत्म हो जाएगा, मैंने कभी सपने में भी नहीं सोचा था... हर उम्मीद, हर वादा आज खामोश हो गया। "
            "अब इन वीरान रास्तों पर मेरा कोई नहीं रहा... सिर्फ एक गहरी तन्हाई बची है।"
        ),
        "english": (
            "Everything slipped away so quickly... I never imagined standing here alone, watching every promise we made "
            "crumble into cold, hollow silence. There is nowhere left for me to go."
        ),
    },
    "crying": {
        "title": "Crying & Choked",
        "badge": "Crying & Choked (रोते हुए / रुंधा गला)",
        "tip": (
            "🎯 **Vocal Coach Tip**: Slightly tense your throat and swallow hard. Introduce a slight crack or tremor in your voice. "
            "Take shaky, audible breaths or sniffles between short, broken clauses as if fighting back tears."
        ),
        "hindi": (
            "(रुंधे गले से) क्यों किया उसने ऐसा... मेरी क्या गलती थी? (हल्की सिसकी) मैं... मैं अब और दर्द नहीं सह सकता... "
            "भगवान के लिए मुझे अकेला छोड़ दो... सब कुछ बिखर गया है..."
        ),
        "english": (
            "(Choked breath / sniffle) Why did it have to end like this... what did I do wrong? (Voice cracking) Please... "
            "I just can't hold back the tears anymore... it hurts too much to pretend I'm okay."
        ),
    },
    "laughing": {
        "title": "Laughing & Giggling",
        "badge": "Laughing & Giggling (हंसते हुए / खिलखिलाहट)",
        "tip": (
            "🎯 **Vocal Coach Tip**: Smile widely so your cheekbones lift (this naturally brightens your acoustic resonance). "
            "Incorporate soft chuckles, breath pulses, and bouncy melodic pitch leaps between words."
        ),
        "hindi": (
            "(हंसते हुए) अरे भाई! तुमने उसकी शक्ल देखी जब वो गिरा? हाहाहा! सच कह रहा हूँ, मैंने आज तक अपनी ज़िंदगी में "
            "ऐसा मजेदार ड्रामा कभी नहीं देखा! रुक जाओ, पेट में दर्द हो रहा है हंसते-हंसते!"
        ),
        "english": (
            "(Laughing / chuckling) Oh you've got to be kidding me! Did you see his face when the bucket tipped over? Haha! "
            "I swear that is the funniest thing that has happened all year! Stop, my sides hurt from laughing!"
        ),
    },
    "excited": {
        "title": "Excited & Thrilled",
        "badge": "Excited & Thrilled (उत्साहित / रोमांचित)",
        "tip": (
            "🎯 **Vocal Coach Tip**: Expand your chest, raise your eyebrows, and lean in. Speak with high vocal energy, "
            "elevated pitch, fast tempo, and punchy, enthusiastic upward inflection."
        ),
        "hindi": (
            "अरे वाह! हम आखिरकार जीत गए! मुझे तो अपनी आँखों पर यकीन ही नहीं हो रहा कि हमने ये कर दिखाया! "
            "चलो जल्दी सामान बांधो, आज रात हमारा सबसे बड़ा जश्न होने वाला है!"
        ),
        "english": (
            "Yes! We actually did it! I can't believe our plan worked out so completely! "
            "Grab your bags right now, the grand adventure is finally beginning!"
        ),
    },
    "angry": {
        "title": "Angry & Furious",
        "badge": "Angry & Furious (क्रोधित / गुस्सैल)",
        "tip": (
            "🎯 **Vocal Coach Tip**: Clench your fists and lock your core. Deliver words with hard, sharp consonants (k, t, p, d) "
            "and forceful chest projection. Maintain an intense, unwavering, commanding tone."
        ),
        "hindi": (
            "बस, बहुत हो चुका! तुम्हारी इतनी हिम्मत कैसे हुई मेरे पीठ पीछे यह सब करने की? "
            "अगर एक और झूठ बोला ना, तो अंजाम भुगतने के लिए तैयार रहना! निकल जाओ मेरी नज़रों के सामने से!"
        ),
        "english": (
            "Enough! How dare you stand there and look me in the eye after what you did! "
            "Don't you dare say another word, or I swear you will regret this for the rest of your life!"
        ),
    },
    "scared": {
        "title": "Scared & Whispering",
        "badge": "Scared & Whispering (डरा हुआ / फुसफुसाहट / खौफ)",
        "tip": (
            "🎯 **Vocal Coach Tip**: Drop volume to an intense stage whisper. Use rapid, shallow breaths. Add nervous, tense pauses "
            "as if listening for a predator or footsteps approaching in the dark."
        ),
        "hindi": (
            "(धीमी कांपती आवाज़ में) श्शश... बिल्कुल चुप रहो! वो दरवाज़ा धीरे-धीरे खुल रहा है... "
            "कोई है जो अँधेरे में हमारे बिल्कुल पीछे खड़ा है... सांस भी मत लेना!"
        ),
        "english": (
            "(Tense whisper) Shh... be completely quiet! Did you hear that heavy thud in the hallway? "
            "Someone is turning the doorknob right now... don't make a sound, hide!"
        ),
    },
    "tired": {
        "title": "Tired & Exhausted",
        "badge": "Tired & Exhausted (थका हुआ / हांफता हुआ / कमजोर)",
        "tip": (
            "🎯 **Vocal Coach Tip**: Slump in your chair and let your jaw hang loose. Speak at the tail end of your exhalations "
            "with sluggish syllables, breathy timbre, and exhausted trailing pauses."
        ),
        "hindi": (
            "मुझमें अब... ज़रा भी जान नहीं बची। आँखें बंद हो रही हैं... पैर लड़खड़ा रहे हैं। "
            "मुझे... बस थोड़ी देर के लिए सोने दो... मुझे यहीं छोड़ो और तुम आगे बढ़ो..."
        ),
        "english": (
            "I can barely take another step... my vision is blurring, and every breath feels like carrying lead. "
            "Just leave me here... and go on without me... I can't go any further..."
        ),
    },
    "funny": {
        "title": "Funny & Sarcastic",
        "badge": "Funny & Sarcastic (मजाकिया / तंज भरा)",
        "tip": (
            "🎯 **Vocal Coach Tip**: Deliver with a mischievous smirk and mock-sweet pitch slides. Roll words with dry irony "
            "and pause theatrically before the punchline."
        ),
        "hindi": (
            "वाह भाई साहब! क्या अद्भुत दिमाग लगाया है आपने! तालियां बजनी चाहिए इस पर! "
            "अगली बार जब ऐसा क्रांतिकारी आइडिया आए ना, तो पहले मुझे भाग जाने का मौका दे देना!"
        ),
        "english": (
            "Oh brilliant! Pure genius of the century! What a revolutionary plan! "
            "Next time you get a brainstorm like that, please give me a five-minute head start to run away!"
        ),
    },
    "romantic": {
        "title": "Romantic & Gentle",
        "badge": "Romantic & Gentle (प्यार भरा / कोमल / धीमा)",
        "tip": (
            "🎯 **Vocal Coach Tip**: Speak close to the microphone with warm, soft breath. Keep your vocal tone intimate, "
            "velvety, low-pitched, and unhurried."
        ),
        "hindi": (
            "जब भी तुम करीब होते हो, दुनिया का सारा शोर जैसे अचानक थम जाता है। "
            "तुम्हारी एक मुस्कान ही मेरे हर मुश्किल दिन को रोशन कर देती है। हमेशा मेरे साथ रहना।"
        ),
        "english": (
            "Whenever you are near, the entire world seems to soften into quiet peace. "
            "In all this chaos, being right here with you is the only place that truly feels like home."
        ),
    },
}

EMOTION_CHOICES = [(data["badge"], key) for key, data in EMOTIONS.items()]

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

