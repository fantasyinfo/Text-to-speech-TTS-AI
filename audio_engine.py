import os
import re
import time
import tempfile
import subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
import gradio as gr
from TTS.api import TTS

from config import VOICES_DIR, PRESET_VOICES, FFMPEG_BIN, DEFAULT_PROJECT_NAME
from text_processor import preprocess_script_text
from project_manager import get_project_dir

# Singleton model holder
_tts_instance = None


def get_tts_model():
    """Initializes and returns the singleton XTTS-v2 TTS model on Apple Silicon CPU."""
    global _tts_instance
    if _tts_instance is None:
        print("Initializing XTTS-v2 engine on Apple Silicon...")
        _tts_instance = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
        print("XTTS-v2 model loaded successfully!")
    return _tts_instance


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


def trim_tail_silence(raw_wav, sr=24000, thresh=0.015, pad_ms=60):
    """Trims trailing dead silence so sentences connect naturally."""
    arr = np.array(raw_wav, dtype=np.float32)
    active = np.where(np.abs(arr) > thresh)[0]
    if len(active) > 0:
        end = min(len(arr), active[-1] + int(sr * pad_ms / 1000))
        return arr[:end]
    return arr


def generate_voiceover_track(
    script_text: str,
    voice_choice: str,
    custom_upload: str,
    language_label: str,
    speed: float,
    project_name: str = DEFAULT_PROJECT_NAME,
    clip_title: str = "",
) -> tuple[str, str, str]:
    """
    Synthesizes script into high-grade MP3 voiceover stored inside outputs/<project_name>/.
    Returns (mp3_path_for_player, mp3_path_for_download, status_log).
    """
    if not script_text or not script_text.strip():
        raise gr.Error("Please paste your script text before generating.")
    if not voice_choice:
        raise gr.Error("Please select a character voice.")

    tts = get_tts_model()
    project_dir = get_project_dir(project_name)

    lang_code = "hi" if "Hindi" in language_label else "en"
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
        speaker_wav = None
        speaker_name = None

        if "[" in voice_choice and voice_choice.endswith("]"):
            # Custom saved character voice with emotion: extract bracketed filename
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

        print(f"Generating audio in [{project_name}] for lang: {lang_code}, voice: {voice_choice}, speed: {speed}...")
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

            trimmed_chunk = trim_tail_silence(wav_chunk, sr=sr)
            combined_audio.append(trimmed_chunk)
            if idx < len(sentences) - 1:
                combined_audio.append(pause_array)

        full_waveform = np.concatenate(combined_audio)
        sf.write(str(temp_wav), full_waveform, sr)

        duration = time.time() - start_time
        print(f"Synthesis completed in {duration:.1f}s. Converting to Filmora MP3 in {project_dir.name}...")

    # Convert to Filmora-ready 192kbps MP3
    convert_wav_to_mp3(temp_wav, final_mp3)
    if temp_wav.exists():
        temp_wav.unlink()

    status_msg = f"✅ Generated in {duration:.1f}s | Saved to '{project_name}/{final_mp3.name}'"
    return str(final_mp3), str(final_mp3), status_msg

