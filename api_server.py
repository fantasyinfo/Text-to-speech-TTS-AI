"""
FastAPI Backend for VoxStudio AI
Serves REST APIs for Project Workspaces, Multi-Emotion Character Voice Vault,
Devanagari Normalization, and Neural Audio Synthesis.
"""

import os
import re
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import (
    BASE_DIR,
    VOICES_DIR,
    OUTPUTS_DIR,
    DEFAULT_PROJECT_NAME,
    EMOTIONS,
    EMOTION_CATEGORIES,
    PRESET_VOICES,
    FFMPEG_BIN,
)
from project_manager import (
    get_all_projects,
    create_new_project,
    get_project_dir,
    list_project_files,
    rename_project_audio,
    delete_project_audio,
    create_project_zip,
)
from voice_manager import (
    get_existing_characters,
    format_voice_file_label,
    get_available_voices,
    get_character_status_markdown,
    get_character_metadata,
    save_character_metadata,
    load_characters_store,
    update_character_profile,
    delete_character_profile,
    git_sync_characters,
    get_git_sync_status,
)
from audio_engine import generate_voiceover_track, get_tts_model
from text_processor import preprocess_script_text
from job_manager import (
    create_synthesis_job,
    get_job_status,
    get_active_jobs,
    get_recent_jobs,
    cancel_job,
    stream_job_events,
)

app = FastAPI(title="VoxStudio AI API", version="2.0.0")

# Enable CORS for Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Request Models
# ---------------------------------------------------------
class CreateProjectRequest(BaseModel):
    name: str


class RenameAudioRequest(BaseModel):
    old_filename: str
    new_filename: str


class GenerateAudioRequest(BaseModel):
    script_text: str
    voice_choice: str
    language: str = "hi"
    speed: float = 1.0
    project_name: str = DEFAULT_PROJECT_NAME
    clip_title: Optional[str] = ""
    emotion: Optional[str] = "neutral"
    remove_silence: Optional[bool] = False


class UpdateCharacterMetadataRequest(BaseModel):
    age: Optional[str] = "adult"
    gender: Optional[str] = "male"


# ---------------------------------------------------------
# System & Stats APIs
# ---------------------------------------------------------
@app.get("/api/health")
def get_health():
    return {
        "status": "healthy",
        "engine": "Coqui XTTS-v2",
        "device": "Neural Engine (CPU Inference)",
        "output_dir": str(OUTPUTS_DIR),
        "voices_dir": str(VOICES_DIR),
    }


@app.get("/api/stats")
def get_dashboard_stats():
    """Returns overview statistics for the SaaS dashboard."""
    all_projects = get_all_projects()
    total_files = 0
    all_recent_files = []

    for proj in all_projects:
        files = list_project_files(proj)
        total_files += len(files)
        for f in files:
            all_recent_files.append({
                **f,
                "project": proj,
                "url": f"/api/audio/{proj}/{f['filename']}",
            })

    # Sort recent files newest first
    all_recent_files.sort(key=lambda x: x["mtime"], reverse=True)

    characters = get_existing_characters()
    total_emotions_recorded = 0
    for f in VOICES_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in {".wav", ".mp3", ".m4a"}:
            total_emotions_recorded += 1

    return {
        "total_projects": len(all_projects),
        "total_audio_tracks": total_files,
        "total_characters": len(characters),
        "total_emotion_samples": total_emotions_recorded,
        "recent_generations": all_recent_files[:8],
    }


# ---------------------------------------------------------
# Project Workspace APIs
# ---------------------------------------------------------
@app.get("/api/projects")
def list_projects():
    projects = get_all_projects()
    return {"projects": projects, "default": projects[0] if projects else DEFAULT_PROJECT_NAME}


@app.post("/api/projects")
def api_create_project(req: CreateProjectRequest):
    new_name, updated_list, msg = create_new_project(req.name)
    return {"name": new_name, "projects": updated_list, "message": msg}


@app.get("/api/projects/{project_name}/files")
def get_project_audio_files(project_name: str):
    files = list_project_files(project_name)
    for f in files:
        f["url"] = f"/api/audio/{project_name}/{f['filename']}"
    return {"project": project_name, "files": files}


@app.post("/api/projects/{project_name}/rename")
def api_rename_audio(project_name: str, req: RenameAudioRequest):
    renamed, choices, msg = rename_project_audio(project_name, req.old_filename, req.new_filename)
    if not renamed:
        raise HTTPException(status_code=400, detail=msg)
    return {
        "renamed_filename": renamed,
        "url": f"/api/audio/{project_name}/{renamed}",
        "message": msg,
    }


@app.delete("/api/projects/{project_name}/files/{filename}")
def api_delete_audio(project_name: str, filename: str):
    choices, msg = delete_project_audio(project_name, filename)
    return {"message": msg, "remaining_count": len(choices)}


@app.get("/api/projects/{project_name}/export-zip")
def api_export_project_zip(project_name: str):
    try:
        zip_path = create_project_zip(project_name)
        return FileResponse(
            path=zip_path,
            filename=Path(zip_path).name,
            media_type="application/zip",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audio/{project_name}/{filename}")
def get_audio_stream(project_name: str, filename: str):
    p_dir = get_project_dir(project_name)
    target = p_dir / filename
    if not target.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    media_type = "audio/mpeg" if target.suffix.lower() == ".mp3" else "audio/wav"
    return FileResponse(path=str(target), media_type=media_type, filename=filename)


# ---------------------------------------------------------
# Character & Emotion Voice Vault APIs
# ---------------------------------------------------------
@app.get("/api/emotions-guide")
def get_emotions_guide():
    """Returns the 15 emotion categories & 121 delivery styles with acting tips and scripts."""
    return {"emotions": EMOTIONS, "categories": EMOTION_CATEGORIES}


@app.get("/api/characters")
def list_characters_with_emotions():
    """Returns character roster with emotion breakdown for SaaS cards."""
    store = load_characters_store()
    characters = get_existing_characters()
    roster = []

    for char_name in characters:
        clean_char = re.sub(r"[^a-zA-Z0-9_-]", "_", char_name.strip().lower())
        char_emotions = {}

        # Scan for existing recorded files
        for f in VOICES_DIR.iterdir():
            if f.is_file() and f.suffix.lower() in {".wav", ".mp3", ".m4a"}:
                stem = f.stem.lower()
                if stem.startswith(f"{clean_char}_") or stem.startswith(f"{clean_char}-"):
                    emo = stem[len(clean_char) + 1 :]
                    char_emotions[emo] = f"/api/voices/raw/{f.name}"
                elif stem == clean_char:
                    char_emotions["neutral"] = f"/api/voices/raw/{f.name}"

        recorded_count = sum(1 for emo in EMOTIONS if emo in char_emotions)
        meta = get_character_metadata(char_name)
        char_entry = store.get("characters", {}).get(clean_char, {})
        roster.append({
            "id": clean_char,
            "name": char_name,
            "age": meta.get("age", 30),
            "age_group": meta.get("age_group", "adult"),
            "gender": meta.get("gender", "male"),
            "description": meta.get("description", ""),
            "recorded_count": recorded_count,
            "total_emotions": len(EMOTIONS),
            "completeness_percent": int((recorded_count / len(EMOTIONS)) * 100),
            "created_at": char_entry.get("created_at"),
            "updated_at": char_entry.get("updated_at"),
            "emotions": {
                emo_key: {
                    "recorded": emo_key in char_emotions,
                    "audio_url": char_emotions.get(emo_key),
                    "title": data["title"],
                }
                for emo_key, data in EMOTIONS.items()
            },
        })

    return {"characters": roster}


@app.get("/api/characters/{char_name}")
def get_single_character(char_name: str):
    """Returns full profile data for a single character."""
    meta = get_character_metadata(char_name)
    store = load_characters_store()
    clean_char = re.sub(r"[^a-zA-Z0-9_-]", "_", char_name.strip().lower())
    char_entry = store.get("characters", {}).get(clean_char, {})
    return {
        "id": clean_char,
        "name": char_entry.get("name", char_name),
        "age": meta.get("age", 30),
        "age_group": meta.get("age_group", "adult"),
        "gender": meta.get("gender", "male"),
        "description": meta.get("description", ""),
        "takes": char_entry.get("takes", {}),
    }


@app.post("/api/characters/update")
async def update_character_api(
    char_name: str = Form(...),
    new_name: Optional[str] = Form(None),
    age: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    emotion: Optional[str] = Form("neutral"),
    push_to_git: Optional[bool] = Form(False),
    audio_file: Optional[UploadFile] = File(None),
):
    """Updates an existing character profile (rename, age, gender, description, replace voice audio)."""
    temp_upload = None
    try:
        if audio_file and audio_file.filename:
            temp_upload = VOICES_DIR / f"temp_upload_{int(time.time() * 1000)}.bin"
            with open(temp_upload, "wb") as f:
                f.write(await audio_file.read())

        updated = update_character_profile(
            char_name=char_name,
            new_name=new_name,
            age=age,
            gender=gender,
            description=description,
            new_audio_path=str(temp_upload) if temp_upload else None,
            emotion_key=emotion or "neutral",
        )

        git_res = None
        if push_to_git:
            commit_msg = f"feat(characters): update character profile '{new_name or char_name}'"
            git_res = git_sync_characters(commit_msg)

        return {
            "success": True,
            "character": updated,
            "git_sync": git_res,
            "message": f"Character '{updated['name']}' updated successfully!",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if temp_upload and temp_upload.exists():
            try:
                temp_upload.unlink()
            except Exception:
                pass


@app.delete("/api/characters/{char_name}")
def delete_character_api(char_name: str):
    """Deletes a custom character profile and all associated audio takes."""
    success = delete_character_profile(char_name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Character '{char_name}' not found.")
    return {
        "success": True,
        "message": f"Character '{char_name}' and all associated audio samples deleted.",
    }


@app.get("/api/git/status")
def api_git_status():
    """Returns local git sync status for character profiles and models."""
    return get_git_sync_status()


@app.post("/api/git/push")
def api_git_push():
    """Commits and pushes character profiles, settings, and voice samples to GitHub."""
    res = git_sync_characters()
    return res


@app.get("/api/voices/raw/{filename}")
def get_voice_sample(filename: str):
    target = VOICES_DIR / filename
    if not target.exists():
        raise HTTPException(status_code=404, detail="Voice file not found")
    return FileResponse(path=str(target), media_type="audio/wav")


@app.get("/api/voices")
def list_all_voices():
    """Returns formatted list of preset and custom voices for the studio dropdown."""
    return {"voices": get_available_voices(), "presets": PRESET_VOICES}


@app.post("/api/characters/record-emotion")
async def save_character_emotion_api(
    character_name: str = Form(...),
    emotion_key: str = Form("neutral"),
    age: Optional[str] = Form("adult"),
    gender: Optional[str] = Form("male"),
    audio_file: UploadFile = File(...),
):
    """Saves and normalizes an emotion audio sample for a character with age and gender metadata."""
    if not character_name or not character_name.strip():
        raise HTTPException(status_code=400, detail="Character name is required")
    if emotion_key not in EMOTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid emotion key: {emotion_key}")

    # Persist character age, age_group, and gender
    save_character_metadata(character_name, age=age or "adult", gender=gender or "male")

    safe_char = re.sub(r"[^a-zA-Z0-9_-]", "_", character_name.strip().lower())
    safe_emo = emotion_key.strip().lower()
    dest_filename = f"{safe_char}_{safe_emo}.wav"
    dest_path = VOICES_DIR / dest_filename

    # Save incoming upload to temporary file
    temp_upload = VOICES_DIR / f"temp_upload_{int(time.time() * 1000)}.bin"
    with open(temp_upload, "wb") as f:
        f.write(await audio_file.read())

    # Normalize with FFmpeg to 24000Hz mono PCM WAV with loudnorm
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", str(temp_upload),
        "-af", "silenceremove=start_periods=1:start_duration=0.05:start_threshold=-40dB,areverse,silenceremove=start_periods=1:start_duration=0.05:start_threshold=-40dB,areverse,loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ac", "1",
        "-ar", "24000",
        "-vn",
        str(dest_path),
    ]
    res = shutil.which("ffmpeg")
    import subprocess
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

    if temp_upload.exists():
        temp_upload.unlink()

    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"FFmpeg processing failed: {result.stderr}")

    display_char = character_name.strip().replace("_", " ").title()
    meta = get_character_metadata(character_name)

    # Record take into characters store
    store = load_characters_store()
    if safe_char not in store.get("characters", {}):
        store["characters"][safe_char] = {
            "id": safe_char,
            "name": display_char,
            "age": meta.get("age", 30),
            "age_group": meta.get("age_group", "adult"),
            "gender": meta.get("gender", "male"),
            "description": meta.get("description", ""),
            "takes": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
    if "takes" not in store["characters"][safe_char]:
        store["characters"][safe_char]["takes"] = {}
    store["characters"][safe_char]["takes"][safe_emo] = {
        "emotion": safe_emo,
        "filename": dest_filename,
        "filepath": f"voices/{dest_filename}",
        "label": EMOTIONS.get(safe_emo, {}).get("title", safe_emo.title()),
    }
    store["characters"][safe_char]["updated_at"] = datetime.now().isoformat()
    from voice_manager import save_characters_store
    save_characters_store(store)

    return {
        "success": True,
        "filename": dest_filename,
        "character": display_char,
        "emotion": safe_emo,
        "profile": meta,
        "message": f"Saved {EMOTIONS[safe_emo]['title']} for {display_char} ({meta['age_group'].title()} • {meta['gender'].title()})!",
    }


@app.put("/api/characters/{char_name}/metadata")
def update_character_metadata_api(char_name: str, req: UpdateCharacterMetadataRequest):
    """Updates age and gender metadata for an existing character."""
    updated = save_character_metadata(char_name, age=req.age or "adult", gender=req.gender or "male")
    return {"success": True, "character": updated}


# ---------------------------------------------------------
# Background Synthesis Job APIs (Non-Blocking with ETA & SSE)
# ---------------------------------------------------------
@app.post("/api/jobs/generate")
def api_create_job(req: GenerateAudioRequest):
    if not req.script_text or not req.script_text.strip():
        raise HTTPException(status_code=400, detail="Script text cannot be empty.")
    if not req.voice_choice:
        raise HTTPException(status_code=400, detail="Please select a character voice.")

    job_id = create_synthesis_job(
        script_text=req.script_text,
        voice_choice=req.voice_choice,
        language=req.language,
        speed=req.speed,
        project_name=req.project_name,
        clip_title=req.clip_title or "",
        emotion=req.emotion or "neutral",
        remove_silence=bool(req.remove_silence),
    )
    job = get_job_status(job_id)
    return {"success": True, "job_id": job_id, "job": job}


@app.get("/api/jobs/active")
def api_get_active_jobs():
    return {"active_jobs": get_active_jobs()}


@app.get("/api/jobs/recent")
def api_get_recent_jobs():
    return {"recent_jobs": get_recent_jobs()}


@app.get("/api/jobs/{job_id}")
def api_get_job(job_id: str):
    job = get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/jobs/{job_id}/stream")
async def api_stream_job(job_id: str):
    job = get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return StreamingResponse(
        stream_job_events(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/jobs/{job_id}/cancel")
def api_cancel_job(job_id: str):
    cancelled = cancel_job(job_id)
    return {"success": cancelled, "job_id": job_id}


# ---------------------------------------------------------
# Voiceover Studio Synthesis API (Synchronous fallback)
# ---------------------------------------------------------
@app.post("/api/generate")
def generate_audio_api(req: GenerateAudioRequest):
    if not req.script_text or not req.script_text.strip():
        raise HTTPException(status_code=400, detail="Script text cannot be empty.")
    if not req.voice_choice:
        raise HTTPException(status_code=400, detail="Please select a character voice.")

    try:
        player_file, dl_file, status_msg = generate_voiceover_track(
            script_text=req.script_text,
            voice_choice=req.voice_choice,
            custom_upload=None,
            language_label="Hindi (hi)" if req.language.lower() in {"hi", "hindi"} else "English (en)",
            speed=float(req.speed),
            project_name=req.project_name,
            clip_title=req.clip_title or "",
        )

        filename = Path(dl_file).name
        return {
            "success": True,
            "filename": filename,
            "project": req.project_name,
            "audio_url": f"/api/audio/{req.project_name}/{filename}",
            "status": status_msg,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# Serve Static React Build if available
# ---------------------------------------------------------
frontend_dist = BASE_DIR / "frontend" / "dist"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    # Warm up model on startup
    get_tts_model()
    uvicorn.run("api_server:app", host="127.0.0.1", port=8000, reload=False)

