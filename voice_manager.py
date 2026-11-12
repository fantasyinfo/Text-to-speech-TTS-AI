import re
import subprocess
from pathlib import Path
import gradio as gr

from config import (
    VOICES_DIR,
    EMOTIONS,
    EMOTION_CHOICES,
    NEW_CHAR_OPTION,
    PRESET_VOICES,
    FFMPEG_BIN,
)


def get_existing_characters() -> list[str]:
    """Extracts unique character names from voices/ folder."""
    VOICES_DIR.mkdir(parents=True, exist_ok=True)
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


def get_character_dropdown_choices() -> list[str]:
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


def get_available_voices() -> list[str]:
    """Combines custom emotion voice files with built-in studio presets, grouped by character."""
    VOICES_DIR.mkdir(parents=True, exist_ok=True)
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

