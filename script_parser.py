"""
Script Parser for Multi-Scene, Multi-Emotion Dialogue & Storytelling
Parses bracketed script cues like:
  [Narrator – Calm, descriptive, storytelling]
  दोपहर का 1 बजा है। प्रिया की desk पर मम्मी का बनाया गरमागरम टिफिन रखा है।

  [Curious, suspenseful]
  लेकिन तभी उसके फोन पर एक notification आया...
"""

import re
from typing import List, Dict, Any, Optional
import config

# Common emotion synonyms and colloquial director cue mappings
SYNONYMS = {
    # Storytelling & Delivery
    "narrator": "storytelling",
    "narration": "storytelling",
    "descriptive": "storytelling",
    "storytelling": "storytelling",
    "conversational": "conversational",
    "reflective": "reflective",
    "inspirational": "inspirational",
    "urgent": "urgent",
    "secretive": "secretive",
    "emotional": "emotional",
    "serious": "serious",
    "laughing": "laughing",
    "crying": "crying",
    "shouting": "shouting",
    "whispering": "whispering",
    "suspenseful": "suspenseful",
    "dramatic": "dramatic",
    # Calm & Peace
    "calm": "calm",
    "peaceful": "peaceful",
    "relaxed": "relaxed",
    "serene": "serene",
    "patient": "patient",
    "content": "content",
    "meditative": "meditative",
    "casual": "relaxed",
    "careless": "relaxed",
    "chill": "relaxed",
    # Curiosity & Suspense
    "curious": "curious",
    "suspense": "suspenseful",
    "intrigued": "intrigued",
    "interested": "interested",
    "inquisitive": "inquisitive",
    "wondering": "wondering",
    "skeptical": "skeptical",
    "investigative": "investigative",
    # Happiness & Energy
    "happy": "happy",
    "joyful": "joyful",
    "excited": "excited",
    "delighted": "delighted",
    "amused": "amused",
    "playful": "playful",
    "proud": "proud",
    "hopeful": "hopeful",
    "grateful": "grateful",
    "relieved": "relieved",
    "promotional": "motivational",
    "energetic": "excited",
    "upbeat": "happy",
    # Sadness
    "sad": "sad",
    "heartbroken": "heartbroken",
    "disappointed": "disappointed",
    "lonely": "lonely",
    "hurt": "hurt",
    "melancholic": "melancholic",
    "grief": "grief_stricken",
    "tearful": "tearful",
    "regretful": "regretful",
    # Anger
    "angry": "angry",
    "furious": "furious",
    "irritated": "irritated",
    "frustrated": "frustrated",
    "annoyed": "annoyed",
    "resentful": "resentful",
    "sarcastic": "sarcastic",
    "indignant": "indignant",
    # Fear & Tension
    "afraid": "afraid",
    "terrified": "terrified",
    "scared": "scared",
    "anxious": "anxious",
    "nervous": "nervous",
    "panicked": "panicked",
    "suspicious": "suspicious",
    "cautious": "cautious",
    # Surprise & Shock
    "surprised": "surprised",
    "shocked": "shocked",
    "astonished": "astonished",
    "amazed": "amazed",
    "stunned": "stunned",
    "confused": "confused",
    "bewildered": "bewildered",
    # Confidence
    "confident": "confident",
    "assertive": "assertive",
    "authoritative": "authoritative",
    "determined": "determined",
    "motivational": "motivational",
    "persuasive": "persuasive",
}


def match_emotion(emotion_raw: str, fallback: str = "storytelling") -> str:
    """Intelligently matches a raw emotion/tone descriptor string against our 121 delivery styles."""
    if not emotion_raw or not emotion_raw.strip():
        return fallback

    emotions = config.EMOTIONS
    clean_raw = emotion_raw.lower().replace(",", " ").replace(";", " ").replace("/", " ").replace("-", " ")
    words = [w.strip() for w in clean_raw.split() if w.strip()]

    # 1. Exact match in EMOTIONS catalog keys
    for w in words:
        if w in emotions:
            return w

    # 2. Check synonyms dictionary
    for w in words:
        if w in SYNONYMS and SYNONYMS[w] in emotions:
            return SYNONYMS[w]

    # 3. Check for multi-word or compound matches (e.g. 'grief-stricken', 'sarcastic humor')
    for emo_key, data in emotions.items():
        title = data.get("title", "").lower()
        if title and title in clean_raw:
            return emo_key
        if emo_key.replace("_", " ") in clean_raw:
            return emo_key

    # 4. Partial substring match in emotion keys
    for w in words:
        if len(w) >= 4:
            for emo_key in emotions:
                if w in emo_key:
                    return emo_key

    return fallback


def match_speaker(speaker_raw: Optional[str], available_voices: List[str], default_voice: str) -> str:
    """Matches a character name from cue tag (e.g. 'Narrator', 'Priya', 'Mohan') against available voices."""
    if not speaker_raw or not speaker_raw.strip():
        return default_voice

    clean_spk = speaker_raw.strip().lower()

    # Exact or substring match in available_voices
    for v in available_voices:
        v_lower = v.lower()
        if clean_spk in v_lower:
            return v

    # Check for 'Narrator' keyword
    if clean_spk in {"narrator", "narrator voice", "storyteller", "sutradhar", "सूत्रधार"}:
        for v in available_voices:
            if "storyteller" in v.lower() or "narrative" in v.lower():
                return v

    return default_voice


def has_bracket_scenes(text: str) -> bool:
    """Checks if the script text contains bracketed scene tags like [Narrator – Calm]."""
    if not text:
        return False
    return bool(re.search(r"\[([^\]]+)\]\s*([^\[]+)", text))


def has_bracketScenes(text: str) -> bool:
    """Alias for camelCase compatibility."""
    return has_bracket_scenes(text)


def parse_script_to_scenes(
    script_text: str,
    default_voice: str = "",
    default_emotion: str = "storytelling",
    available_voices: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Parses a script containing bracketed cues like [Narrator – Calm] into structured scene objects.
    If no brackets exist, returns a single scene object with full text.
    """
    if not script_text or not script_text.strip():
        return []

    available_voices = available_voices or []
    pattern = r"\[([^\]]+)\]\s*([^\[]+)"
    matches = list(re.finditer(pattern, script_text, re.DOTALL))

    if not matches:
        # Fallback: Single scene without brackets
        return [
            {
                "index": 1,
                "scene_title": "Scene 01",
                "speaker_raw": "",
                "emotion_raw": default_emotion,
                "voice": default_voice,
                "emotion": default_emotion,
                "text": script_text.strip(),
            }
        ]

    scenes = []
    current_voice = default_voice

    for idx, match in enumerate(matches):
        tag = match.group(1).strip()
        content = match.group(2).strip()
        if not content:
            continue

        speaker = None
        emotion_str = tag

        # Check for separators like '–', '—', '-', ':'
        for sep in ["–", "—", "-", ":"]:
            if sep in tag:
                parts = tag.split(sep, 1)
                potential_speaker = parts[0].strip()
                potential_emotion = parts[1].strip()
                # Ensure potential_speaker is not just an emotion word
                if len(potential_speaker) > 0 and len(potential_emotion) > 0:
                    speaker = potential_speaker
                    emotion_str = potential_emotion
                    break

        matched_emotion = match_emotion(emotion_str, fallback=default_emotion)

        if speaker:
            scene_voice = match_speaker(speaker, available_voices, default_voice)
            current_voice = scene_voice
        else:
            scene_voice = current_voice or default_voice

        scenes.append(
            {
                "index": idx + 1,
                "scene_title": f"Scene {idx + 1:02d}",
                "speaker_raw": speaker or "",
                "emotion_raw": emotion_str,
                "voice": scene_voice,
                "emotion": matched_emotion,
                "text": content,
            }
        )

    return scenes


def format_scenes_to_script(scenes: List[Dict[str, Any]]) -> str:
    """Rebuilds the bracketed script text from an array of structured scene objects."""
    blocks = []
    for sc in scenes:
        spk = sc.get("speaker_raw") or sc.get("voice", "").split("[")[0].replace("🎭 Custom:", "").replace("🎙️ Preset:", "").strip()
        emo = sc.get("emotion") or sc.get("emotion_raw") or "storytelling"
        text = sc.get("text", "").strip()

        if spk and spk.lower() not in {"damien black", "default"}:
            header = f"[{spk} – {emo.replace('_', ' ').title()}]"
        else:
            header = f"[{emo.replace('_', ' ').title()}]"

        blocks.append(f"{header}\n{text}")

    return "\n\n".join(blocks)
