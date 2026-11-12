import os
import re
import sys
import time
import shutil
import tempfile
import subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
import gradio as gr

# Automatically acknowledge Coqui CPML terms for non-interactive / automated environments
os.environ["COQUI_TOC_ACK"] = "1"
os.environ["COQUI_TOS_AGREED"] = "1"

# --- Fix: Monkey-patch XTTS tokenizer for Hindi number expansion ---
# By default, num2words raises NotImplementedError for Hindi ('hi').
# We patch the tokenizer to convert numbers, ordinals, and decimals into proper Hindi words.
import TTS.tts.layers.xtts.tokenizer as xtts_tokenizer

HINDI_NUMS_0_TO_99 = [
    "शून्य", "एक", "दो", "तीन", "चार", "पांच", "छह", "सात", "आठ", "नौ",
    "दस", "ग्यारह", "बारह", "तेरह", "चौदह", "पंद्रह", "सोलह", "सत्रह", "अठारह", "उन्नीस",
    "बीस", "इक्कीस", "बाईस", "तेईस", "चौबीस", "पच्चीस", "छब्बीस", "सत्ताईस", "अट्ठाईस", "उनतीस",
    "तीस", "इकतीस", "बत्तीस", "तैंतीस", "चौंतीस", "पैंतीस", "छत्तीस", "सैंतीस", "अड़तीस", "उनतालीस",
    "चालीस", "इकतालीस", "बयालीस", "तैंतालीस", "चवालीस", "पैंतालीस", "छियालीस", "सैंतालीस", "अड़तालीस", "उनचास",
    "पचास", "इक्यावन", "बावन", "तिरपन", "चौवन", "पचपन", "छप्पन", "सत्तावन", "अट्ठावन", "उनसठ",
    "साठ", "इकसठ", "बासठ", "तिरसठ", "चौंसठ", "पैंसठ", "छियासठ", "सड़सठ", "अड़सठ", "उनहत्तर",
    "सत्तर", "इकहत्तर", "बहत्तर", "तिहत्तर", "चौहत्तर", "पचहत्तर", "छिहत्तर", "सतहत्तर", "अठहत्तर", "उन्यासी",
    "अस्सी", "इक्यासी", "बयासी", "तिरासी", "चौरासी", "पचासी", "छियासी", "सत्तासी", "अट्ठासी", "नवासी",
    "नब्बे", "इक्यानवे", "बानवे", "तिरानवे", "चौरानवे", "पचानवे", "छियानवे", "सत्तानवे", "अठानवे", "निन्यानवे",
]


def hindi_num2words(n: int) -> str:
    """Converts integers up to crores into natural Hindi Devanagari words."""
    if n < 0:
        return "माइनस " + hindi_num2words(-n)
    if n < 100:
        return HINDI_NUMS_0_TO_99[n]
    if n < 1000:
        hundreds = n // 100
        rem = n % 100
        res = HINDI_NUMS_0_TO_99[hundreds] + " सौ"
        if rem > 0:
            res += " " + HINDI_NUMS_0_TO_99[rem]
        return res
    if n < 100000:
        thousands = n // 1000
        rem = n % 1000
        res = hindi_num2words(thousands) + " हज़ार"
        if rem > 0:
            res += " " + hindi_num2words(rem)
        return res
    if n < 10000000:
        lakhs = n // 100000
        rem = n % 100000
        res = hindi_num2words(lakhs) + " लाख"
        if rem > 0:
            res += " " + hindi_num2words(rem)
        return res
    crores = n // 10000000
    rem = n % 10000000
    res = hindi_num2words(crores) + " करोड़"
    if rem > 0:
        res += " " + hindi_num2words(rem)
    return res


orig_expand_number = xtts_tokenizer._expand_number
orig_expand_ordinal = xtts_tokenizer._expand_ordinal
orig_expand_decimal = xtts_tokenizer._expand_decimal_point


def safe_expand_number(m, lang="en"):
    if lang == "hi":
        try:
            return hindi_num2words(int(m.group(0)))
        except Exception:
            return m.group(0)
    try:
        return orig_expand_number(m, lang=lang)
    except Exception:
        return m.group(0)


def safe_expand_ordinal(m, lang="en"):
    if lang == "hi":
        try:
            val = int(m.group(1))
            ordinal_map = {1: "पहला", 2: "दूसरा", 3: "तीसरा", 4: "चौथा", 5: "पांचवां"}
            return ordinal_map.get(val, hindi_num2words(val) + "वां")
        except Exception:
            return m.group(1)
    try:
        return orig_expand_ordinal(m, lang=lang)
    except Exception:
        return m.group(1)


def safe_expand_decimal_point(m, lang="en"):
    amount = m.group(1).replace(",", ".")
    if lang == "hi":
        try:
            parts = amount.split(".")
            int_part = hindi_num2words(int(parts[0])) if parts[0] else "शून्य"
            if len(parts) > 1 and parts[1]:
                dec_digits = " ".join(hindi_num2words(int(d)) for d in parts[1])
                return f"{int_part} दशमलव {dec_digits}"
            return int_part
        except Exception:
            return amount
    try:
        return orig_expand_decimal(m, lang=lang)
    except Exception:
        return amount


# Apply the safe tokenizer patches
xtts_tokenizer._expand_number = safe_expand_number
xtts_tokenizer._expand_ordinal = safe_expand_ordinal
xtts_tokenizer._expand_decimal_point = safe_expand_decimal_point

from TTS.api import TTS

# ---------------------------------------------------------
# 1. Configuration & Directories
# ---------------------------------------------------------
BASE_DIR = Path(__file__).parent.resolve()
VOICES_DIR = BASE_DIR / "voices"
OUTPUTS_DIR = BASE_DIR / "outputs"
VOICES_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

NEW_CHAR_OPTION = "➕ [Create New Character...]"

# Built-in XTTS-v2 high-quality speakers categorized by gender/tone
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

# 10 Professional Acting Emotions with Tailored Prompts & Vocal Coach Instructions
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

# Locate FFmpeg binary safely (checking standard Homebrew paths on Apple Silicon)
FFMPEG_BIN = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"

# ---------------------------------------------------------
# 2. Load XTTS-v2 Model (CPU is optimal & stable on Apple Silicon)
# ---------------------------------------------------------
print("Initializing XTTS-v2 engine on Apple Silicon...")
# CPU inference is the officially recommended, rock-solid mode for XTTS-v2 on macOS Apple Silicon
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
print("XTTS-v2 model loaded successfully!")


def get_existing_characters():
    """Extracts unique character names from voices/ folder."""
    characters = set()
    for f in VOICES_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in {".wav", ".mp3", ".m4a", ".flac", ".ogg"}:
            stem = f.stem.lower()
            found_emotion = False
            for emo_key in EMOTIONS.keys():
                if stem.endswith(f"_{emo_key}") or stem.endswith(f"-{emo_key}"):
                    char_part = stem[: -(len(emo_key) + 1)].replace("_", " ").replace("-", " ").strip().title()
                    if char_part:
                        characters.add(char_part)
                    found_emotion = True
                    break
            if not found_emotion and stem != "readme":
                clean_name = stem.replace("_", " ").replace("-", " ").strip().title()
                if clean_name:
                    characters.add(clean_name)
    return sorted(list(characters))


def get_character_dropdown_choices():
    """Returns dropdown choices for character selection with 'Create New' option."""
    chars = get_existing_characters()
    return chars + [NEW_CHAR_OPTION]


def format_voice_file_label(filename: str) -> str:
    """Formats custom voice filenames into clean Character + Emotion labels."""
    base = Path(filename).stem.lower()
    for key, data in EMOTIONS.items():
        if base.endswith(f"_{key}") or base.endswith(f"-{key}"):
            char_name = base[: -(len(key) + 1)].replace("_", " ").replace("-", " ").strip().title()
            if not char_name:
                char_name = "Character"
            return f"🎭 Custom: {char_name} — {data['title']} [{filename}]"
    clean_name = base.replace("_", " ").replace("-", " ").strip().title()
    return f"🎭 Custom: {clean_name} — Base Voice [{filename}]"


def get_available_voices():
    """Combines custom emotion voice files with built-in studio presets, grouped by character."""
    custom_labels = []
    custom_files = sorted(
        [
            f.name
            for f in VOICES_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in {".wav", ".mp3", ".m4a", ".flac", ".ogg"}
        ]
    )
    for cf in custom_files:
        custom_labels.append(format_voice_file_label(cf))

    # Sort custom labels so all emotions for each character are grouped together
    custom_labels.sort()

    preset_labels = [f"🎙️ Preset: {p}" for p in PRESET_VOICES.keys()]
    return custom_labels + preset_labels


def get_character_status_markdown(character_name: str) -> str:
    """Returns dynamic badge status showing which emotions are recorded for the given character."""
    if not character_name or not character_name.strip() or character_name == NEW_CHAR_OPTION:
        return "💡 *Select an existing Character or enter a new name to view emotion status.*"

    clean_char = re.sub(r"[^a-zA-Z0-9_-]", "_", character_name.strip().lower())
    existing_emotions = set()

    for f in VOICES_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in {".wav", ".mp3", ".m4a", ".flac", ".ogg"}:
            stem = f.stem.lower()
            if stem.startswith(f"{clean_char}_") or stem.startswith(f"{clean_char}-"):
                emo = stem[len(clean_char) + 1 :]
                existing_emotions.add(emo)
            elif stem == clean_char:
                existing_emotions.add("neutral")

    badges = []
    for key, data in EMOTIONS.items():
        title = data["title"]
        if key in existing_emotions:
            badges.append(f"✅ **{title}**")
        else:
            badges.append(f"⚪ *{title}*")

    recorded_count = sum(1 for k in EMOTIONS if k in existing_emotions)
    display_title = character_name.strip().replace("_", " ").replace("-", " ").title()
    header = f"**Character: {display_title}** &nbsp;•&nbsp; ({recorded_count}/{len(EMOTIONS)} emotions recorded)\n\n"
    return header + " &nbsp;•&nbsp; ".join(badges)


def get_next_unrecorded_emotion(character_name: str, current_emotion: str = "neutral") -> str:
    """Finds the next emotion that hasn't been recorded yet for this character."""
    clean_char = re.sub(r"[^a-zA-Z0-9_-]", "_", character_name.strip().lower())
    existing = set()
    for f in VOICES_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in {".wav", ".mp3", ".m4a", ".flac", ".ogg"}:
            stem = f.stem.lower()
            if stem.startswith(f"{clean_char}_") or stem.startswith(f"{clean_char}-"):
                emo = stem[len(clean_char) + 1 :]
                existing.add(emo)
            elif stem == clean_char:
                existing.add("neutral")

    emotion_keys = list(EMOTIONS.keys())
    curr_idx = emotion_keys.index(current_emotion) if current_emotion in emotion_keys else 0

    # Look for the next unrecorded emotion starting from current + 1
    for i in range(1, len(emotion_keys) + 1):
        candidate = emotion_keys[(curr_idx + i) % len(emotion_keys)]
        if candidate not in existing:
            return candidate

    return current_emotion


# Comprehensive English loanwords & common names used in Hindi dialogues, mapped to natural Devanagari pronunciation
HINDI_LOANWORDS = {
    # Workspace & Everyday objects
    "desk": "डेस्क",
    "tiffin": "टिफिन",
    "office": "ऑफिस",
    "school": "स्कूल",
    "college": "कॉलेज",
    "class": "क्लास",
    "student": "स्टूडेंट",
    "teacher": "टीचर",
    "principal": "प्रिंसिपल",
    "hospital": "अस्पताल",
    "doctor": "डॉक्टर",
    "nurse": "नर्स",
    "clinic": "क्लिनिक",
    "medicine": "दवा",
    "patient": "मरीज",
    "ambulance": "एंबुलेंस",
    # Tech & gadgets
    "phone": "फ़ोन",
    "mobile": "मोबाइल",
    "call": "कॉल",
    "laptop": "लैपटॉप",
    "computer": "कंप्यूटर",
    "screen": "स्क्रीन",
    "mouse": "माउस",
    "keyboard": "कीबोर्ड",
    "charger": "चार्जर",
    "cable": "केबल",
    "battery": "बैटरी",
    "camera": "कैमरा",
    "video": "वीडियो",
    "photo": "फ़ोटो",
    "audio": "ऑडियो",
    "film": "फिल्म",
    "movie": "मूवी",
    "message": "मैसेज",
    "chat": "चैट",
    "post": "पोस्ट",
    "status": "स्टेटस",
    "link": "लिंक",
    "site": "साइट",
    "website": "वेबसाइट",
    "app": "ऐप",
    "online": "ऑनलाइन",
    "offline": "ऑफलाइन",
    "net": "नेट",
    "internet": "इंटरनेट",
    "wifi": "वाईफ़ाई",
    "password": "पासवर्ड",
    "data": "डेटा",
    "system": "सिस्टम",
    "software": "सॉफ्टवेयर",
    # Transportation & Places
    "car": "कार",
    "bike": "बाइक",
    "bus": "बस",
    "train": "ट्रेन",
    "station": "स्टेशन",
    "metro": "मेट्रो",
    "flight": "फ्लाइट",
    "airport": "एयरपोर्ट",
    "taxi": "टैक्सी",
    "auto": "ऑटो",
    "driver": "ड्राइवर",
    "road": "रोड",
    "highway": "हाईवे",
    "traffic": "ट्रैफिक",
    "bridge": "ब्रिज",
    "hotel": "होटल",
    "restaurant": "रेस्टोरेंट",
    "cafe": "कैफे",
    "mall": "मॉल",
    "market": "मार्केट",
    "shop": "शॉप",
    "bank": "बैंक",
    "atm": "एटीएम",
    "park": "पार्क",
    "garden": "गार्डन",
    "gym": "जिम",
    # Home & Furniture
    "room": "रूम",
    "table": "टेबल",
    "chair": "चेयर",
    "bed": "बेड",
    "door": "डोर",
    "window": "विंडो",
    "light": "लाइट",
    "fan": "फैन",
    "switch": "स्विच",
    "bottle": "बोतल",
    "bag": "बैग",
    "box": "बॉक्स",
    "packet": "पैकेट",
    "plate": "प्लेट",
    "glass": "ग्लास",
    "cup": "कप",
    "lock": "लॉक",
    "key": "चाबी",
    # Food & Daily Routine
    "lunch": "लंच",
    "dinner": "डिनर",
    "breakfast": "ब्रेकफ़ास्ट",
    "snack": "स्नैक",
    "tea": "चाय",
    "coffee": "कॉफ़ी",
    "water": "वॉटर",
    "juice": "जूस",
    "milk": "दूध",
    "cake": "केक",
    "chocolate": "चॉकलेट",
    "ice cream": "आइसक्रीम",
    # Workplace, Business & Money
    "job": "जॉब",
    "interview": "इंटरव्यू",
    "salary": "सैलरी",
    "bonus": "बोनस",
    "meeting": "मीटिंग",
    "presentation": "प्रेजेंटेशन",
    "project": "प्रोजेक्ट",
    "target": "टारगेट",
    "client": "क्लाइंट",
    "service": "सर्विस",
    "order": "ऑर्डर",
    "delivery": "डिलीवरी",
    "money": "मनी",
    "cash": "कैश",
    "bill": "बिल",
    "card": "कार्ड",
    "manager": "मैनेजर",
    "boss": "बॉस",
    "staff": "स्टाफ",
    "sir": "सर",
    "madam": "मैडम",
    "police": "पुलिस",
    "company": "कंपनी",
    "business": "बिजनेस",
    "contract": "कॉन्ट्रैक्ट",
    "deal": "डील",
    "offer": "ऑफर",
    "shift": "शिफ्ट",
    # Entertainment & Sports
    "game": "गेम",
    "match": "मैच",
    "team": "टीम",
    "player": "प्लेयर",
    "coach": "कोच",
    "ground": "ग्राउंड",
    "party": "पार्टी",
    "club": "क्लब",
    "song": "गाना",
    "music": "म्यूज़िक",
    "dance": "डांस",
    # Emotions, Conversational Words & Slang
    "problem": "प्रॉब्लम",
    "tension": "टेंशन",
    "issue": "इश्यू",
    "idea": "आइडिया",
    "plan": "प्लान",
    "secret": "सीक्रेट",
    "surprise": "सरप्राइज़",
    "gift": "गिफ्ट",
    "ticket": "टिकट",
    "help": "हेल्प",
    "please": "प्लीज़",
    "thanks": "थैंक्स",
    "thank you": "थैंक यू",
    "sorry": "सॉरी",
    "hello": "हैलो",
    "hi": "हाय",
    "bye": "बाय",
    "goodbye": "गुडबाय",
    "ok": "ओके",
    "okay": "ओके",
    "yes": "यस",
    "no": "नो",
    "sure": "श्योर",
    "fine": "फाइन",
    "cool": "कूल",
    "super": "सुपर",
    "ready": "रेडी",
    "start": "स्टार्ट",
    "stop": "स्टॉप",
    "wait": "वेट",
    "relax": "रिलैक्स",
    # Common English / Roman Names inside Hindi Scripts
    "priya": "प्रीया",
    "supriya": "सुप्रीया",
    "riya": "रीया",
    "siya": "सीया",
    "rahul": "राहुल",
    "amit": "अमित",
    "neha": "नेहा",
    "pooja": "पूजा",
    "rohit": "रोहित",
    "vikas": "विकास",
    "gaurav": "गौरव",
    "simran": "सिमरन",
    "anjali": "अंजलि",
    "karan": "करण",
    "arjun": "अर्जुन",
    "raj": "राज",
    "ravi": "रवि",
    "sonia": "सोनिया",
    "mona": "मोना",
    "tina": "टीना",
    "anita": "अनिता",
    "sunita": "सुनीता",
    "geeta": "गीता",
    "seema": "सीमा",
    "rekha": "रेखा",
    "deepak": "दीपक",
    "manoj": "मनोज",
    "sanjay": "संजय",
    "vijay": "विजय",
    "ajay": "अजय",
}


def prepare_reference_audio(audio_path: str, temp_dir: Path) -> str:
    """Converts reference audio to clean 24kHz mono WAV with silence trimmed and loudnorm for optimal XTTS conditioning."""
    src_path = Path(audio_path)
    if not src_path.exists():
        raise FileNotFoundError(f"Reference voice audio file not found: {audio_path}")

    clean_wav = temp_dir / f"clean_ref_{int(time.time() * 1000)}.wav"
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", str(src_path),
        "-af", "silenceremove=start_periods=1:start_duration=0.05:start_threshold=-40dB,areverse,silenceremove=start_periods=1:start_duration=0.05:start_threshold=-40dB,areverse,loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ac", "1",
        "-ar", "24000",
        "-vn",
        str(clean_wav),
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0 and clean_wav.exists():
        return str(clean_wav)
    return str(src_path)


def convert_wav_to_mp3(wav_path: Path, mp3_path: Path):
    """Uses FFmpeg with libmp3lame to convert WAV to clean 192kbps 44.1kHz MP3 for Filmora, trimming dead tail air."""
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", str(wav_path),
        "-af", "areverse,silenceremove=start_periods=1:start_duration=0.08:start_threshold=-45dB,areverse",
        "-codec:a", "libmp3lame",
        "-b:a", "192k",
        "-ar", "44100",
        str(mp3_path),
    ]
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")


def save_emotion_voice(audio_path: str, char_dropdown_val: str, new_char_val: str, emotion_key: str):
    """Saves an emotion recording into ./voices/<character>_<emotion>.wav and refreshes character choices."""
    if char_dropdown_val == NEW_CHAR_OPTION:
        char_name = new_char_val.strip() if new_char_val else ""
    else:
        char_name = char_dropdown_val.strip() if char_dropdown_val else ""

    if not char_name:
        raise gr.Error("Please select an existing Character or type a new Character Name.")
    if not audio_path:
        raise gr.Error("Please record your voice or upload an audio sample first.")

    safe_char = re.sub(r"[^a-zA-Z0-9_-]", "_", char_name.lower())
    safe_emo = emotion_key.strip().lower()
    dest_filename = f"{safe_char}_{safe_emo}.wav"
    dest_path = VOICES_DIR / dest_filename

    # Standardize to 24000Hz mono PCM WAV with silence removal and loudness normalization
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", str(audio_path),
        "-af", "silenceremove=start_periods=1:start_duration=0.05:start_threshold=-40dB,areverse,silenceremove=start_periods=1:start_duration=0.05:start_threshold=-40dB,areverse,loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ac", "1",
        "-ar", "24000",
        "-vn",
        str(dest_path),
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg failed to save voice: {res.stderr}")

    display_char_name = char_name.replace("_", " ").replace("-", " ").strip().title()
    formatted_main_label = format_voice_file_label(dest_filename)

    updated_main_voices = get_available_voices()
    updated_char_choices = get_character_dropdown_choices()
    updated_status = get_character_status_markdown(display_char_name)

    next_emotion = get_next_unrecorded_emotion(display_char_name, safe_emo)
    next_data = EMOTIONS.get(next_emotion, EMOTIONS["neutral"])

    success_msg = (
        f"✅ **Saved '{dest_filename}' successfully!**\n\n"
        f"Character **{display_char_name}** now has the **{EMOTIONS[safe_emo]['title']}** "
        f"emotion ready. It has been automatically selected in the Voice dropdown above!"
    )

    return (
        gr.Dropdown(choices=updated_main_voices, value=formatted_main_label),  # 1. Main voice dropdown
        gr.Dropdown(choices=updated_char_choices, value=display_char_name),    # 2. Character dropdown
        gr.Textbox(visible=False, value=display_char_name),                   # 3. New character textbox
        updated_status,                                                       # 4. Status badges
        gr.Dropdown(choices=EMOTION_CHOICES, value=next_emotion),             # 5. Emotion selector auto-advances
        next_data["tip"],                                                     # 6. Vocal coach tip for next emotion
        next_data["hindi"],                                                   # 7. Hindi script for next emotion
        next_data["english"],                                                 # 8. English script for next emotion
        success_msg,                                                          # 9. Success banner
        None,                                                                 # 10. Clear audio recorder
    )


# Root Hindi verbs that must preserve their native spelling
PROTECTED_HINDI_VERBS = {"किया", "दिया", "लिया", "पिया", "जिया", "सिया"}


def preprocess_script_text(text: str, lang_code: str) -> str:
    """Comprehensive linguistic & phonetic pre-processing engine:
    1. Strips invisible formatting & zero-width noise (ZWJ, ZWNJ, BOM).
    2. Transliterates common English / Hinglish loanwords into clean Devanagari.
    3. Normalizes Hindi numerals, fractions, decimals, clock times, percentages, and currencies.
    4. Resolves BPE tokenization pitfalls for ALL Devanagari conjuncts & names (प्रिया -> प्रीया, शुक्रिया -> शुक्रीया).
    5. Resolves greedy matra collapse on feminine plurals (कहानियां -> कहानीयां, गाड़ियां -> गाड़ीयां, रोटियां -> रोटीयां).
    6. Normalizes Chandrabindu (ँ) to Anusvara (ं) to leverage fused subwords (हँसना -> हंसना).
    7. Cleans unhandled Nukta characters and Visarga breaks (दुःख -> दुख, स्वतः -> स्वत).
    8. Unifies hyphens in reduplicated words (गरमा-गरम -> गरमा गरम, धीरे-धीरे -> धीरे धीरे).
    9. Ensures clean punctuation spacing for breath-aligned sentence segmentation.
    """
    text = text.strip()

    if lang_code == "hi":
        # 1. Strip invisible Unicode junk (ZWJ, ZWNJ, ZWSP, BOM, soft hyphen)
        text = re.sub(r"[\u200b-\u200f\ufeff\u00ad]", "", text)

        # 2. Convert Devanagari numerals (०-९) to standard digits (0-9)
        text = text.translate(str.maketrans("०१२३४५६७८९", "0123456789"))

        # 3. Transliterate English loanwords into clean Devanagari
        for en_word, hi_word in HINDI_LOANWORDS.items():
            text = re.sub(rf"\b{re.escape(en_word)}\b", hi_word, text, flags=re.IGNORECASE)

        # 4. Clock / Time format (e.g., '1:30' or '10:00 बजे' -> 'एक बजकर तीस मिनट' / 'दस बजे')
        def _time_repl(m):
            hr, mn = int(m.group(1)), int(m.group(2))
            if mn == 0:
                return f"{hindi_num2words(hr)} बजे "
            return f"{hindi_num2words(hr)} बजकर {hindi_num2words(mn)} मिनट "
        text = re.sub(r"\b(\d{1,2}):(\d{2})(?:\s*बजे)?", _time_repl, text)

        # 5. Common fractions & decimals
        text = re.sub(r"\b1/2\b", "आधा", text)
        text = re.sub(r"\b1/4\b", "एक चौथाई", text)
        text = re.sub(r"\b3/4\b", "तीन चौथाई", text)
        text = re.sub(r"\b1\.5\b", "डेढ़", text)
        text = re.sub(r"\b2\.5\b", "ढाई", text)

        # 6. Currency symbols and percentages
        text = re.sub(r"₹\s*(\d+)", r"\1 रुपये", text)
        text = re.sub(r"\$\s*(\d+)", r"\1 डॉलर", text)
        text = re.sub(r"(\d+)\s*%", r"\1 प्रतिशत", text)

        # 7. Pre-expand standalone numbers into spoken Hindi words
        def _replace_num(match):
            try:
                return hindi_num2words(int(match.group(0)))
            except Exception:
                return match.group(0)
        text = re.sub(r"\b\d+\b", _replace_num, text)

        # 8. Chandrabindu (ँ) to Anusvara (ं) - enables XTTS pre-fused subwords (हँसना -> हंसना, गाँव -> गांव)
        text = text.replace("ँ", "ं")

        # 9. Visarga (ः) cleanup - avoids mid-word tokenization breaks (दुःख -> दुख, स्वतः -> स्वत)
        text = text.replace("दुःख", "दुख").replace("दु:ख", "दुख")
        text = re.sub(r"([क-ह])ः", r"\1", text)

        # 10. Nukta normalization for characters that lack native pre-fused subwords in XTTS
        text = re.sub(r"क़", "क", text)
        text = re.sub(r"ख़", "ख", text)
        text = re.sub(r"ग़", "ग", text)
        text = re.sub(r"ज़ि", "जि", text)
        text = re.sub(r"फ़ि", "फि", text)
        text = re.sub(r"([क-ह])ाफ़\b", r"\1ाफ", text)

        # 11. Hyphens between Devanagari reduplicated words (धीरे-धीरे -> धीरे धीरे, गरमा-गरम -> गरमा गरम)
        text = re.sub(r"([क-ह]़?[\u093e-\u094c]?)-([क-ह])", r"\1 \2", text)

        # 12. Universal 'िया' / 'ियों' / 'ियां' / 'िए' normalization
        # Resolves tokenization breaks across names, conjuncts and feminine plurals
        def _iya_repl(m):
            full = m.group(0)
            if full in PROTECTED_HINDI_VERBS:
                return full
            prefix = m.group(1)
            suffix = m.group(2)
            return prefix + "ी" + suffix

        iya_pattern = r"([क-ह]़?(?:्[क-ह]़?)*)ि(य[ाोे][ंँ]?)"
        text = re.sub(iya_pattern, _iya_repl, text)

        # 13. Dramatic pause normalization (... or -- to clean clause boundaries)
        text = re.sub(r"\.{3,}", "। ", text)
        text = re.sub(r"--+", ", ", text)
        text = text.replace("॥", "।")

        # 14. Ensure sentence terminators have trailing spaces for clean sentence segmentation
        text = re.sub(r"([।!?])([^\s])", r"\1 \2", text)
        text = re.sub(r"(\.)([^\s\d])", r"\1 \2", text)

        # 15. Collapse excessive whitespace
        text = re.sub(r"\s+", " ", text).strip()

    else:
        # English text cleaning
        text = re.sub(r"[\u200b-\u200f\ufeff\u00ad]", "", text)
        text = re.sub(r"\$\s*(\d+)", r"\1 dollars", text)
        text = re.sub(r"(\d+)\s*%", r"\1 percent", text)
        text = re.sub(r"\.{3,}", ". ", text)
        text = re.sub(r"--+", ", ", text)
        text = re.sub(r"\s+", " ", text).strip()

    return text


def generate_voiceover(script_text, voice_choice, custom_upload, language_label, speed):
    if not script_text or not script_text.strip():
        raise gr.Error("Please paste your script text before generating.")
    if not voice_choice:
        raise gr.Error("Please select a character voice.")

    lang_code = "hi" if "Hindi" in language_label else "en"
    processed_text = preprocess_script_text(script_text, lang_code)
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    # Extract clean file prefix
    safe_prefix = re.sub(r"[^a-zA-Z0-9_-]", "_", voice_choice.split("[")[0].strip())[:25]
    temp_wav = OUTPUTS_DIR / f"temp_{timestamp}.wav"
    final_mp3 = OUTPUTS_DIR / f"{safe_prefix}_{timestamp}.mp3"

    with tempfile.TemporaryDirectory() as temp_work_dir:
        temp_dir_path = Path(temp_work_dir)
        speaker_wav = None
        speaker_name = None

        if "[" in voice_choice and voice_choice.endswith("]"):
            # Custom saved character voice with emotion
            match = re.search(r"\[(.*?)\]", voice_choice)
            if match:
                ref_file = VOICES_DIR / match.group(1).strip()
                if ref_file.exists():
                    speaker_wav = prepare_reference_audio(str(ref_file), temp_dir_path)
        elif voice_choice.startswith("Custom Clone: "):
            filename = voice_choice.replace("Custom Clone: ", "").strip()
            ref_file = VOICES_DIR / filename
            if ref_file.exists():
                speaker_wav = prepare_reference_audio(str(ref_file), temp_dir_path)
        elif "Preset:" in voice_choice:
            clean_preset = voice_choice.replace("🎙️ Preset: ", "").strip()
            speaker_name = PRESET_VOICES.get(clean_preset, "Damien Black")
        elif custom_upload is not None:
            speaker_wav = prepare_reference_audio(custom_upload, temp_dir_path)
        else:
            speaker_name = "Damien Black"

        print(f"Generating audio for language: {lang_code}, voice: {voice_choice}, speed: {speed}...")
        start_time = time.time()

        # Split into sentences for clean breathing and alignment
        sentences = tts.synthesizer.split_into_sentences(processed_text, lang_code)
        sentences = [s.strip() for s in sentences if s and s.strip()]
        if not sentences:
            sentences = [processed_text]

        sr = 24000
        # 280ms breath pause between sentences for realistic storytelling cadence
        pause_samples = int(sr * 0.28)
        pause_array = np.zeros(pause_samples, dtype=np.float32)

        def trim_tail_silence(raw_wav, thresh=0.015, pad_ms=60):
            arr = np.array(raw_wav, dtype=np.float32)
            active = np.where(np.abs(arr) > thresh)[0]
            if len(active) > 0:
                end = min(len(arr), active[-1] + int(sr * pad_ms / 1000))
                return arr[:end]
            return arr

        combined_audio = []
        for idx, sen in enumerate(sentences):
            if speaker_wav:
                wav_chunk = tts.tts(
                    text=sen,
                    speaker_wav=speaker_wav,
                    language=lang_code,
                    speed=float(speed),
                    split_sentences=False,
                )
            else:
                wav_chunk = tts.tts(
                    text=sen,
                    speaker=speaker_name,
                    language=lang_code,
                    speed=float(speed),
                    split_sentences=False,
                )

            trimmed_chunk = trim_tail_silence(wav_chunk)
            combined_audio.append(trimmed_chunk)
            if idx < len(sentences) - 1:
                combined_audio.append(pause_array)

        full_waveform = np.concatenate(combined_audio)
        sf.write(str(temp_wav), full_waveform, sr)

        duration = time.time() - start_time
        print(f"Synthesis completed in {duration:.1f}s. Converting to Filmora MP3...")

    # Convert to Filmora-ready 192kbps MP3
    convert_wav_to_mp3(temp_wav, final_mp3)
    if temp_wav.exists():
        temp_wav.unlink()

    return str(final_mp3), str(final_mp3), f"✅ Generated in {duration:.1f}s | Saved: {final_mp3.name}"


# ---------------------------------------------------------
# 3. Gradio Web Interface (Optimized Tailwind Slate / Sky Design)
# ---------------------------------------------------------
existing_characters = get_existing_characters()
init_char_choices = get_character_dropdown_choices()
init_char_value = existing_characters[0] if existing_characters else NEW_CHAR_OPTION
init_new_char_visible = (init_char_value == NEW_CHAR_OPTION)

if existing_characters:
    init_emotion = get_next_unrecorded_emotion(existing_characters[0], "neutral")
else:
    init_emotion = "neutral"

init_emotion_data = EMOTIONS[init_emotion]

CUSTOM_CSS = """
/* Calm Tailwind Slate & Sky Theme */
.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto !important;
    padding-top: 1rem !important;
}

/* Header subtle card */
.header-card {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 18px 24px;
    margin-bottom: 20px;
}

/* Dedicated Voice Studio Drawer */
.studio-drawer {
    background: #0f172a !important;
    border: 1px solid #38bdf8 !important;
    border-radius: 14px !important;
    padding: 22px !important;
    margin-top: 14px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 10px 30px -5px rgba(2, 132, 199, 0.15) !important;
}

/* Button hover polish */
button.primary {
    background: #0284c7 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
}
button.primary:hover {
    background: #0369a1 !important;
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

with gr.Blocks(title="Local Voice Studio") as demo:
    # Top Minimalist Header
    with gr.Column(elem_classes=["header-card"]):
        gr.Markdown(
            "# 🎙️ Local Multi-Character Voice Studio\n"
            "Generate Hindi & English storytelling dialogue with realistic character emotions and export **192kbps MP3s directly for Filmora**."
        )

    # State tracking whether the Voice Studio drawer is open or closed
    studio_is_open = gr.State(False)

    with gr.Row():
        # LEFT COLUMN: Clean Homepage Text-to-Speech Core
        with gr.Column(scale=3):
            script_input = gr.Textbox(
                label="Scene Script / Dialogue (कहानी या संवाद)",
                placeholder="यहाँ अपनी कहानी या संवाद पेस्ट करें... (Paste your Hindi or English dialogue here)",
                lines=6,
            )

            with gr.Row():
                voice_dropdown = gr.Dropdown(
                    choices=get_available_voices(),
                    value=get_available_voices()[0] if get_available_voices() else None,
                    label="Character Voice & Emotion (पात्र और भाव चुनें)",
                    scale=4,
                )
                refresh_btn = gr.Button("🔄 Refresh", scale=1, variant="secondary", size="sm")
                toggle_studio_btn = gr.Button("🎙️ Clone / Add Voice", scale=2, variant="secondary", size="sm")

            with gr.Row():
                lang_radio = gr.Radio(
                    choices=["Hindi (hi)", "English (en)"],
                    value="Hindi (hi)",
                    label="Spoken Language",
                    scale=2,
                )
                speed_slider = gr.Slider(
                    minimum=0.50,
                    maximum=3.00,
                    value=1.0,
                    step=0.05,
                    label="Speaking Speed",
                    scale=3,
                )

            # Core Homepage Action Button
            generate_btn = gr.Button("🚀 Generate MP3 Audio for Filmora", variant="primary", size="lg")

            # --- DEDICATED SEPARATE VOICE CLONING & EMOTION STUDIO DRAWER ---
            # Kept separate and opened on demand via the '🎙️ Clone / Add Voice' button
            with gr.Column(visible=False, elem_classes=["studio-drawer"]) as studio_drawer:
                with gr.Row():
                    gr.Markdown("### 🎭 Character Emotion Studio (Record & Save Custom Voice)")
                    close_studio_btn = gr.Button("✕ Close Studio", variant="secondary", size="sm", scale=0)

                gr.Markdown(
                    "Select or create your character below, pick an emotion, and read the prompt into the microphone for 10–15s."
                )

                with gr.Row():
                    char_dropdown = gr.Dropdown(
                        choices=init_char_choices,
                        value=init_char_value,
                        label="1. Select Character (पात्र चुनें)",
                        scale=3,
                    )
                    new_char_input = gr.Textbox(
                        label="New Character Name (नया पात्र नाम)",
                        placeholder="e.g. Gaurav, Mohan, Villain, Dadi Ji",
                        visible=init_new_char_visible,
                        scale=2,
                    )
                    emotion_selector = gr.Dropdown(
                        choices=EMOTION_CHOICES,
                        value=init_emotion,
                        label="2. Choose Emotion to Record (भाव चुनें)",
                        scale=3,
                    )

                # Character Emotion Status Badges
                status_badges_box = gr.Markdown(
                    get_character_status_markdown(init_char_value)
                    if init_char_value != NEW_CHAR_OPTION
                    else "💡 *Type a new Character Name above to start creating your character profile.*"
                )

                # Vocal Coach Advice
                vocal_coach_tip = gr.Markdown(init_emotion_data["tip"])

                with gr.Tab("🇮🇳 Hindi Acting Prompt (हिंदी में यह बोलें)"):
                    hindi_prompt_box = gr.Textbox(
                        value=init_emotion_data["hindi"],
                        label="Read this emotionally into the microphone (10–15 seconds):",
                        lines=3,
                        interactive=False,
                    )

                with gr.Tab("🇬🇧 English Acting Prompt (English Script)"):
                    english_prompt_box = gr.Textbox(
                        value=init_emotion_data["english"],
                        label="Read this emotionally into the microphone (10–15 seconds):",
                        lines=3,
                        interactive=False,
                    )

                # Audio Recorder
                audio_recorder = gr.Audio(
                    sources=["microphone", "upload"],
                    type="filepath",
                    label="3. Record or Upload Audio Sample (10–20 sec)",
                )

                with gr.Row():
                    save_emotion_btn = gr.Button("💾 Save This Emotion to Character Profile", variant="primary", scale=2)
                    done_and_close_btn = gr.Button("✨ Done & Return to Studio", variant="secondary", scale=1)

                save_feedback = gr.Markdown("")

        # RIGHT COLUMN: Audio Player, Direct Download & Tips
        with gr.Column(scale=2):
            gr.Markdown("### 🎧 Voiceover Preview & Filmora Export")
            audio_player = gr.Audio(label="Preview Audio", type="filepath")
            download_file = gr.File(label="Download 192kbps MP3 for Filmora")
            status_box = gr.Textbox(label="Status / Generation Log", interactive=False, lines=2)

            gr.Markdown(
                """
                ---
                ### 🎬 Filmora Timeline Storytelling Tips:
                1. **Pick Character & Emotion**: Select your character and the matching emotion in the dropdown.
                2. **Dialogue Transitions**: Generate dialogues beat-by-beat to create authentic emotional transitions.
                3. **Direct Drag**: All audio is saved into `./outputs/` as clean **192kbps MP3s**. Drag them straight into your Filmora timeline!
                """
            )

    # --- EVENT BINDINGS ---
    def toggle_studio(is_open):
        new_state = not is_open
        btn_text = "✕ Close Voice Studio" if new_state else "🎙️ Clone / Add Voice"
        return gr.update(visible=new_state), btn_text, new_state

    def close_studio():
        return gr.update(visible=False), "🎙️ Clone / Add Voice", False

    toggle_studio_btn.click(
        fn=toggle_studio,
        inputs=studio_is_open,
        outputs=[studio_drawer, toggle_studio_btn, studio_is_open],
    )

    close_studio_btn.click(
        fn=close_studio,
        outputs=[studio_drawer, toggle_studio_btn, studio_is_open],
    )

    done_and_close_btn.click(
        fn=close_studio,
        outputs=[studio_drawer, toggle_studio_btn, studio_is_open],
    )

    def on_emotion_change(emo_key):
        data = EMOTIONS.get(emo_key, EMOTIONS["neutral"])
        return data["tip"], data["hindi"], data["english"]

    def on_char_dropdown_change(selected_char):
        if selected_char == NEW_CHAR_OPTION:
            badges = "💡 *Type a new Character Name in the box, then record their first emotion below.*"
            neutral_data = EMOTIONS["neutral"]
            return (
                gr.Textbox(visible=True, value=""),
                badges,
                gr.Dropdown(choices=EMOTION_CHOICES, value="neutral"),
                neutral_data["tip"],
                neutral_data["hindi"],
                neutral_data["english"],
            )
        else:
            badges = get_character_status_markdown(selected_char)
            next_emo = get_next_unrecorded_emotion(selected_char, "neutral")
            emo_data = EMOTIONS.get(next_emo, EMOTIONS["neutral"])
            return (
                gr.Textbox(visible=False, value=selected_char),
                badges,
                gr.Dropdown(choices=EMOTION_CHOICES, value=next_emo),
                emo_data["tip"],
                emo_data["hindi"],
                emo_data["english"],
            )

    def on_new_char_text_change(typed_name):
        if not typed_name or not typed_name.strip():
            return "💡 *Type a new Character Name above to start creating your character profile.*"
        return get_character_status_markdown(typed_name)

    emotion_selector.change(
        fn=on_emotion_change,
        inputs=emotion_selector,
        outputs=[vocal_coach_tip, hindi_prompt_box, english_prompt_box],
    )

    char_dropdown.change(
        fn=on_char_dropdown_change,
        inputs=char_dropdown,
        outputs=[new_char_input, status_badges_box, emotion_selector, vocal_coach_tip, hindi_prompt_box, english_prompt_box],
    )

    new_char_input.change(
        fn=on_new_char_text_change,
        inputs=new_char_input,
        outputs=status_badges_box,
    )

    save_emotion_btn.click(
        fn=save_emotion_voice,
        inputs=[audio_recorder, char_dropdown, new_char_input, emotion_selector],
        outputs=[
            voice_dropdown,
            char_dropdown,
            new_char_input,
            status_badges_box,
            emotion_selector,
            vocal_coach_tip,
            hindi_prompt_box,
            english_prompt_box,
            save_feedback,
            audio_recorder,
        ],
    )

    refresh_btn.click(
        fn=lambda: gr.Dropdown(choices=get_available_voices()),
        outputs=voice_dropdown,
    )

    generate_btn.click(
        fn=generate_voiceover,
        inputs=[script_input, voice_dropdown, audio_recorder, lang_radio, speed_slider],
        outputs=[audio_player, download_file, status_box],
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, inbrowser=True, theme=TAILWIND_THEME, css=CUSTOM_CSS)
