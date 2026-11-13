import json
import re
import shutil
import subprocess
import time
from datetime import datetime
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

CHARACTERS_METADATA_FILE = VOICES_DIR / "characters_metadata.json"
CHARACTERS_JSON_FILE = VOICES_DIR / "characters.json"
ROOT_CHARACTERS_JSON = Path(__file__).resolve().parent / "characters.json"
WORKSPACE_DIR = Path(__file__).resolve().parent


def normalize_age_group(age_val) -> tuple[str, int]:
    """Returns (age_group, approximate_age_int). Groups: child (<=12), young (13-24), adult (25-55), elder (56+)."""
    if isinstance(age_val, (int, float)):
        age_int = int(age_val)
        if age_int <= 12:
            return "child", age_int
        elif age_int <= 24:
            return "young", age_int
        elif age_int <= 55:
            return "adult", age_int
        else:
            return "elder", age_int

    val_str = str(age_val).strip().lower()
    num_match = re.search(r"\d+", val_str)
    if num_match:
        age_int = int(num_match.group(0))
        if age_int <= 12:
            return "child", age_int
        elif age_int <= 24:
            return "young", age_int
        elif age_int <= 55:
            return "adult", age_int
        else:
            return "elder", age_int

    if any(k in val_str for k in ["child", "kid", "baby", "बच्चा", "बाल"]):
        return "child", 8
    if any(k in val_str for k in ["young", "teen", "youth", "युवा", "किशोरी"]):
        return "young", 20
    if any(k in val_str for k in ["elder", "old", "senior", "grand", "बुजुर्ग", "दादी", "दादा"]):
        return "elder", 65
    return "adult", 30


def load_characters_store() -> dict:
    """Loads the primary characters repository store.
    If characters.json does not exist, it bootstraps from characters_metadata.json and voices/ files.
    """
    VOICES_DIR.mkdir(parents=True, exist_ok=True)
    if CHARACTERS_JSON_FILE.exists():
        try:
            with open(CHARACTERS_JSON_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "characters" in data:
                    return data
        except Exception:
            pass

    # Bootstrap from metadata & folder scan
    meta = {}
    if CHARACTERS_METADATA_FILE.exists():
        try:
            with open(CHARACTERS_METADATA_FILE, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            meta = {}

    characters_map = {}
    for f in VOICES_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in {".wav", ".mp3", ".m4a", ".flac", ".ogg"}:
            stem = f.stem.lower()
            if stem == "readme":
                continue
            found_emo = None
            char_slug = stem
            for emo_k in EMOTIONS.keys():
                if stem.endswith(f"_{emo_k}") or stem.endswith(f"-{emo_k}"):
                    found_emo = emo_k
                    char_slug = stem[: -(len(emo_k) + 1)]
                    break
            if not found_emo:
                found_emo = "neutral"

            char_slug = re.sub(r"[^a-zA-Z0-9_-]", "_", char_slug).strip("_")
            if not char_slug:
                continue

            if char_slug not in characters_map:
                m = meta.get(char_slug, {})
                cname = m.get("name", char_slug.replace("_", " ").replace("-", " ").title())
                cage = m.get("age", 30)
                cgroup = m.get("age_group", "adult")
                cgender = m.get("gender", "male")
                cdesc = m.get("description", f"{cgroup.title()} {cgender.title()}")
                characters_map[char_slug] = {
                    "id": char_slug,
                    "name": cname,
                    "age": cage,
                    "age_group": cgroup,
                    "gender": cgender,
                    "description": cdesc,
                    "takes": {},
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }

            characters_map[char_slug]["takes"][found_emo] = {
                "emotion": found_emo,
                "filename": f.name,
                "filepath": f"voices/{f.name}",
                "label": EMOTIONS.get(found_emo, {}).get("title", found_emo.title()),
            }

    if not characters_map:
        characters_map["test01"] = {
            "id": "test01",
            "name": "Test01",
            "age": 30,
            "age_group": "adult",
            "gender": "male",
            "description": "Adult Male",
            "takes": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    store = {
        "version": "1.0",
        "updated_at": datetime.now().isoformat(),
        "characters": characters_map,
    }
    save_characters_store(store)
    return store


def save_characters_store(store: dict):
    """Saves characters store to voices/characters.json, characters.json (root), and syncs characters_metadata.json."""
    VOICES_DIR.mkdir(parents=True, exist_ok=True)
    store["updated_at"] = datetime.now().isoformat()
    with open(CHARACTERS_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2, ensure_ascii=False)

    try:
        with open(ROOT_CHARACTERS_JSON, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    flat = {}
    for cid, cinfo in store.get("characters", {}).items():
        flat[cid] = {
            "name": cinfo.get("name", cid.title()),
            "age": cinfo.get("age", 30),
            "age_group": cinfo.get("age_group", "adult"),
            "gender": cinfo.get("gender", "male"),
            "description": cinfo.get("description", ""),
        }
    try:
        with open(CHARACTERS_METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(flat, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def load_characters_metadata() -> dict:
    store = load_characters_store()
    flat = {}
    for cid, cinfo in store.get("characters", {}).items():
        flat[cid] = {
            "name": cinfo.get("name", cid.title()),
            "age": cinfo.get("age", 30),
            "age_group": cinfo.get("age_group", "adult"),
            "gender": cinfo.get("gender", "male"),
            "description": cinfo.get("description", ""),
        }
    return flat


def get_character_metadata(char_name: str) -> dict:
    clean_key = re.sub(r"[^a-zA-Z0-9_-]", "_", char_name.strip().lower())
    store = load_characters_store()
    chars = store.get("characters", {})
    if clean_key in chars:
        c = chars[clean_key]
        return {
            "name": c.get("name", char_name),
            "age": c.get("age", 30),
            "age_group": c.get("age_group", "adult"),
            "gender": c.get("gender", "male"),
            "description": c.get("description", ""),
        }
    return {
        "name": char_name.strip().replace("_", " ").title(),
        "age": 30,
        "age_group": "adult",
        "gender": "male",
        "description": "Adult Male",
    }


def save_character_metadata(char_name: str, age: str | int = "adult", gender: str = "male", description: str = "") -> dict:
    clean_key = re.sub(r"[^a-zA-Z0-9_-]", "_", char_name.strip().lower())
    store = load_characters_store()
    age_group, age_num = normalize_age_group(age)
    gender_clean = gender.strip().lower() if gender else "male"
    if gender_clean not in {"male", "female", "neutral"}:
        gender_clean = "male"

    display_name = char_name.strip().replace("_", " ").title()
    if clean_key not in store["characters"]:
        store["characters"][clean_key] = {
            "id": clean_key,
            "name": display_name,
            "age": age_num,
            "age_group": age_group,
            "gender": gender_clean,
            "description": description or f"{age_group.title()} {gender_clean.title()}",
            "takes": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
    else:
        c = store["characters"][clean_key]
        c["name"] = display_name
        c["age"] = age_num
        c["age_group"] = age_group
        c["gender"] = gender_clean
        if description:
            c["description"] = description
        c["updated_at"] = datetime.now().isoformat()

    save_characters_store(store)
    return store["characters"][clean_key]


def update_character_profile(
    char_name: str,
    new_name: str = None,
    age: str | int = None,
    gender: str = None,
    description: str = None,
    new_audio_path: str = None,
    emotion_key: str = "neutral",
) -> dict:
    """Updates an existing character profile with renaming, age, gender, and reference audio changes."""
    store = load_characters_store()
    old_key = re.sub(r"[^a-zA-Z0-9_-]", "_", char_name.strip().lower())

    target_char = None
    if old_key in store["characters"]:
        target_char = store["characters"][old_key]
    else:
        for cid, cinfo in store["characters"].items():
            if cinfo.get("name", "").lower() == char_name.strip().lower():
                old_key = cid
                target_char = cinfo
                break

    if not target_char:
        target_char = {
            "id": old_key,
            "name": char_name.strip().replace("_", " ").title(),
            "age": 30,
            "age_group": "adult",
            "gender": "male",
            "description": "Adult Male",
            "takes": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        store["characters"][old_key] = target_char

    active_key = old_key

    # 1. Renaming
    if new_name and new_name.strip() and new_name.strip() != target_char.get("name"):
        new_clean_name = new_name.strip().replace("_", " ").title()
        new_key = re.sub(r"[^a-zA-Z0-9_-]", "_", new_name.strip().lower())
        if new_key != old_key:
            # Rename matching files on disk
            for f in list(VOICES_DIR.iterdir()):
                if f.is_file() and f.suffix.lower() in {".wav", ".mp3", ".m4a", ".flac", ".ogg"}:
                    stem = f.stem.lower()
                    if stem == old_key:
                        new_f = VOICES_DIR / f"{new_key}{f.suffix}"
                        f.rename(new_f)
                    elif stem.startswith(f"{old_key}_") or stem.startswith(f"{old_key}-"):
                        rest = stem[len(old_key) :]
                        new_f = VOICES_DIR / f"{new_key}{rest}{f.suffix}"
                        f.rename(new_f)

            # Update takes in target_char
            new_takes = {}
            for emo_k, tinfo in target_char.get("takes", {}).items():
                fname = tinfo.get("filename", "")
                if fname.lower().startswith(old_key):
                    new_fname = new_key + fname[len(old_key) :]
                    new_takes[emo_k] = {
                        "emotion": emo_k,
                        "filename": new_fname,
                        "filepath": f"voices/{new_fname}",
                        "label": tinfo.get("label", emo_k.title()),
                    }
                else:
                    new_takes[emo_k] = tinfo

            target_char["id"] = new_key
            target_char["name"] = new_clean_name
            target_char["takes"] = new_takes

            del store["characters"][old_key]
            store["characters"][new_key] = target_char
            active_key = new_key
        else:
            target_char["name"] = new_clean_name

    # 2. Age update
    if age is not None:
        age_group, age_num = normalize_age_group(age)
        target_char["age"] = age_num
        target_char["age_group"] = age_group

    # 3. Gender update
    if gender:
        g_clean = gender.strip().lower()
        if g_clean in {"male", "female", "neutral"}:
            target_char["gender"] = g_clean

    # 4. Description update
    if description is not None:
        target_char["description"] = description.strip()

    # 5. New Audio Sample update
    if new_audio_path and Path(new_audio_path).exists():
        safe_emo = emotion_key.strip().lower()
        if safe_emo not in EMOTIONS:
            safe_emo = "neutral"
        dest_filename = f"{active_key}_{safe_emo}.wav"
        dest_path = VOICES_DIR / dest_filename

        cmd = [
            FFMPEG_BIN,
            "-y",
            "-i", str(new_audio_path),
            "-af", "silenceremove=start_periods=1:start_duration=0.05:start_threshold=-40dB,areverse,silenceremove=start_periods=1:start_duration=0.05:start_threshold=-40dB,areverse,loudnorm=I=-16:TP=-1.5:LRA=11",
            "-ac", "1",
            "-ar", "24000",
            "-vn",
            str(dest_path),
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg processing failed: {res.stderr}")

        if "takes" not in target_char:
            target_char["takes"] = {}
        target_char["takes"][safe_emo] = {
            "emotion": safe_emo,
            "filename": dest_filename,
            "filepath": f"voices/{dest_filename}",
            "label": EMOTIONS.get(safe_emo, {}).get("title", safe_emo.title()),
        }

    target_char["updated_at"] = datetime.now().isoformat()
    save_characters_store(store)
    return target_char


def delete_character_profile(char_name: str) -> bool:
    """Deletes a character profile and all its recorded takes from disk and JSON."""
    store = load_characters_store()
    old_key = re.sub(r"[^a-zA-Z0-9_-]", "_", char_name.strip().lower())

    target_key = None
    if old_key in store["characters"]:
        target_key = old_key
    else:
        for cid, cinfo in store["characters"].items():
            if cinfo.get("name", "").lower() == char_name.strip().lower():
                target_key = cid
                break

    if not target_key:
        return False

    for f in list(VOICES_DIR.iterdir()):
        if f.is_file() and f.suffix.lower() in {".wav", ".mp3", ".m4a", ".flac", ".ogg"}:
            stem = f.stem.lower()
            if stem == target_key or stem.startswith(f"{target_key}_") or stem.startswith(f"{target_key}-"):
                try:
                    f.unlink()
                except Exception:
                    pass

    if target_key in store["characters"]:
        del store["characters"][target_key]
    save_characters_store(store)
    return True


def git_sync_characters(commit_message: str = None) -> dict:
    """Stages voices/, characters.json, and .gitignore, commits and pushes to GitHub."""
    try:
        # 1. git add
        subprocess.run(
            ["git", "add", "voices/", "characters.json", ".gitignore"],
            cwd=str(WORKSPACE_DIR),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # 2. Check if staged changes exist
        diff_res = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=str(WORKSPACE_DIR),
        )

        committed = False
        if diff_res.returncode != 0:
            msg = commit_message or f"feat(characters): update character voice profiles [{datetime.now().strftime('%Y-%m-%d %H:%M')}]"
            commit_res = subprocess.run(
                ["git", "commit", "-m", msg],
                cwd=str(WORKSPACE_DIR),
                capture_output=True,
                text=True,
            )
            if commit_res.returncode == 0:
                committed = True

        # 3. Get commit hash
        rev_res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            text=True,
        )
        commit_hash = rev_res.stdout.strip() if rev_res.returncode == 0 else ""

        # 4. Attempt git push origin HEAD
        push_res = subprocess.run(
            ["git", "push", "origin", "HEAD"],
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            text=True,
            timeout=15,
        )

        pushed = push_res.returncode == 0
        if pushed:
            return {
                "success": True,
                "committed": committed,
                "pushed": True,
                "commit": commit_hash,
                "message": f"Successfully pushed characters & audio to GitHub! (Commit {commit_hash})",
            }
        else:
            err_msg = push_res.stderr.strip() or push_res.stdout.strip()
            return {
                "success": True,
                "committed": committed,
                "pushed": False,
                "commit": commit_hash,
                "message": f"Saved locally (Commit {commit_hash}). Push note: {err_msg[:160]}",
            }
    except Exception as e:
        return {
            "success": False,
            "committed": False,
            "pushed": False,
            "message": f"Git sync error: {str(e)}",
        }


def get_git_sync_status() -> dict:
    """Returns local git sync status, uncommitted character changes, and remote info."""
    try:
        branch_res = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            text=True,
        )
        branch = branch_res.stdout.strip() or "main"

        status_res = subprocess.run(
            ["git", "status", "--porcelain", "voices/", "characters.json"],
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            text=True,
        )
        dirty_files = [line.strip() for line in status_res.stdout.splitlines() if line.strip()]

        ahead_res = subprocess.run(
            ["git", "rev-list", f"origin/{branch}..HEAD", "--count"],
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            text=True,
        )
        unpushed_count = int(ahead_res.stdout.strip()) if ahead_res.returncode == 0 and ahead_res.stdout.strip().isdigit() else 0

        remote_res = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            text=True,
        )
        remote_url = remote_res.stdout.strip() if remote_res.returncode == 0 else ""

        return {
            "branch": branch,
            "remote": remote_url,
            "uncommitted_changes": len(dirty_files),
            "unpushed_commits": unpushed_count,
            "is_clean": len(dirty_files) == 0 and unpushed_count == 0,
        }
    except Exception as e:
        return {
            "branch": "main",
            "remote": "",
            "uncommitted_changes": 0,
            "unpushed_commits": 0,
            "is_clean": True,
            "error": str(e),
        }


def get_existing_characters() -> list[str]:
    """Extracts unique character names from store and voices/ folder."""
    VOICES_DIR.mkdir(parents=True, exist_ok=True)
    store = load_characters_store()
    characters = set()

    for cid, cdata in store.get("characters", {}).items():
        if cdata.get("name"):
            characters.add(cdata["name"])

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
    """Formats custom voice filenames into clean Character + Profile + Emotion labels."""
    base = Path(filename).stem.lower()
    for key, data in EMOTIONS.items():
        if base.endswith(f"_{key}") or base.endswith(f"-{key}"):
            char_name = base[: -(len(key) + 1)].replace("_", " ").replace("-", " ").strip().title()
            if not char_name:
                char_name = "Character"
            meta = get_character_metadata(char_name)
            profile_tag = f"{meta['age_group'].title()} • {meta['gender'].title()}"
            return f"🎭 Custom: {char_name} ({profile_tag}) — {data['title']} [{filename}]"
    clean_name = base.replace("_", " ").replace("-", " ").strip().title()
    meta = get_character_metadata(clean_name)
    profile_tag = f"{meta['age_group'].title()} • {meta['gender'].title()}"
    return f"🎭 Custom: {clean_name} ({profile_tag}) — Base Voice [{filename}]"


def get_available_voices() -> list[str]:
    """Returns clean, short custom character voices without duplicate takes or predefined presets."""
    VOICES_DIR.mkdir(parents=True, exist_ok=True)
    chars = get_existing_characters()
    labels = []
    for c in chars:
        meta = get_character_metadata(c)
        profile_tag = f"{meta['age_group'].title()} • {meta['gender'].title()}"
        labels.append(f"🎭 Custom: {c} ({profile_tag})")

    return labels


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
    meta = get_character_metadata(display_title)
    profile_badge = f"{meta['age_group'].title()} ({meta['age']}y) • {meta['gender'].title()}"
    header = f"**Character: {display_title}** &nbsp;•&nbsp; `{profile_badge}` &nbsp;•&nbsp; ({recorded_count}/{len(EMOTIONS)} emotions recorded)\n\n"
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

    for i in range(1, len(emotion_keys) + 1):
        candidate = emotion_keys[(curr_idx + i) % len(emotion_keys)]
        if candidate not in existing:
            return candidate

    return current_emotion


def save_emotion_voice(
    audio_path: str,
    char_dropdown_val: str,
    new_char_val: str,
    emotion_key: str,
    age: str = "adult",
    gender: str = "male",
):
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

    # Update characters store & metadata
    update_character_profile(
        char_name=char_name,
        age=age,
        gender=gender,
        new_audio_path=None,  # Already saved by ffmpeg above
    )
    store = load_characters_store()
    if safe_char in store["characters"]:
        store["characters"][safe_char]["takes"][safe_emo] = {
            "emotion": safe_emo,
            "filename": dest_filename,
            "filepath": f"voices/{dest_filename}",
            "label": EMOTIONS.get(safe_emo, {}).get("title", safe_emo.title()),
        }
        save_characters_store(store)

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
        gr.Dropdown(choices=updated_main_voices, value=formatted_main_label),
        gr.Dropdown(choices=updated_char_choices, value=display_char_name),
        gr.Textbox(visible=False, value=display_char_name),
        updated_status,
        gr.Dropdown(choices=EMOTION_CHOICES, value=next_emotion),
        next_data["tip"],
        next_data["hindi"],
        next_data["english"],
        success_msg,
        None,
    )
