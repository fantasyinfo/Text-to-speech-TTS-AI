"""
VoxStudio AI: Single Command Launcher
Starts the FastAPI backend serving the React Vite SaaS UI.
"""

import os
import sys
import webbrowser
import uvicorn
from pathlib import Path

# Set Coqui TOS env vars
os.environ["COQUI_TOC_ACK"] = "1"
os.environ["COQUI_TOS_AGREED"] = "1"

# Import engine to warm up model
from audio_engine import get_tts_model

def main():
    port = int(os.environ.get("PORT", 8000))
    print("=" * 60)
    print("🎙️  VoxStudio AI — Multi-Character SaaS Voice Studio")
    print("    Neural TTS Engine & React Vite")
    print("=" * 60)
    
    print("\n[1/2] Initializing XTTS-v2 voice engine...")
    get_tts_model()
    print("XTTS-v2 engine ready.")

    url = f"http://127.0.0.1:{port}"
    print(f"\n[2/2] Starting SaaS Web Server at: {url}")
    print("=" * 60)
    print(f"👉 Access your studio at: {url}")
    print("=" * 60 + "\n")

    # Automatically open browser
    try:
        webbrowser.open(url)
    except Exception:
        pass

    # Launch Uvicorn server
    uvicorn.run("api_server:app", host="127.0.0.1", port=port, log_level="info")

if __name__ == "__main__":
    main()

