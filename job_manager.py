"""
Background Synthesis Job Manager for VoxStudio AI
Manages non-blocking background voiceover synthesis, real-time sentence progress,
dynamic Apple Silicon ETA tracking, and Server-Sent Events (SSE) updates.
"""

import time
import uuid
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional, Dict, Any, AsyncGenerator

from audio_engine import generate_voiceover_track
from config import DEFAULT_PROJECT_NAME

# Single-worker thread pool for Apple Silicon CPU inference
_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="xtts_worker")
_lock = threading.Lock()
_jobs: Dict[str, Dict[str, Any]] = {}


def create_synthesis_job(
    script_text: str,
    voice_choice: str,
    language: str,
    speed: float,
    project_name: str = DEFAULT_PROJECT_NAME,
    clip_title: str = "",
) -> str:
    """Enqueues a new synthesis job in the background and returns job_id immediately."""
    job_id = f"job_{uuid.uuid4().hex[:10]}"
    now = time.time()

    preview = (script_text[:65] + "...") if len(script_text) > 65 else script_text

    with _lock:
        _jobs[job_id] = {
            "id": job_id,
            "status": "queued",
            "progress": 0,
            "step": "Queued in background...",
            "current_sentence": 0,
            "total_sentences": 0,
            "eta_seconds": 15.0,
            "elapsed_seconds": 0.0,
            "created_at": now,
            "started_at": None,
            "completed_at": None,
            "project": project_name,
            "clip_title": clip_title,
            "voice": voice_choice,
            "script_preview": preview,
            "result": None,
            "error": None,
        }

    # Submit to worker thread
    _executor.submit(
        _run_job_worker,
        job_id=job_id,
        script_text=script_text,
        voice_choice=voice_choice,
        language=language,
        speed=speed,
        project_name=project_name,
        clip_title=clip_title,
    )

    return job_id


def _run_job_worker(
    job_id: str,
    script_text: str,
    voice_choice: str,
    language: str,
    speed: float,
    project_name: str,
    clip_title: str,
):
    """Worker task executed in background thread."""
    t_start = time.time()

    with _lock:
        if job_id not in _jobs:
            return
        _jobs[job_id]["status"] = "processing"
        _jobs[job_id]["started_at"] = t_start
        _jobs[job_id]["step"] = "Initializing Apple Silicon XTTS-v2 inference..."
        _jobs[job_id]["progress"] = 5

    def on_progress(percent: int, step_desc: str, current_sen: int, total_sen: int, eta: float):
        elapsed = round(time.time() - t_start, 1)
        with _lock:
            if job_id in _jobs:
                # Do not overwrite if cancelled
                if _jobs[job_id]["status"] == "cancelled":
                    return
                _jobs[job_id]["progress"] = percent
                _jobs[job_id]["step"] = step_desc
                _jobs[job_id]["current_sentence"] = current_sen
                _jobs[job_id]["total_sentences"] = total_sen
                _jobs[job_id]["eta_seconds"] = round(eta, 1)
                _jobs[job_id]["elapsed_seconds"] = elapsed

    try:
        player_file, dl_file, status_msg = generate_voiceover_track(
            script_text=script_text,
            voice_choice=voice_choice,
            custom_upload=None,
            language_label="Hindi (hi)" if language.lower() in {"hi", "hindi"} else "English (en)",
            speed=float(speed),
            project_name=project_name,
            clip_title=clip_title or "",
            progress_callback=on_progress,
        )

        t_end = time.time()
        filename = Path(dl_file).name

        with _lock:
            if job_id in _jobs and _jobs[job_id]["status"] != "cancelled":
                _jobs[job_id]["status"] = "completed"
                _jobs[job_id]["progress"] = 100
                _jobs[job_id]["step"] = f"Voiceover ready! ({round(t_end - t_start, 1)}s)"
                _jobs[job_id]["eta_seconds"] = 0.0
                _jobs[job_id]["elapsed_seconds"] = round(t_end - t_start, 1)
                _jobs[job_id]["completed_at"] = t_end
                _jobs[job_id]["result"] = {
                    "filename": filename,
                    "project": project_name,
                    "audio_url": f"/api/audio/{project_name}/{filename}",
                    "status": status_msg,
                    "duration_seconds": round(t_end - t_start, 1),
                }

    except Exception as exc:
        import traceback
        traceback.print_exc()
        t_end = time.time()
        with _lock:
            if job_id in _jobs:
                _jobs[job_id]["status"] = "failed"
                _jobs[job_id]["step"] = f"Failed: {str(exc)}"
                _jobs[job_id]["eta_seconds"] = 0.0
                _jobs[job_id]["elapsed_seconds"] = round(t_end - t_start, 1)
                _jobs[job_id]["error"] = str(exc)


def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Returns snapshot of current job state."""
    with _lock:
        job = _jobs.get(job_id)
        if job:
            # If still processing, update elapsed time on read
            if job["status"] == "processing" and job["started_at"]:
                job["elapsed_seconds"] = round(time.time() - job["started_at"], 1)
            return dict(job)
    return None


def get_active_jobs() -> list[Dict[str, Any]]:
    """Returns all queued or currently processing jobs."""
    with _lock:
        active = []
        for j in _jobs.values():
            if j["status"] in {"queued", "processing"}:
                item = dict(j)
                if item["started_at"]:
                    item["elapsed_seconds"] = round(time.time() - item["started_at"], 1)
                active.append(item)
        return active


def get_recent_jobs(limit: int = 10) -> list[Dict[str, Any]]:
    """Returns recently completed/failed jobs."""
    with _lock:
        all_jobs = list(_jobs.values())
        all_jobs.sort(key=lambda x: x["created_at"], reverse=True)
        return [dict(j) for j in all_jobs[:limit]]


def cancel_job(job_id: str) -> bool:
    """Marks a job as cancelled."""
    with _lock:
        if job_id in _jobs and _jobs[job_id]["status"] in {"queued", "processing"}:
            _jobs[job_id]["status"] = "cancelled"
            _jobs[job_id]["step"] = "Cancelled by user"
            _jobs[job_id]["eta_seconds"] = 0.0
            return True
    return False


async def stream_job_events(job_id: str) -> AsyncGenerator[str, None]:
    """Yields SSE events with JSON data while job is active."""
    import json
    last_payload = ""

    while True:
        job = get_job_status(job_id)
        if not job:
            yield f"data: {json.dumps({'error': 'Job not found', 'status': 'not_found'})}\n\n"
            break

        payload = json.dumps(job)
        if payload != last_payload:
            yield f"data: {payload}\n\n"
            last_payload = payload

        if job["status"] in {"completed", "failed", "cancelled"}:
            # Send final event and terminate stream
            break

        await asyncio.sleep(0.35)

