"""
AudioAI: Pro Multi-Character Voice Studio & Project Admin Panel
Optimized for Apple Silicon (M-Series) with Universal Devanagari Linguistic Normalization,
10-Emotion Character Vault, Project Workspaces, and Full Media Library Management.
"""

import os
import re
from pathlib import Path
import gradio as gr

from config import (
    VOICES_DIR,
    OUTPUTS_DIR,
    DEFAULT_PROJECT_NAME,
    EMOTIONS,
    EMOTION_CHOICES,
    NEW_CHAR_OPTION,
    CUSTOM_CSS,
    TAILWIND_THEME,
)
from project_manager import (
    get_all_projects,
    create_new_project,
    get_project_dir,
    list_project_files,
    get_project_file_choices,
    rename_project_audio,
    delete_project_audio,
    create_project_zip,
)
from voice_manager import (
    get_existing_characters,
    get_character_dropdown_choices,
    format_voice_file_label,
    get_available_voices,
    get_character_status_markdown,
    get_next_unrecorded_emotion,
    save_emotion_voice,
)
from audio_engine import generate_voiceover_track, get_tts_model

# Pre-warm model on startup
print("Readying AudioAI Studio...")
get_tts_model()

# Initial state lookups
initial_projects = get_all_projects()
initial_project = initial_projects[0] if initial_projects else DEFAULT_PROJECT_NAME

existing_characters = get_existing_characters()
init_char_choices = get_character_dropdown_choices()
init_char_value = existing_characters[0] if existing_characters else NEW_CHAR_OPTION
init_new_char_visible = (init_char_value == NEW_CHAR_OPTION)

if existing_characters:
    init_emotion = get_next_unrecorded_emotion(existing_characters[0], "neutral")
else:
    init_emotion = "neutral"

init_emotion_data = EMOTIONS[init_emotion]
initial_files = get_project_file_choices(initial_project)
init_file_val = initial_files[0] if initial_files else None

# ---------------------------------------------------------
# Build Gradio UI
# ---------------------------------------------------------
with gr.Blocks(title="AudioAI Studio — Multi-Character Voice Studio") as demo:

    # Global Top Navigation Bar: Project Workspace System
    with gr.Row(elem_classes=["studio-navbar"]):
        with gr.Column(scale=5):
            gr.Markdown(
                """
                # 🎙️ AudioAI Studio & Project Admin
                **Professional Multi-Character Voice Cloning & Filmora Audio Workspace**
                """
            )
        with gr.Column(scale=4):
            with gr.Row():
                active_project_dropdown = gr.Dropdown(
                    choices=initial_projects,
                    value=initial_project,
                    label="📁 Active Project Workspace",
                    scale=3,
                    interactive=True,
                )
                refresh_projects_btn = gr.Button("🔄", scale=1)
            with gr.Row():
                new_project_input = gr.Textbox(
                    placeholder="New Project Name (e.g. Horror_Ep1)...",
                    label="Create Project Folder",
                    scale=3,
                    lines=1,
                )
                create_project_btn = gr.Button("➕ Create", variant="primary", scale=1)
        with gr.Column(scale=3):
            gr.Markdown("**📦 Batch Project Export**")
            export_project_zip_btn = gr.Button("📦 Download All Audio as ZIP", variant="secondary")
            zip_download_file = gr.File(label="Project ZIP Download", interactive=False, visible=False)

    project_status_banner = gr.Markdown(f"📂 *Current Workspace:* **`outputs/{initial_project}/`**")

    # Main Tabs Interface
    with gr.Tabs():

        # =========================================================
        # TAB 1: 🎙️ VOICEOVER STUDIO
        # =========================================================
        with gr.Tab("🎙️ Voiceover Studio"):
            with gr.Row():
                # LEFT COLUMN: Script, Controls, and Emotion Studio Drawer
                with gr.Column(scale=3):
                    script_input = gr.Textbox(
                        label="Scene Script / Dialogue (कहानी या संवाद)",
                        placeholder="Paste your Hindi or English dialogue here...\n\nExample: दोपहर का 1 बजा है। प्रिया की desk पर मम्मी का बनाया गरमागरम टिफिन रखा है।",
                        lines=5,
                    )

                    with gr.Row():
                        clip_title_input = gr.Textbox(
                            label="Scene / Take Title (Optional)",
                            placeholder="e.g. Scene_1_Intro or Priya_Reaction",
                            scale=3,
                            lines=1,
                        )
                        voice_dropdown = gr.Dropdown(
                            choices=get_available_voices(),
                            value=get_available_voices()[0] if get_available_voices() else None,
                            label="Character Voice & Emotion (पात्र और भाव चुनें)",
                            scale=4,
                        )

                    with gr.Row():
                        refresh_voices_btn = gr.Button("🔄 Refresh Voices", scale=1)
                        toggle_studio_btn = gr.Button("🎙️ Clone / Add Voice", variant="secondary", scale=2)

                    # Collapsible Character Emotion Voice Studio Drawer
                    studio_is_open = gr.State(False)
                    with gr.Column(visible=False, elem_classes=["studio-drawer"]) as studio_drawer:
                        with gr.Row():
                            gr.Markdown("### 🎭 Character Emotion Voice Studio (Record & Align Realistic Emotions)")
                            close_studio_btn = gr.Button("✕ Close Studio", variant="secondary", size="sm")

                        gr.Markdown(
                            """
                            **💡 Why Record Separate Emotions?**
                            In real storytelling, human voices shift dynamically when **crying, angry, laughing, or tired**.
                            By recording a short 10–15s sample for each emotion, your character retains their vocal identity
                            while sounding authentic in every scene!
                            """
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
                                placeholder="e.g. Gaurav, Mohan, Priya, Villain",
                                visible=init_new_char_visible,
                                scale=2,
                            )
                            emotion_selector = gr.Dropdown(
                                choices=EMOTION_CHOICES,
                                value=init_emotion,
                                label="2. Choose Emotion to Record (भाव चुनें)",
                                scale=2,
                            )

                        status_badges_box = gr.Markdown(
                            get_character_status_markdown(init_char_value)
                            if init_char_value != NEW_CHAR_OPTION
                            else "💡 *Type a new Character Name above to start creating your character profile.*"
                        )

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

                        audio_recorder = gr.Audio(
                            sources=["microphone", "upload"],
                            type="filepath",
                            label="3. Record or Upload Audio Sample (10–20 sec)",
                        )

                        with gr.Row():
                            save_emotion_btn = gr.Button("💾 Save This Emotion to Character Profile", variant="primary", scale=2)
                            done_and_close_btn = gr.Button("✨ Done & Return to Studio", variant="secondary", scale=1)

                        save_feedback = gr.Markdown("")

                    with gr.Row():
                        lang_radio = gr.Radio(
                            choices=["Hindi (hi)", "English (en)"],
                            value="Hindi (hi)",
                            label="Spoken Language",
                            scale=1,
                        )
                        speed_slider = gr.Slider(
                            minimum=0.75,
                            maximum=3.0,
                            value=1.0,
                            step=0.05,
                            label="Speaking Speed",
                            scale=2,
                        )

                    generate_btn = gr.Button("🚀 Generate MP3 Audio for Filmora", variant="primary", size="lg")

                # RIGHT COLUMN: Audio Playback, File Download & Generation Logs
                with gr.Column(scale=2):
                    gr.Markdown("### 🎧 Voiceover Preview & Filmora Export")
                    audio_player = gr.Audio(label="Preview Audio", type="filepath")
                    download_file = gr.File(label="Download 192kbps MP3 for Filmora")
                    status_box = gr.Textbox(label="Status / Generation Log", interactive=False, lines=2)

                    gr.Markdown(
                        """
                        ---
                        ### 🎬 Filmora Timeline Storytelling Tips:
                        1. **Pick Character & Emotion**: Select your character with matching emotion (e.g. *Sad, Angry, Crying*).
                        2. **Dialogue Transitions**: Generate dialogues beat-by-beat to create authentic emotional transitions.
                        3. **Automatic Project Folder**: Every take is safely archived into your active project folder (`outputs/<project_name>/`).
                        4. **Direct Drag**: Drag MP3s directly from the download box or project folder straight into Filmora!
                        """
                    )

        # =========================================================
        # TAB 2: 🗂️ PROJECT MEDIA LIBRARY & ADMIN PANEL
        # =========================================================
        with gr.Tab("🗂️ Project Media Library & Admin Panel"):
            gr.Markdown(
                """
                ### 🗂️ Project Media Library (Admin Panel)
                Manage all audio files generated inside your current project workspace. Preview any audio take,
                rename files for easy organization in Filmora, delete unwanted takes, or download tracks.
                """
            )

            with gr.Row():
                # LEFT: File List & Preview
                with gr.Column(scale=3):
                    with gr.Row():
                        project_files_dropdown = gr.Dropdown(
                            choices=initial_files,
                            value=init_file_val,
                            label="🎵 Select Audio Track from Active Project",
                            scale=3,
                        )
                        refresh_files_btn = gr.Button("🔄 Refresh Files", scale=1)

                    admin_audio_player = gr.Audio(
                        label="Selected Track Preview",
                        type="filepath",
                        value=str(Path(OUTPUTS_DIR / initial_project / init_file_val)) if init_file_val else None,
                    )
                    admin_file_download = gr.File(
                        label="Direct Download Selected Track",
                        value=str(Path(OUTPUTS_DIR / initial_project / init_file_val)) if init_file_val else None,
                    )

                # RIGHT: File Management Tools (Rename / Delete)
                with gr.Column(scale=2):
                    gr.Markdown("#### ✏️ Track Management Actions")
                    rename_input = gr.Textbox(
                        label="Rename Selected Audio",
                        value=Path(init_file_val).stem if init_file_val else "",
                        placeholder="Enter new filename without extension...",
                        lines=1,
                    )
                    rename_btn = gr.Button("✏️ Rename Audio Track", variant="primary")

                    gr.Markdown("---")
                    gr.Markdown("#### 🗑️ Remove Track")
                    delete_btn = gr.Button("🗑️ Delete Selected Audio", variant="stop")

                    admin_status_box = gr.Textbox(
                        label="Admin Panel Action Status",
                        interactive=False,
                        lines=2,
                        value="Ready.",
                    )

        # =========================================================
        # TAB 3: 🎭 CHARACTER VAULT
        # =========================================================
        with gr.Tab("🎭 Character Voice Vault"):
            gr.Markdown(
                """
                ### 🎭 Character Roster & Emotion Coverage
                Review all registered characters and check which emotional profiles are recorded.
                """
            )
            vault_char_dropdown = gr.Dropdown(
                choices=get_existing_characters(),
                value=get_existing_characters()[0] if get_existing_characters() else None,
                label="Select Character to Inspect",
            )
            vault_status_markdown = gr.Markdown(
                get_character_status_markdown(get_existing_characters()[0])
                if get_existing_characters()
                else "💡 *No custom characters created yet. Use the Voice Studio to clone your first character!*"
            )

    # ---------------------------------------------------------
    # Event Handlers & Callbacks
    # ---------------------------------------------------------

    # 1. Project Management Events
    def on_create_project(name: str):
        new_name, updated_choices, msg = create_new_project(name)
        new_files = get_project_file_choices(new_name)
        banner = f"📂 *Current Workspace:* **`outputs/{new_name}/`**"
        return (
            gr.Dropdown(choices=updated_choices, value=new_name),  # active_project_dropdown
            "",                                                    # clear new_project_input
            banner,                                                # project_status_banner
            gr.Dropdown(choices=new_files, value=new_files[0] if new_files else None),  # project_files_dropdown
            msg,                                                   # status log
        )

    create_project_btn.click(
        fn=on_create_project,
        inputs=new_project_input,
        outputs=[active_project_dropdown, new_project_input, project_status_banner, project_files_dropdown, status_box],
    )

    def on_project_change(selected_project: str):
        files = get_project_file_choices(selected_project)
        first_file = files[0] if files else None
        first_path = str(Path(OUTPUTS_DIR / selected_project / first_file)) if first_file else None
        stem = Path(first_file).stem if first_file else ""
        banner = f"📂 *Current Workspace:* **`outputs/{selected_project}/`**"
        return (
            banner,
            gr.Dropdown(choices=files, value=first_file),
            first_path,
            first_path,
            stem,
            f"Switched active project to '{selected_project}'.",
        )

    active_project_dropdown.change(
        fn=on_project_change,
        inputs=active_project_dropdown,
        outputs=[
            project_status_banner,
            project_files_dropdown,
            admin_audio_player,
            admin_file_download,
            rename_input,
            admin_status_box,
        ],
    )

    refresh_projects_btn.click(
        fn=lambda: gr.Dropdown(choices=get_all_projects()),
        outputs=active_project_dropdown,
    )

    def on_export_zip(project_name: str):
        try:
            zip_path = create_project_zip(project_name)
            return gr.File(value=zip_path, visible=True), f"✅ ZIP archive ready for '{project_name}'!"
        except Exception as e:
            raise gr.Error(str(e))

    export_project_zip_btn.click(
        fn=on_export_zip,
        inputs=active_project_dropdown,
        outputs=[zip_download_file, status_box],
    )

    # 2. Studio Drawer Toggle Events
    def toggle_studio(is_open):
        new_state = not is_open
        btn_text = "✕ Close Voice Studio" if new_state else "🎙️ Clone / Add Voice"
        return gr.update(visible=new_state), btn_text, new_state

    def close_studio():
        return gr.update(visible=False), "🎙️ Clone / Add Voice", False

    toggle_studio_btn.click(
        fn=toggle_studio,
        inputs=studio_is_open,
        outputs=[studio_drawer, toggle_studio_btn, studio_is_open],
    )

    close_studio_btn.click(
        fn=close_studio,
        outputs=[studio_drawer, toggle_studio_btn, studio_is_open],
    )

    done_and_close_btn.click(
        fn=close_studio,
        outputs=[studio_drawer, toggle_studio_btn, studio_is_open],
    )

    # 3. Emotion Studio Drawer Dynamic Updates
    def on_emotion_change(emo_key):
        data = EMOTIONS.get(emo_key, EMOTIONS["neutral"])
        return data["tip"], data["hindi"], data["english"]

    emotion_selector.change(
        fn=on_emotion_change,
        inputs=emotion_selector,
        outputs=[vocal_coach_tip, hindi_prompt_box, english_prompt_box],
    )

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

    char_dropdown.change(
        fn=on_char_dropdown_change,
        inputs=char_dropdown,
        outputs=[new_char_input, status_badges_box, emotion_selector, vocal_coach_tip, hindi_prompt_box, english_prompt_box],
    )

    new_char_input.change(
        fn=lambda val: get_character_status_markdown(val) if val and val.strip() else "💡 *Type a new Character Name above to start creating your character profile.*",
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

    refresh_voices_btn.click(
        fn=lambda: gr.Dropdown(choices=get_available_voices()),
        outputs=voice_dropdown,
    )

    # 4. Audio Synthesis Generation
    def run_synthesis(script, voice, lang, speed, project, clip_title):
        player_path, dl_path, log = generate_voiceover_track(
            script_text=script,
            voice_choice=voice,
            custom_upload=None,
            language_label=lang,
            speed=speed,
            project_name=project,
            clip_title=clip_title,
        )
        updated_files = get_project_file_choices(project)
        return (
            player_path,
            dl_path,
            log,
            gr.Dropdown(choices=updated_files, value=Path(dl_path).name),
        )

    generate_btn.click(
        fn=run_synthesis,
        inputs=[
            script_input,
            voice_dropdown,
            lang_radio,
            speed_slider,
            active_project_dropdown,
            clip_title_input,
        ],
        outputs=[audio_player, download_file, status_box, project_files_dropdown],
    )

    # 5. Admin Panel File Actions (Select, Rename, Delete, Refresh)
    def on_select_project_file(project_name: str, filename: str):
        if not filename:
            return None, None, "", "No track selected."
        target_path = Path(OUTPUTS_DIR / project_name / filename)
        if target_path.exists():
            return str(target_path), str(target_path), target_path.stem, f"Loaded '{filename}'."
        return None, None, "", f"File '{filename}' not found."

    project_files_dropdown.change(
        fn=on_select_project_file,
        inputs=[active_project_dropdown, project_files_dropdown],
        outputs=[admin_audio_player, admin_file_download, rename_input, admin_status_box],
    )

    def on_rename_file(project_name: str, old_file: str, new_name: str):
        renamed_file, updated_choices, msg = rename_project_audio(project_name, old_file, new_name)
        new_path = str(Path(OUTPUTS_DIR / project_name / renamed_file)) if renamed_file else None
        stem = Path(renamed_file).stem if renamed_file else ""
        return (
            gr.Dropdown(choices=updated_choices, value=renamed_file),
            new_path,
            new_path,
            stem,
            msg,
        )

    rename_btn.click(
        fn=on_rename_file,
        inputs=[active_project_dropdown, project_files_dropdown, rename_input],
        outputs=[
            project_files_dropdown,
            admin_audio_player,
            admin_file_download,
            rename_input,
            admin_status_box,
        ],
    )

    def on_delete_file(project_name: str, filename: str):
        updated_choices, msg = delete_project_audio(project_name, filename)
        first_file = updated_choices[0] if updated_choices else None
        first_path = str(Path(OUTPUTS_DIR / project_name / first_file)) if first_file else None
        stem = Path(first_file).stem if first_file else ""
        return (
            gr.Dropdown(choices=updated_choices, value=first_file),
            first_path,
            first_path,
            stem,
            msg,
        )

    delete_btn.click(
        fn=on_delete_file,
        inputs=[active_project_dropdown, project_files_dropdown],
        outputs=[
            project_files_dropdown,
            admin_audio_player,
            admin_file_download,
            rename_input,
            admin_status_box,
        ],
    )

    refresh_files_btn.click(
        fn=lambda project: gr.Dropdown(choices=get_project_file_choices(project)),
        inputs=active_project_dropdown,
        outputs=project_files_dropdown,
    )

    # 6. Character Vault Event
    vault_char_dropdown.change(
        fn=get_character_status_markdown,
        inputs=vault_char_dropdown,
        outputs=vault_status_markdown,
    )


if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        inbrowser=True,
        theme=TAILWIND_THEME,
        css=CUSTOM_CSS,
    )
