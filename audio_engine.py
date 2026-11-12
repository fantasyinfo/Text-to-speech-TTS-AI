import os
import re
import time
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
import soundfile as sf
import torch
import gradio as gr
from TTS.api import TTS

from config import VOICES_DIR, PRESET_VOICES, FFMPEG_BIN, DEFAULT_PROJECT_NAME, EMOTIONS
from text_processor import preprocess_script_text
from project_manager import get_project_dir

# Singleton model holder
_tts_instance = None


def get_tts_model():
    """Initializes and returns the singleton XTTS-v2 TTS model."""
    global _tts_instance
    if _tts_instance is None:
        print("Initializing Neural Audio Engine...")
        _tts_instance = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
        print("Neural Audio Engine loaded successfully!")
    return _tts_instance


def build_tone_and_silence_filter(
    age_group: str = "adult",
    gender: str = "male",
    emotion: str = "neutral",
    remove_silence: bool = False,
    is_reference: bool = False,
) -> str:
    """
    Builds an FFmpeg audio filter chain that:
    1. Adjusts voice pitch, vocal tract formants, and resonance based on character Age and Gender
       (e.g., childlike pitch and lightness for kids, deep/resonant warmth and tremor for elders, female pitch shift).
    2. Modulates prosody and frequency curve based on selected Emotion (happy, sad, angry, etc.).
    3. Trims dead silence gaps if remove_silence=True.
    """
    filters = []
    p_factor = 1.0

    ag = (age_group or "adult").lower()
    g = (gender or "male").lower()

    # Age and Gender vocal tract reshaping
    if ag == "child":
        p_factor *= 1.26
        filters.append("highpass=f=130")
        filters.append("equalizer=f=3200:t=q:w=1.2:g=2.5")
        filters.append("equalizer=f=200:t=q:w=1.0:g=-3.0")
    elif ag == "elder":
        if g == "female":
            p_factor *= 1.08
            filters.append("lowpass=f=7200")
            filters.append("equalizer=f=250:t=q:w=1.2:g=2.5")
            if not is_reference:
                filters.append("vibrato=f=4.5:d=0.07")
        else:
            p_factor *= 0.88
            filters.append("lowpass=f=6800")
            filters.append("equalizer=f=200:t=q:w=1.2:g=3.0")
            if not is_reference:
                filters.append("vibrato=f=4.5:d=0.08")
    elif ag == "young":
        if g == "female":
            p_factor *= 1.22
            filters.append("highpass=f=120")
            filters.append("equalizer=f=2800:t=q:w=1.2:g=2.0")
        else:
            p_factor *= 1.05
            filters.append("equalizer=f=3000:t=q:w=1.2:g=1.5")
    elif ag == "adult":
        if g == "female":
            p_factor *= 1.18
            filters.append("highpass=f=100")
            filters.append("equalizer=f=2600:t=q:w=1.2:g=2.0")

    # Emotion prosody & acoustic formant modulation (applied across 15 categories)
    if not is_reference and emotion:
        emo = emotion.lower().strip()
        emo_data = EMOTIONS.get(emo, {})
        cat_id = emo_data.get("category_id", "")

        # 1. Happiness & Positive Emotions
        if cat_id == "happiness" or emo in {"happy", "joyful", "delighted", "playful", "proud", "hopeful", "grateful", "relieved"}:
            p_factor *= 1.05
            filters.append("equalizer=f=3500:t=q:w=1.2:g=2.0")
            if emo in {"excited", "joyful"}:
                p_factor *= 1.03
                filters.append("equalizer=f=4000:t=q:w=1.2:g=2.5")

        # 2. Sadness & Emotional Pain
        elif cat_id == "sadness" or emo in {"sad", "heartbroken", "disappointed", "lonely", "hurt", "melancholic", "grief_stricken", "tearful", "regretful"}:
            p_factor *= 0.94
            filters.append("lowpass=f=6500")
            filters.append("equalizer=f=400:t=q:w=1.2:g=1.5")
            if emo in {"heartbroken", "grief_stricken", "tearful"}:
                p_factor *= 0.98
                filters.append("vibrato=f=4.5:d=0.08")

        # 3. Anger & Frustration
        elif cat_id == "anger" or emo in {"angry", "furious", "irritated", "frustrated", "annoyed", "resentful", "sarcastic", "indignant"}:
            p_factor *= 1.04
            filters.append("acompressor=threshold=-16dB:ratio=4:attack=5:release=50")
            filters.append("equalizer=f=2500:t=q:w=1.2:g=2.5")
            if emo in {"furious", "indignant"}:
                p_factor *= 1.03
                filters.append("equalizer=f=2200:t=q:w=1.0:g=3.5")

        # 4. Fear, Anxiety & Nervousness
        elif cat_id == "fear" or emo in {"afraid", "terrified", "scared", "anxious", "nervous", "panicked", "suspicious", "insecure", "cautious"}:
            p_factor *= 1.06
            filters.append("highpass=f=120")
            filters.append("equalizer=f=3000:t=q:w=1.2:g=2.0")
            if emo in {"panicked", "terrified"}:
                p_factor *= 1.04
                filters.append("vibrato=f=5.5:d=0.10")

        # 5. Surprise & Shock
        elif cat_id == "surprise" or emo in {"surprised", "shocked", "astonished", "amazed", "stunned", "confused", "bewildered"}:
            p_factor *= 1.07
            filters.append("equalizer=f=3200:t=q:w=1.2:g=2.2")

        # 6. Love, Care & Affection
        elif cat_id == "love" or emo in {"loving", "affectionate", "compassionate", "empathetic", "caring", "tender", "reassuring", "nostalgic"}:
            p_factor *= 0.98
            filters.append("equalizer=f=320:t=q:w=1.2:g=2.0")
            filters.append("lowpass=f=7500")

        # 7. Confidence & Authority
        elif cat_id == "confidence" or emo in {"confident", "assertive", "authoritative", "determined", "motivational", "persuasive", "dominant", "defiant"}:
            p_factor *= 0.97
            filters.append("equalizer=f=180:t=q:w=1.0:g=2.5")
            filters.append("equalizer=f=2800:t=q:w=1.2:g=2.0")

        # 8. Curiosity & Interest
        elif cat_id == "curiosity" or emo in {"curious", "intrigued", "interested", "inquisitive", "wondering", "skeptical", "investigative"}:
            p_factor *= 1.03
            filters.append("equalizer=f=3000:t=q:w=1.2:g=1.8")

        # 9. Calmness & Peace
        elif cat_id == "calmness" or emo in {"calm", "peaceful", "relaxed", "serene", "patient", "content", "meditative"}:
            p_factor *= 0.97
            filters.append("lowpass=f=7200")
            filters.append("equalizer=f=250:t=q:w=1.0:g=1.5")

        # 10. Humor & Comedy
        elif cat_id == "humor" or emo in {"funny", "amused_laughter", "chuckling", "giggling", "sarcastic_humor", "teasing", "witty", "deadpan"}:
            p_factor *= 1.05
            filters.append("equalizer=f=3600:t=q:w=1.2:g=2.2")
            if emo in {"giggling", "amused_laughter", "laughing"}:
                filters.append("vibrato=f=5.8:d=0.08")

        # 11. Disgust & Disapproval
        elif cat_id == "disgust" or emo in {"disgusted", "repulsed", "unimpressed", "disapproving", "contemptuous", "dismissive"}:
            p_factor *= 0.95
            filters.append("lowpass=f=6800")
            filters.append("equalizer=f=1200:t=q:w=1.0:g=-2.0")

        # 12. Shame, Guilt & Embarrassment
        elif cat_id == "shame" or emo in {"guilty", "ashamed", "embarrassed", "regretful_shame", "remorseful", "humiliated"}:
            p_factor *= 0.94
            filters.append("lowpass=f=6200")
            filters.append("equalizer=f=350:t=q:w=1.0:g=1.8")

        # 13. Determination, Courage & Resilience
        elif cat_id == "determination" or emo in {"brave", "courageous", "resilient", "persistent", "passionate", "inspired", "empowered"}:
            p_factor *= 1.02
            filters.append("acompressor=threshold=-15dB:ratio=4:attack=4:release=45")
            filters.append("equalizer=f=200:t=q:w=1.0:g=2.2")

        # 14. Confusion, Doubt & Indecision
        elif cat_id == "confusion" or emo in {"doubtful", "hesitant", "uncertain", "indecisive", "puzzled", "distrustful"}:
            p_factor *= 1.01
            filters.append("equalizer=f=1500:t=q:w=1.2:g=1.5")

        # 15. Storytelling & Communication Expressions
        elif cat_id == "storytelling" or emo in {
            "storytelling", "dramatic", "suspenseful", "whispering", "whisper", "shouting",
            "crying", "laughing", "serious", "emotional", "secretive", "urgent",
            "explanatory", "conversational", "reflective", "inspirational"
        }:
            if emo in {"whispering", "whisper"}:
                filters.append("highpass=f=320")
                filters.append("equalizer=f=5500:t=q:w=1.0:g=5.0")
            elif emo == "shouting":
                p_factor *= 1.07
                filters.append("acompressor=threshold=-18dB:ratio=5:attack=2:release=40")
                filters.append("equalizer=f=2200:t=q:w=1.0:g=3.0")
            elif emo in {"dramatic", "suspenseful"}:
                filters.append("equalizer=f=120:t=q:w=1.0:g=2.5")
                filters.append("lowpass=f=7500")
            elif emo == "crying":
                p_factor *= 0.94
                filters.append("vibrato=f=5.2:d=0.15")
                filters.append("equalizer=f=300:t=q:w=1.2:g=2.0")
            elif emo == "urgent":
                p_factor *= 1.05
                filters.append("equalizer=f=2600:t=q:w=1.2:g=2.5")
            elif emo == "secretive":
                filters.append("highpass=f=200")
                filters.append("lowpass=f=6800")
            elif emo == "reflective":
                p_factor *= 0.96
                filters.append("equalizer=f=300:t=q:w=1.0:g=1.8")

    if abs(p_factor - 1.0) > 0.01:
        p_rate = round(24000 * p_factor)
        p_tempo = round(1.0 / p_factor, 5)
        filters.insert(0, f"asetrate={p_rate},atempo={p_tempo},aresample=24000")

    if remove_silence:
        filters.append("silenceremove=start_periods=1:start_duration=0.04:start_threshold=-38dB")
        filters.append("silenceremove=stop_periods=-1:stop_duration=0.12:stop_threshold=-38dB")

    return ",".join(filters)


def prepare_reference_audio(audio_path: str, temp_dir: Path, tone_filter: str = "") -> str:
    """Converts reference audio to clean 24kHz mono WAV with silence trimmed, optional tone conditioning, and loudnorm for optimal XTTS conditioning."""
    src_path = Path(audio_path)
    if not src_path.exists():
        raise FileNotFoundError(f"Reference voice audio file not found: {audio_path}")

    clean_wav = temp_dir / f"clean_ref_{int(time.time() * 1000)}.wav"
    af_chain = ["silenceremove=start_periods=1:start_duration=0.05:start_threshold=-40dB,areverse,silenceremove=start_periods=1:start_duration=0.05:start_threshold=-40dB,areverse"]
    if tone_filter:
        af_chain.append(tone_filter)
    af_chain.append("loudnorm=I=-16:TP=-1.5:LRA=11")
    full_af = ",".join(af_chain)

    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", str(src_path),
        "-af", full_af,
        "-ac", "1",
        "-ar", "24000",
        "-vn",
        str(clean_wav),
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0 and clean_wav.exists():
        return str(clean_wav)
    return str(src_path)


def convert_wav_to_mp3(wav_path: Path, mp3_path: Path, tone_filter: str = "", remove_silence: bool = False):
    """Uses FFmpeg with libmp3lame to convert WAV to clean 192kbps 44.1kHz broadcast MP3, applying tone shaping and optional silence removal."""
    af_chain = ["areverse,silenceremove=start_periods=1:start_duration=0.08:start_threshold=-45dB,areverse"]
    if tone_filter:
        af_chain.append(tone_filter)
    if remove_silence:
        af_chain.append("silenceremove=start_periods=1:start_duration=0.04:start_threshold=-38dB")
        af_chain.append("silenceremove=stop_periods=-1:stop_duration=0.12:stop_threshold=-38dB")
    full_af = ",".join(af_chain)

    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", str(wav_path),
        "-af", full_af,
        "-codec:a", "libmp3lame",
        "-b:a", "192k",
        "-ar", "44100",
        str(mp3_path),
    ]
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")


def trim_tail_silence(raw_wav, sr=24000, thresh=0.015, pad_ms=60):
    """Trims trailing dead silence so sentences connect naturally."""
    arr = np.array(raw_wav, dtype=np.float32)
    active = np.where(np.abs(arr) > thresh)[0]
    if len(active) > 0:
        end = min(len(arr), active[-1] + int(sr * pad_ms / 1000))
        return arr[:end]
    return arr


def merge_short_sentence_chunks(sentences: list[str], min_words: int = 5, min_chars: int = 24) -> list[str]:
    """
    XTTS-v2 autoregressive GPT tends to hallucinate trailing mumbled syllables or random phonemes
    when sentences are extremely short (fewer than 5 words or 24 characters, e.g. 'ओम नम शिवाय।', 'हाँ!', 'ठीक है।').
    This function intelligently merges very short fragments with adjacent sentences using a natural
    clause comma (', '), providing sufficient semantic attention context while preserving natural
    breathing cadence and preventing tail hallucinations.
    """
    clean_sents = [s.strip() for s in sentences if s and s.strip()]
    if not clean_sents:
        return []
    if len(clean_sents) == 1:
        return clean_sents

    merged = []
    buffer = ""

    for s in clean_sents:
        if not buffer:
            buffer = s
        else:
            word_count = len(re.findall(r"\S+", buffer))
            char_count = len(buffer)
            if word_count < min_words or char_count < min_chars:
                # Buffer is too short; merge with current sentence
                # Replace terminal punctuation on buffer with a natural comma pause
                buffer = re.sub(r"[।!?.]+\s*$", "", buffer).strip() + ", " + s
            else:
                merged.append(buffer)
                buffer = s

    # Handle the remaining buffer
    if buffer:
        word_count = len(re.findall(r"\S+", buffer))
        char_count = len(buffer)
        if (word_count < min_words or char_count < min_chars) and merged:
            # Merge with previous sentence
            prev = merged.pop()
            prev = re.sub(r"[।!?.]+\s*$", "", prev).strip() + ", " + buffer
            merged.append(prev)
        else:
            merged.append(buffer)

    return merged


def get_safe_max_new_tokens(text: str, speed: float) -> int | None:
    """Caps runaway generation on isolated short sentences (e.g. 1-3 words) to prevent hallucinated audio."""
    words = len(re.findall(r"\S+", text))
    if words <= 12:
        tokens = int((words * 22 + 40) / max(0.5, speed))
        return min(600, max(50, tokens))
    return None


def resolve_voice_conditioning(
    voice_choice: str,
    emotion: str,
    temp_dir_path: Path,
    remove_silence: bool = False,
    custom_upload: Optional[str] = None,
    progress_callback=None,
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Resolves reference audio (speaker_wav or speaker_name) and out_tone_filter
    based on character persona, age, gender, and emotion takes.
    Returns (speaker_wav, speaker_name, out_tone_filter).
    """
    char_name = ""
    meta = {"age": 30, "age_group": "adult", "gender": "male"}

    if "Custom:" in voice_choice or "[" in voice_choice:
        m = re.search(r"Custom:\s*([^(—\[]+)", voice_choice)
        if m:
            char_name = m.group(1).strip()
        elif "[" in voice_choice:
            file_stem = Path(re.search(r"\[(.*?)\]", voice_choice).group(1)).stem
            char_name = file_stem.split("_")[0].replace("-", " ").title()

        from voice_manager import get_character_metadata
        if char_name:
            meta = get_character_metadata(char_name)

    age_group = meta.get("age_group", "adult")
    gender = meta.get("gender", "male")

    ref_tone_filter = build_tone_and_silence_filter(
        age_group=age_group,
        gender=gender,
        emotion="",
        remove_silence=False,
        is_reference=True,
    )

    out_tone_filter = build_tone_and_silence_filter(
        age_group=age_group,
        gender=gender,
        emotion=emotion,
        remove_silence=remove_silence,
        is_reference=False,
    )

    speaker_wav = None
    speaker_name = None

    if "[" in voice_choice and voice_choice.endswith("]"):
        match = re.search(r"\[(.*?)\]", voice_choice)
        if match:
            chosen_filename = match.group(1).strip()
            ref_file = None
            if emotion and emotion.lower() != "neutral" and char_name:
                char_clean = re.sub(r"[^a-zA-Z0-9_-]", "_", char_name.lower())
                emo_file = VOICES_DIR / f"{char_clean}_{emotion.lower()}.wav"
                if emo_file.exists():
                    ref_file = emo_file
                else:
                    from config import get_emotion_anchor
                    anchor = get_emotion_anchor(emotion)
                    if anchor and anchor != emotion.lower():
                        anchor_file = VOICES_DIR / f"{char_clean}_{anchor}.wav"
                        if anchor_file.exists():
                            ref_file = anchor_file

            if not ref_file:
                fallback_file = VOICES_DIR / chosen_filename
                if fallback_file.exists():
                    ref_file = fallback_file

            if ref_file and ref_file.exists():
                if progress_callback:
                    progress_callback(10, f"Conditioning {age_group.title()} {gender.title()} timbre from {ref_file.name}...", 0, 0, 12.0)
                speaker_wav = prepare_reference_audio(str(ref_file), temp_dir_path, tone_filter=ref_tone_filter)
    elif voice_choice.startswith("Custom Clone: "):
        filename = voice_choice.replace("Custom Clone: ", "").strip()
        ref_file = VOICES_DIR / filename
        if ref_file.exists():
            speaker_wav = prepare_reference_audio(str(ref_file), temp_dir_path, tone_filter=ref_tone_filter)
    elif "Preset:" in voice_choice:
        clean_preset = voice_choice.replace("🎙️ Preset: ", "").strip()
        speaker_name = PRESET_VOICES.get(clean_preset, "Damien Black")
    elif custom_upload is not None:
        speaker_wav = prepare_reference_audio(custom_upload, temp_dir_path, tone_filter=ref_tone_filter)
    else:
        speaker_name = "Damien Black"

    return speaker_wav, speaker_name, out_tone_filter


def _generate_multi_scene_track(
    scenes: list[dict],
    voice_choice: str,
    language_label: str = "Hindi (hi)",
    speed: float = 1.0,
    project_name: str = DEFAULT_PROJECT_NAME,
    clip_title: str = "",
    remove_silence: bool = False,
    progress_callback=None,
) -> tuple[str, str, str]:
    """
    Synthesizes a multi-scene, multi-emotion story.
    Generates each scene take with its custom emotion & voice prosody, saves individual scene MP3s
    into outputs/<project>/, and concatenates all scenes into a master broadcast MP3.
    """
    tts = get_tts_model()
    project_dir = get_project_dir(project_name)
    lang_code = "hi" if "Hindi" in language_label else "en"
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    start_time = time.time()

    clean_title = re.sub(r"[^a-zA-Z0-9_\- ]", "", clip_title.strip()).replace(" ", "_")[:35] if clip_title else "Story"
    final_master_mp3 = project_dir / f"{clean_title}_Master_{timestamp}.mp3"

    total_scenes = len(scenes)
    sr = 24000
    inter_scene_pause = int(sr * 0.10) if remove_silence else int(sr * 0.42)
    pause_array = np.zeros(inter_scene_pause, dtype=np.float32)

    master_waveforms = []
    created_stem_files = []

    with tempfile.TemporaryDirectory() as temp_work_dir:
        temp_dir_path = Path(temp_work_dir)

        for sc_idx, sc in enumerate(scenes):
            sc_num = sc_idx + 1
            sc_text = sc.get("text", "").strip()
            sc_emotion = sc.get("emotion") or "storytelling"
            sc_voice = sc.get("voice") or voice_choice

            pct_start = int(8 + (sc_idx / total_scenes) * 82)
            est_eta = max(1.5, round((total_scenes - sc_idx) * 6.5, 1))

            if progress_callback:
                progress_callback(
                    pct_start,
                    f"Synthesizing Scene {sc_num}/{total_scenes} [{sc_emotion.title()}]: {sc_text[:35]}...",
                    sc_num,
                    total_scenes,
                    est_eta,
                )

            speaker_wav, speaker_name, sc_filter = resolve_voice_conditioning(
                voice_choice=sc_voice,
                emotion=sc_emotion,
                temp_dir_path=temp_dir_path,
                remove_silence=remove_silence,
            )

            processed_text = preprocess_script_text(sc_text, lang_code)
            raw_sentences = tts.synthesizer.split_into_sentences(processed_text, lang_code)
            raw_sentences = [s.strip() for s in raw_sentences if s and s.strip()] or [processed_text]
            sentences = merge_short_sentence_chunks(raw_sentences, min_words=5, min_chars=24) or raw_sentences

            scene_audio_chunks = []
            sentence_pause = np.zeros(int(sr * 0.05 if remove_silence else sr * 0.25), dtype=np.float32)

            for s_i, sen in enumerate(sentences):
                extra_kwargs = {
                    "temperature": 0.70,
                    "repetition_penalty": 10.0,
                }
                safe_tokens = get_safe_max_new_tokens(sen, float(speed))
                if safe_tokens is not None:
                    extra_kwargs["max_new_tokens"] = safe_tokens

                if speaker_wav:
                    chunk = tts.tts(
                        text=sen,
                        speaker_wav=speaker_wav,
                        language=lang_code,
                        speed=float(speed),
                        split_sentences=False,
                        **extra_kwargs,
                    )
                else:
                    chunk = tts.tts(
                        text=sen,
                        speaker=speaker_name,
                        language=lang_code,
                        speed=float(speed),
                        split_sentences=False,
                        **extra_kwargs,
                    )

                chunk = trim_tail_silence(chunk, sr=sr)
                scene_audio_chunks.append(chunk)
                if s_i < len(sentences) - 1:
                    scene_audio_chunks.append(sentence_pause)

            scene_waveform = np.concatenate(scene_audio_chunks)

            # Export individual scene stem MP3
            stem_filename = f"Part_{sc_num:02d}_{clean_title}_Scene_{sc_num:02d}_{sc_emotion}.mp3"
            stem_path = project_dir / stem_filename
            scene_temp_wav = temp_dir_path / f"scene_{sc_num}.wav"
            sf.write(str(scene_temp_wav), scene_waveform, sr)

            convert_wav_to_mp3(scene_temp_wav, stem_path, tone_filter=sc_filter, remove_silence=remove_silence)
            created_stem_files.append(stem_filename)

            # Append to master sequence
            master_waveforms.append(scene_waveform)
            if sc_idx < total_scenes - 1:
                master_waveforms.append(pause_array)

        # Assemble full story master track
        if progress_callback:
            progress_callback(93, "Assembling Full Multi-Scene Story Master...", total_scenes, total_scenes, 2.0)

        master_full_waveform = np.concatenate(master_waveforms)
        master_temp_wav = temp_dir_path / "master_temp.wav"
        sf.write(str(master_temp_wav), master_full_waveform, sr)

        if progress_callback:
            progress_callback(97, "Mastering 192kbps Broadcast MP3...", total_scenes, total_scenes, 1.0)

        convert_wav_to_mp3(master_temp_wav, final_master_mp3, tone_filter=None, remove_silence=remove_silence)
        duration = round(time.time() - start_time, 1)

    if progress_callback:
        progress_callback(100, f"Full Story Ready ({duration}s) — {total_scenes} Scenes Generated!", total_scenes, total_scenes, 0.0)

    status_msg = f"✅ Generated {total_scenes}-scene story in {duration}s | Master: '{final_master_mp3.name}' ({len(created_stem_files)} scene stems saved)"
    return str(final_master_mp3), str(final_master_mp3), status_msg


def generate_voiceover_track(
    script_text: str,
    voice_choice: str,
    custom_upload: str = None,
    language_label: str = "Hindi (hi)",
    speed: float = 1.0,
    project_name: str = DEFAULT_PROJECT_NAME,
    clip_title: str = "",
    emotion: str = "neutral",
    remove_silence: bool = False,
    progress_callback=None,
) -> tuple[str, str, str]:
    """
    Synthesizes script into broadcast-quality 192kbps MP3 stored inside outputs/<project_name>/.
    Automatically parses multi-scene bracketed cues ([Narrator – Calm], [Curious], etc.) if present.
    """
    if not script_text or not script_text.strip():
        raise gr.Error("Please paste your script text before generating.")
    if not voice_choice:
        raise gr.Error("Please select a character voice.")

    # Check for multi-scene bracket cues in script
    from script_parser import parse_script_to_scenes, has_bracketScenes
    if has_bracketScenes(script_text):
        parsed_scenes = parse_script_to_scenes(script_text, default_voice=voice_choice, default_emotion=emotion)
        if len(parsed_scenes) > 1:
            return _generate_multi_scene_track(
                scenes=parsed_scenes,
                voice_choice=voice_choice,
                language_label=language_label,
                speed=speed,
                project_name=project_name,
                clip_title=clip_title,
                remove_silence=remove_silence,
                progress_callback=progress_callback,
            )

    if progress_callback:
        progress_callback(3, "Initializing Neural Audio Engine...", 0, 0, 15.0)

    tts = get_tts_model()
    project_dir = get_project_dir(project_name)

    lang_code = "hi" if "Hindi" in language_label else "en"
    
    if progress_callback:
        progress_callback(7, "Applying 15-Layer Devanagari Linguistic Normalization...", 0, 0, 14.0)

    processed_text = preprocess_script_text(script_text, lang_code)
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    # Generate clean filename based on optional clip_title or voice prefix
    if clip_title and clip_title.strip():
        clean_title = re.sub(r"[^a-zA-Z0-9_\- ]", "", clip_title.strip()).replace(" ", "_")[:35]
        output_filename = f"{clean_title}_{timestamp}.mp3"
    else:
        safe_prefix = re.sub(r"[^a-zA-Z0-9_-]", "_", voice_choice.split("[")[0].strip())[:25]
        output_filename = f"{safe_prefix}_{timestamp}.mp3"

    temp_wav = project_dir / f"temp_{timestamp}.wav"
    final_mp3 = project_dir / output_filename

    with tempfile.TemporaryDirectory() as temp_work_dir:
        temp_dir_path = Path(temp_work_dir)
        speaker_wav, speaker_name, out_tone_filter = resolve_voice_conditioning(
            voice_choice=voice_choice,
            emotion=emotion,
            temp_dir_path=temp_dir_path,
            remove_silence=remove_silence,
            custom_upload=custom_upload,
            progress_callback=progress_callback,
        )

        print(f"Generating audio in [{project_name}] for lang: {lang_code}, voice: {voice_choice}, emotion: {emotion}, speed: {speed}...")
        start_time = time.time()

        # Split into sentences for clean breathing and alignment
        raw_sentences = tts.synthesizer.split_into_sentences(processed_text, lang_code)
        raw_sentences = [s.strip() for s in raw_sentences if s and s.strip()]
        if not raw_sentences:
            raw_sentences = [processed_text]

        # Merge tiny chunks (< 5 words or < 24 chars) to prevent XTTS autoregressive hallucination
        sentences = merge_short_sentence_chunks(raw_sentences, min_words=5, min_chars=24)
        if not sentences:
            sentences = raw_sentences

        total_sentences = len(sentences)
        est_per_sen = 6.0
        current_eta = round(total_sentences * est_per_sen + 2.0, 1)

        sr = 24000
        # Breathing pause between sentences
        if remove_silence:
            pause_samples = int(sr * 0.05)  # 50ms tight spacing
        else:
            pause_samples = int(sr * 0.28)  # 280ms natural diaphragm breathing
        pause_array = np.zeros(pause_samples, dtype=np.float32)

        combined_audio = []
        sentence_times = []

        for idx, sen in enumerate(sentences):
            sen_start_pct = int(12 + (idx / total_sentences) * 78)
            step_desc = f"Synthesizing sentence {idx + 1} of {total_sentences}..."
            if progress_callback:
                progress_callback(sen_start_pct, step_desc, idx + 1, total_sentences, current_eta)

            sen_t0 = time.time()
            extra_kwargs = {
                "temperature": 0.70,
                "repetition_penalty": 10.0,
            }
            safe_tokens = get_safe_max_new_tokens(sen, float(speed))
            if safe_tokens is not None:
                extra_kwargs["max_new_tokens"] = safe_tokens

            if speaker_wav:
                wav_chunk = tts.tts(
                    text=sen,
                    speaker_wav=speaker_wav,
                    language=lang_code,
                    speed=float(speed),
                    split_sentences=False,
                    **extra_kwargs,
                )
            else:
                wav_chunk = tts.tts(
                    text=sen,
                    speaker=speaker_name,
                    language=lang_code,
                    speed=float(speed),
                    split_sentences=False,
                    **extra_kwargs,
                )

            sen_elapsed = time.time() - sen_t0
            sentence_times.append(sen_elapsed)
            avg_sen_time = sum(sentence_times) / len(sentence_times)
            rem_sentences = total_sentences - (idx + 1)
            current_eta = round(max(0.5, rem_sentences * avg_sen_time + 1.2), 1)

            trimmed_chunk = trim_tail_silence(wav_chunk, sr=sr)
            combined_audio.append(trimmed_chunk)
            if idx < len(sentences) - 1:
                combined_audio.append(pause_array)

            sen_done_pct = int(12 + ((idx + 1) / total_sentences) * 78)
            if progress_callback and rem_sentences > 0:
                progress_callback(
                    sen_done_pct,
                    f"Completed sentence {idx + 1}/{total_sentences}. Rendering next...",
                    idx + 1,
                    total_sentences,
                    current_eta,
                )

        if progress_callback:
            progress_callback(92, "Assembling master waveform...", total_sentences, total_sentences, 1.5)

        full_waveform = np.concatenate(combined_audio)
        sf.write(str(temp_wav), full_waveform, sr)

        duration = time.time() - start_time
        print(f"Synthesis completed in {duration:.1f}s. Mastering 192kbps MP3 in {project_dir.name}...")

    # Convert to broadcast-ready 192kbps MP3 with tone shaping and silence trimming
    if progress_callback:
        progress_callback(96, "Mastering 192kbps MP3 (tone shaping & dynamics)...", total_sentences, total_sentences, 0.8)

    convert_wav_to_mp3(temp_wav, final_mp3, tone_filter=out_tone_filter, remove_silence=remove_silence)
    if temp_wav.exists():
        temp_wav.unlink()

    if progress_callback:
        progress_callback(100, f"Generated in {duration:.1f}s — Master Audio Ready!", total_sentences, total_sentences, 0.0)

    status_msg = f"✅ Generated in {duration:.1f}s | Saved to '{project_name}/{final_mp3.name}'"
    return str(final_mp3), str(final_mp3), status_msg

