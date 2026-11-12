import os
import re
import sys
import time
import shutil
import tempfile
import subprocess
from pathlib import Path
import gradio as gr

# Automatically acknowledge Coqui CPML terms for non-interactive / automated environments
os.environ["COQUI_TOC_ACK"] = "1"
os.environ["COQUI_TOS_AGREED"] = "1"

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
    header = f"### 🎭 Character: **{display_title}** ({recorded_count}/{len(EMOTIONS)} emotions ready)\n\n"
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


def prepare_reference_audio(audio_path: str, temp_dir: Path) -> str:
    """Converts reference audio to clean 24kHz mono WAV for XTTS conditioning."""
    src_path = Path(audio_path)
    if not src_path.exists():
        raise FileNotFoundError(f"Reference voice audio file not found: {audio_path}")

    clean_wav = temp_dir / f"clean_ref_{int(time.time() * 1000)}.wav"
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", str(src_path),
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
    """Uses FFmpeg with libmp3lame to convert WAV to clean 192kbps 44.1kHz MP3 for Filmora."""
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", str(wav_path),
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
    # Resolve character name
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

    # Standardize to 24000Hz mono PCM WAV via FFmpeg
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", str(audio_path),
        "-ac", "1",
        "-ar", "24000",
        "-vn",
        str(dest_path),
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg failed to save voice: {res.stderr}")

    # Format names for UI
    display_char_name = char_name.replace("_", " ").replace("-", " ").strip().title()
    formatted_main_label = format_voice_file_label(dest_filename)

    # Refresh dropdown choices
    updated_main_voices = get_available_voices()
    updated_char_choices = get_character_dropdown_choices()
    updated_status = get_character_status_markdown(display_char_name)

    # Auto-advance to the next unrecorded emotion
    next_emotion = get_next_unrecorded_emotion(display_char_name, safe_emo)
    next_data = EMOTIONS.get(next_emotion, EMOTIONS["neutral"])

    success_msg = (
        f"✅ **Saved successfully!** File: `voices/{dest_filename}`\n\n"
        f"Character **{display_char_name}** now has the **{EMOTIONS[safe_emo]['title']}** "
        f"emotion ready. It has been automatically selected in the Voice Type dropdown above!"
    )

    return (
        gr.Dropdown(choices=updated_main_voices, value=formatted_main_label),  # 1. Main voice dropdown
        gr.Dropdown(choices=updated_char_choices, value=display_char_name),    # 2. Character dropdown (locks to character)
        gr.Textbox(visible=False, value=display_char_name),                   # 3. New character textbox (hidden)
        updated_status,                                                       # 4. Status badges
        gr.Dropdown(choices=EMOTION_CHOICES, value=next_emotion),             # 5. Emotion selector auto-advances
        next_data["tip"],                                                     # 6. Vocal coach tip for next emotion
        next_data["hindi"],                                                   # 7. Hindi script for next emotion
        next_data["english"],                                                 # 8. English script for next emotion
        success_msg,                                                          # 9. Success banner
        None,                                                                 # 10. Clear audio recorder for next take
    )


def generate_voiceover(script_text, voice_choice, custom_upload, language_label, speed):
    if not script_text or not script_text.strip():
        raise gr.Error("Please paste your script text before generating.")
    if not voice_choice:
        raise gr.Error("Please select a character voice.")

    lang_code = "hi" if "Hindi" in language_label else "en"
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

        # Synthesize speech via XTTS-v2
        if speaker_wav:
            tts.tts_to_file(
                text=script_text.strip(),
                speaker_wav=speaker_wav,
                language=lang_code,
                speed=float(speed),
                file_path=str(temp_wav),
            )
        else:
            tts.tts_to_file(
                text=script_text.strip(),
                speaker=speaker_name,
                language=lang_code,
                speed=float(speed),
                file_path=str(temp_wav),
            )

        duration = time.time() - start_time
        print(f"Synthesis completed in {duration:.1f}s. Converting to MP3...")

    # Convert to Filmora-ready 192kbps MP3
    convert_wav_to_mp3(temp_wav, final_mp3)
    if temp_wav.exists():
        temp_wav.unlink()

    return str(final_mp3), str(final_mp3), f"✅ Generated in {duration:.1f}s | Saved: {final_mp3.name}"


# ---------------------------------------------------------
# 3. Gradio Web Interface
# ---------------------------------------------------------
existing_characters = get_existing_characters()
init_char_choices = get_character_dropdown_choices()
init_char_value = existing_characters[0] if existing_characters else NEW_CHAR_OPTION
init_new_char_visible = (init_char_value == NEW_CHAR_OPTION)

# Determine initial emotion
if existing_characters:
    init_emotion = get_next_unrecorded_emotion(existing_characters[0], "neutral")
else:
    init_emotion = "neutral"

init_emotion_data = EMOTIONS[init_emotion]

with gr.Blocks(title="Local Voice Studio") as demo:
    gr.Markdown("# 🎙️ Local Multi-Character Voice Studio (macOS Apple Silicon)")
    gr.Markdown(
        "Generate realistic multi-character voiceovers with **10 distinct emotions** (Sad, Crying, Laughing, "
        "Angry, Scared, Tired, Excited, etc.) and export **192kbps MP3s ready for Filmora**."
    )

    with gr.Row():
        # LEFT COLUMN: Main Controls & Recording Studio
        with gr.Column(scale=3):
            script_input = gr.Textbox(
                label="Scene Script / Dialogue (कहानी या संवाद)",
                placeholder="यहाँ अपनी कहानी या संवाद पेस्ट करें... (Paste your Hindi or English scene script here)",
                lines=7,
            )

            with gr.Row():
                voice_dropdown = gr.Dropdown(
                    choices=get_available_voices(),
                    value=get_available_voices()[0] if get_available_voices() else None,
                    label="Select Character Voice & Emotion (पात्र और भाव चुनें)",
                    scale=3,
                )
                refresh_btn = gr.Button("🔄 Refresh Voices", scale=1)

            with gr.Row():
                lang_radio = gr.Radio(
                    choices=["Hindi (hi)", "English (en)"],
                    value="Hindi (hi)",
                    label="Spoken Language",
                )
                speed_slider = gr.Slider(
                    minimum=0.75,
                    maximum=1.30,
                    value=1.0,
                    step=0.05,
                    label="Speaking Speed",
                )

            # --- MULTI-EMOTION CHARACTER VOICE STUDIO ---
            with gr.Accordion("🎭 Character Emotion Voice Studio (Record & Align Realistic Emotions)", open=True):
                gr.Markdown(
                    "### 💡 Why Record Separate Emotions?\n"
                    "In storytelling, human voices change drastically when **crying**, **angry**, **laughing**, or **tired**. "
                    "Select your character below, record each emotion once, and your character will sound authentic in every scene!"
                )

                with gr.Row():
                    char_dropdown = gr.Dropdown(
                        choices=init_char_choices,
                        value=init_char_value,
                        label="1. Select Character (पात्र चुनें)",
                        scale=2,
                    )
                    new_char_input = gr.Textbox(
                        label="New Character Name (नया पात्र नाम)",
                        placeholder="e.g. Gaurav, Mohan, Villain, Dadi Ji",
                        visible=init_new_char_visible,
                        scale=2,
                    )
                    emotion_selector = gr.Dropdown(
                        choices=[(data["badge"], key) for key, data in EMOTIONS.items()],
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

                # Vocal Coach Tip & Prompts Card
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

                save_emotion_btn = gr.Button("💾 Save This Emotion to Character Profile", variant="secondary", size="lg")
                save_feedback = gr.Markdown("")

            generate_btn = gr.Button("🚀 Generate MP3 Audio for Filmora", variant="primary", size="lg")

        # RIGHT COLUMN: Audio Player & Timeline Export
        with gr.Column(scale=2):
            gr.Markdown("### 🎧 Voiceover Preview & Filmora Export")
            audio_player = gr.Audio(label="Preview Audio", type="filepath")
            download_file = gr.File(label="Download 192kbps MP3 for Filmora")
            status_box = gr.Textbox(label="Status / Generation Log", interactive=False, lines=3)

            gr.Markdown(
                """
                ---
                ### 🎬 Filmora Timeline Storytelling Tips:
                1. **Pick Character & Emotion**: In the dropdown above, select your character with the matching emotion (e.g. `Gaurav — Crying & Choked`).
                2. **Dialogue Transitions**: Generate dialogues line-by-line. They will keep the same voice identity with scene-appropriate emotion!
                3. **Direct Drag**: All audio is saved into `./outputs/` as high-grade **192kbps MP3s**. Drag them straight into your Filmora timeline!
                """
            )

    # --- EVENT BINDINGS ---
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
    demo.launch(server_name="127.0.0.1", server_port=7860, inbrowser=True, theme=gr.themes.Soft())
