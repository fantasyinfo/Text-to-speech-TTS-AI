import os
import re
import time
import shutil
import zipfile
from pathlib import Path
from config import OUTPUTS_DIR, DEFAULT_PROJECT_NAME


def clean_project_name(raw_name: str) -> str:
    """Normalizes project names into safe filesystem folder names."""
    if not raw_name or not raw_name.strip():
        return DEFAULT_PROJECT_NAME
    cleaned = re.sub(r"[^a-zA-Z0-9_\- ]", "", raw_name.strip()).replace(" ", "_")
    return cleaned if cleaned else DEFAULT_PROJECT_NAME


def get_all_projects() -> list[str]:
    """Returns a sorted list of all project folders inside outputs/."""
    OUTPUTS_DIR.mkdir(exist_ok=True)
    projects = []
    for item in OUTPUTS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            projects.append(item.name)

    # Ensure at least Default_Project exists
    if not projects:
        default_dir = OUTPUTS_DIR / DEFAULT_PROJECT_NAME
        default_dir.mkdir(exist_ok=True)
        projects.append(DEFAULT_PROJECT_NAME)

    projects.sort()
    return projects


def create_new_project(raw_name: str) -> tuple[str, list[str], str]:
    """Creates a new project folder and returns (new_project_name, updated_choices, status_message)."""
    safe_name = clean_project_name(raw_name)
    target_dir = OUTPUTS_DIR / safe_name
    created = False
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
        created = True

    updated_choices = get_all_projects()
    status_msg = f"✅ Project '{safe_name}' created!" if created else f"📁 Project '{safe_name}' already exists."
    return safe_name, updated_choices, status_msg


def get_project_dir(project_name: str) -> Path:
    """Returns the Path to the project's folder, creating it if necessary."""
    safe_name = clean_project_name(project_name)
    p_dir = OUTPUTS_DIR / safe_name
    p_dir.mkdir(parents=True, exist_ok=True)
    return p_dir


def list_project_files(project_name: str) -> list[dict]:
    """Lists all audio files (.mp3, .wav) inside the project folder sorted newest-first."""
    p_dir = get_project_dir(project_name)
    files = []
    valid_exts = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
    for f in p_dir.iterdir():
        if f.is_file() and f.suffix.lower() in valid_exts and not f.name.startswith("."):
            st = f.stat()
            files.append({
                "filename": f.name,
                "path": str(f.resolve()),
                "size_kb": f"{st.st_size / 1024:.1f} KB",
                "modified": time.strftime("%d %b %Y, %H:%M:%S", time.localtime(st.st_mtime)),
                "mtime": st.st_mtime,
            })
    files.sort(key=lambda x: x["mtime"], reverse=True)
    return files


def get_project_file_choices(project_name: str) -> list[str]:
    """Returns filenames in the project for dropdowns."""
    files = list_project_files(project_name)
    return [f["filename"] for f in files]


def rename_project_audio(project_name: str, old_filename: str, new_filename: str) -> tuple[str, list[str], str]:
    """Renames an audio file inside the project folder."""
    if not old_filename or not old_filename.strip():
        return "", get_project_file_choices(project_name), "⚠️ Please select an audio file to rename."
    if not new_filename or not new_filename.strip():
        return old_filename, get_project_file_choices(project_name), "⚠️ Please enter a new filename."

    p_dir = get_project_dir(project_name)
    src_file = p_dir / old_filename.strip()
    if not src_file.exists():
        return "", get_project_file_choices(project_name), f"⚠️ File '{old_filename}' not found."

    orig_ext = src_file.suffix
    clean_stem = re.sub(r"[^a-zA-Z0-9_\- ]", "", Path(new_filename.strip()).stem).strip().replace(" ", "_")
    if not clean_stem:
        return old_filename, get_project_file_choices(project_name), "⚠️ Invalid new filename."

    dest_filename = f"{clean_stem}{orig_ext}"
    dest_file = p_dir / dest_filename

    if dest_file.exists() and dest_file != src_file:
        return old_filename, get_project_file_choices(project_name), f"⚠️ A file named '{dest_filename}' already exists."

    src_file.rename(dest_file)
    updated_choices = get_project_file_choices(project_name)
    return dest_filename, updated_choices, f"✅ Renamed to '{dest_filename}' successfully!"


def delete_project_audio(project_name: str, filename: str) -> tuple[list[str], str]:
    """Deletes an audio file from the project folder."""
    if not filename or not filename.strip():
        return get_project_file_choices(project_name), "⚠️ No audio file selected."

    p_dir = get_project_dir(project_name)
    target = p_dir / filename.strip()
    if target.exists():
        target.unlink()
        return get_project_file_choices(project_name), f"🗑️ Deleted '{filename}'."
    return get_project_file_choices(project_name), f"⚠️ File '{filename}' not found."


def create_project_zip(project_name: str) -> str:
    """Bundles all audio tracks in the project into a single ZIP file for batch download."""
    p_dir = get_project_dir(project_name)
    files = list_project_files(project_name)
    if not files:
        raise ValueError(f"Project '{project_name}' has no audio files to export.")

    zip_filename = f"{p_dir.name}_Audio_Export_{time.strftime('%Y%m%d_%H%M%S')}.zip"
    zip_path = OUTPUTS_DIR / zip_filename

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for f_info in files:
            file_path = Path(f_info["path"])
            zipf.write(file_path, arcname=file_path.name)

    return str(zip_path.resolve())

