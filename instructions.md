# 🎙️ VoxStudio AI: Multi-Character SaaS Voice Studio (Apple Silicon)

A local, 100% private, and unlimited Text-to-Speech (TTS) and Voice Cloning SaaS web application built with **React + Vite + Tailwind CSS**, powered by **Coqui XTTS-v2** and **FastAPI** on Apple Silicon (M-Series).

Engineered to match modern SaaS standards (like **ElevenLabs** and modern executive dashboards) to generate high-quality **Hindi (`hi`)** and **English (`en`)** storytelling tracks with **10 distinct character emotions**, dynamic project workspaces, inline audio renaming, and direct **192kbps MP3 export** for **Filmora**, **Premiere Pro**, and **DaVinci Resolve**.

---

## 📁 1. Project Directory Layout

```text
audioAI/
├── run.py                 # Single-command launcher (FastAPI + React SaaS UI)
├── api_server.py          # High-performance FastAPI REST API backend
├── job_manager.py         # Non-blocking background synthesis queue, real-time ETA & SSE streams
├── app.py                 # Alternative Gradio interface (<450 lines)
├── config.py              # Central settings, paths, styles, presets & 10 emotion prompts
├── text_processor.py      # Universal 15-Layer Devanagari Linguistic Normalization Engine
├── project_manager.py     # Workspace isolation, project creation, audio rename, delete & ZIP export
├── voice_manager.py       # Character profile vault, emotion badges, and reference voice saving
├── audio_engine.py        # Apple Silicon XTTS-v2 inference, sentence pacing & 192kbps MP3 export
├── frontend/              # Modern React + Vite + Tailwind CSS SaaS Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx           # Obsidian navigation sidebar with workspace sections
│   │   │   ├── TopNavbar.jsx         # Project switcher, new project modal & ZIP export
│   │   │   ├── StudioView.jsx        # ElevenLabs-style TTS studio & live waveform visualizer
│   │   │   ├── JobProgressWidget.jsx # Real-time background progress bar with live % & ETA
│   │   │   ├── DashboardView.jsx     # Executive AP & audio metrics dashboard
│   │   │   ├── ProjectsView.jsx      # Workspace folder manager with cards
│   │   │   ├── MediaLibraryView.jsx  # Complete audio takes browser with inline rename
│   │   │   ├── CharacterVaultView.jsx# Character emotion matrix & sample auditions
│   │   │   ├── RecordEmotionModal.jsx# Vocal coach recording studio with Hindi/English scripts
│   │   │   └── AudioPlayerBar.jsx    # Persistent bottom scrubber player with speed control
│   │   ├── App.jsx                   # Central state management & API coordinator
│   │   └── index.css                 # Dark obsidian theme & sleek scrollbars
│   ├── dist/                         # Pre-compiled high-performance production build
│   └── package.json                  # React 18, Vite 5, Lucide React, Tailwind CSS
├── requirements.txt       # Python dependencies (PyTorch, Coqui XTTS-v2, FastAPI, FFmpeg)
├── .venv/                 # Dedicated Apple Silicon Python 3.11 virtual environment
├── voices/                # Stored character voice reference files by emotion
└── outputs/               # Isolated project workspace folders
    ├── Default_Project/   # Default audio exports (older takes safely preserved)
    └── <Project_Name>/    # Dedicated subfolder for each project's MP3 takes
```

---

## ⚡ 2. Quick Start (SaaS React + Vite Experience)

### Step 1: Activate Virtual Environment
Open your terminal in `/Users/gauravsharma/Documents/audioAI`:

```bash
cd /Users/gauravsharma/Documents/audioAI
source .venv/bin/activate
```

### Step 2: Launch the Studio
```bash
python run.py
```

Your browser will automatically open:
👉 **http://127.0.0.1:8000**

*(Optional) For live React frontend development with hot-module reloading:*
```bash
cd frontend
npm run dev
```
*(Runs on `http://localhost:5173` with automatic API proxying to FastAPI on port 8000).*

---

## 🎭 3. Multi-Emotion Character System

In realistic storytelling and film editing, a human character's voice changes completely depending on what happens in the scene. A character speaking while **crying** sounds entirely different from when they are **angry**, **excited**, or **exhausted**.

### How XTTS-v2 Emotion Conditioning Works:
XTTS-v2 extracts the pitch dynamics, formant contours, and vocal energy from your 10–15s reference sample. By recording separate emotional samples for your character (e.g. `gaurav_sad.wav`, `gaurav_angry.wav`), XTTS-v2 synthesizes your dialogue with that **exact emotional prosody** while preserving your character's voice identity.

### How to Create an Emotional Character Profile (Clean On-Demand Workflow):
1. In the Web UI, click the **`🎙️ Clone / Add Voice`** button next to the voice dropdown.
2. The **🎭 Character Emotion Studio** smoothly expands on demand:
   - **For a New Character**: Choose `➕ [Create New Character...]` and enter the name once (e.g. `Gaurav`, `Mohan`, `Dadi Ji`).
   - **For Existing Characters**: Simply select their name from the dropdown (zero typos, zero re-typing!).
3. Read the corresponding **Vocal Coach Tip** and **Acting Script** into the microphone for 10–15 seconds.
4. Click **💾 Save This Emotion to Character Profile**:
   - The audio is normalized to 24kHz mono PCM WAV and saved into `voices/<character>_<emotion>.wav`.
   - Your character's emotion badges update with a green checkmark (`✅`).
   - The studio automatically cues up the next unrecorded emotion!
5. Click **`✨ Done & Return to Studio`** (or `✕ Close Studio`) to return to the clean homepage and generate speech!

---

## 📖 4. The 10 Acting Emotions: Vocal Techniques & Scripts

Below are the 10 supported acting emotions. Use these exact acting prompts when recording each emotion:

---

### 1. 🎙️ Neutral / Storyteller (शांत / कथावाचक)
- **Vocal Acting Tip:** Sit tall with relaxed shoulders. Keep your pitch in a comfortable mid-range with a calm, steady cadence. Breathe from your diaphragm. Enunciate clearly without rushing.
- **🇮🇳 Hindi Script:**
  > *"पुराने जमाने की बात है, जब घने जंगलों के बीच एक शांत नदी बहती थी। वहां के लोग कहते थे कि उस नदी के पानी में एक अनोखा जादू है, जो हर सच्चे इंसान के दिल की बात समझ लेता था। उस रात, हवा में एक अजीब सी ठंडक थी।"*
- **🇬🇧 English Script:**
  > *"Deep within the ancient mountains, where the mist never seemed to clear, an old traveler began his long journey toward the silent valley. He knew the road ahead was filled with unexpected turns, yet he took a steady breath and stepped forward into the unknown."*

---

### 2. 😢 Sad & Grieving (उदास / गमगीन)
- **Vocal Acting Tip:** Drop your physical energy and drop your chin slightly. Allow a lower pitch with gentle downward pitch inflections at sentence ends. Speak with heavy, prolonged exhalations and solemn pauses.
- **🇮🇳 Hindi Script:**
  > *"सब कुछ इतनी जल्दी खत्म हो जाएगा, मैंने कभी सपने में भी नहीं सोचा था... हर उम्मीद, हर वादा आज खामोश हो गया। अब इन वीरान रास्तों पर मेरा कोई नहीं रहा... सिर्फ एक गहरी तन्हाई बची है।"*
- **🇬🇧 English Script:**
  > *"Everything slipped away so quickly... I never imagined standing here alone, watching every promise we made crumble into cold, hollow silence. There is nowhere left for me to go."*

---

### 3. 😭 Crying & Choked (रोते हुए / रुंधा गला / बेबसी)
- **Vocal Acting Tip:** Slightly tense your throat and swallow hard before speaking. Introduce a slight crack or tremor in your voice. Take shaky, audible breaths or sniffles between short, broken clauses as if fighting back tears.
- **🇮🇳 Hindi Script:**
  > *"(रुंधे गले से) क्यों किया उसने ऐसा... मेरी क्या गलती थी? (हल्की सिसकी) मैं... मैं अब और दर्द नहीं सह सकता... भगवान के लिए मुझे अकेला छोड़ दो... सब कुछ बिखर गया है..."*
- **🇬🇧 English Script:**
  > *"(Choked breath / sniffle) Why did it have to end like this... what did I do wrong? (Voice cracking) Please... I just can't hold back the tears anymore... it hurts too much to pretend I'm okay."*

---

### 4. 😂 Laughing & Giggling (हंसते हुए / खिलखिलाहट)
- **Vocal Acting Tip:** Smile widely so your cheekbones lift (this naturally brightens your acoustic resonance). Incorporate soft chuckles, breath pulses, and bouncy melodic pitch leaps between words.
- **🇮🇳 Hindi Script:**
  > *"(हंसते हुए) अरे भाई! तुमने उसकी शक्ल देखी जब वो गिरा? हाहाहा! सच कह रहा हूँ, मैंने आज तक अपनी ज़िंदगी में ऐसा मजेदार ड्रामा कभी नहीं देखा! रुक जाओ, पेट में दर्द हो रहा है हंसते-हंसते!"*
- **🇬🇧 English Script:**
  > *"(Laughing / chuckling) Oh you've got to be kidding me! Did you see his face when the bucket tipped over? Haha! I swear that is the funniest thing that has happened all year! Stop, my sides hurt from laughing!"*

---

### 5. 🤩 Excited & Thrilled (उत्साहित / रोमांचित)
- **Vocal Acting Tip:** Expand your chest, raise your eyebrows, and lean in. Speak with high vocal energy, elevated pitch, fast tempo, and punchy, enthusiastic upward inflection.
- **🇮🇳 Hindi Script:**
  > *"अरे वाह! हम आखिरकार जीत गए! मुझे तो अपनी आँखों पर यकीन ही नहीं हो रहा कि हमने ये कर दिखाया! चलो जल्दी सामान बांधो, आज रात हमारा सबसे बड़ा जश्न होने वाला है!"*
- **🇬🇧 English Script:**
  > *"Yes! We actually did it! I can't believe our plan worked out so completely! Grab your bags right now, the grand adventure is finally beginning!"*

---

### 6. 😡 Angry & Furious (क्रोधित / गुस्सैल)
- **Vocal Acting Tip:** Clench your fists and lock your core. Deliver words with hard, sharp consonants (k, t, p, d) and forceful chest projection. Maintain an intense, unwavering, commanding tone.
- **🇮🇳 Hindi Script:**
  > *"बस, बहुत हो चुका! तुम्हारी इतनी हिम्मत कैसे हुई मेरे पीठ पीछे यह सब करने की? अगर एक और झूठ बोला ना, तो अंजाम भुगतने के लिए तैयार रहना! निकल जाओ मेरी नज़रों के सामने से!"*
- **🇬🇧 English Script:**
  > *"Enough! How dare you stand there and look me in the eye after what you did! Don't you dare say another word, or I swear you will regret this for the rest of your life!"*

---

### 7. 😨 Scared & Whispering (डरा हुआ / फुसफुसाहट / खौफ)
- **Vocal Acting Tip:** Drop volume to an intense stage whisper. Use rapid, shallow breaths. Add nervous, tense pauses as if listening for a predator or footsteps approaching in the dark.
- **🇮🇳 Hindi Script:**
  > *"(धीमी कांपती आवाज़ में) श्शश... बिल्कुल चुप रहो! वो दरवाज़ा धीरे-धीरे खुल रहा है... कोई है जो अँधेरे में हमारे बिल्कुल पीछे खड़ा है... सांस भी मत लेना!"*
- **🇬🇧 English Script:**
  > *"(Tense whisper) Shh... be completely quiet! Did you hear that heavy thud in the hallway? Someone is turning the doorknob right now... don't make a sound, hide!"*

---

### 8. 😴 Tired & Exhausted (थका हुआ / हांफता हुआ / कमजोर)
- **Vocal Acting Tip:** Slump in your chair and let your jaw hang loose. Speak at the tail end of your exhalations with sluggish syllables, breathy timbre, and exhausted trailing pauses.
- **🇮🇳 Hindi Script:**
  > *"मुझमें अब... ज़रा भी जान नहीं बची। आँखें बंद हो रही हैं... पैर लड़खड़ा रहे हैं। मुझे... बस थोड़ी देर के लिए सोने दो... मुझे यहीं छोड़ो और तुम आगे बढ़ो..."*
- **🇬🇧 English Script:**
  > *"I can barely take another step... my vision is blurring, and every breath feels like carrying lead. Just leave me here... and go on without me... I can't go any further..."*

---

### 9. 😏 Funny & Sarcastic (मजाकिया / तंज भरा)
- **Vocal Acting Tip:** Deliver with a mischievous smirk and mock-sweet pitch slides. Roll words with dry irony and pause theatrically before the punchline.
- **🇮🇳 Hindi Script:**
  > *"वाह भाई साहब! क्या अद्भुत दिमाग लगाया है आपने! तालियां बजनी चाहिए इस पर! अगली बार जब ऐसा क्रांतिकारी आइडिया आए ना, तो पहले मुझे भाग जाने का मौका दे देना!"*
- **🇬🇧 English Script:**
  > *"Oh brilliant! Pure genius of the century! What a revolutionary plan! Next time you get a brainstorm like that, please give me a five-minute head start to run away!"*

---

### 10. 💖 Romantic & Gentle (प्यार भरा / कोमल / धीमा)
- **Vocal Acting Tip:** Speak close to the microphone with warm, soft breath. Keep your vocal tone intimate, velvety, low-pitched, and unhurried.
- **🇮🇳 Hindi Script:**
  > *"जब भी तुम करीब होते हो, दुनिया का सारा शोर जैसे अचानक थम जाता है। तुम्हारी एक मुस्कान ही मेरे हर मुश्किल दिन को रोशन कर देती है। हमेशा मेरे साथ रहना।"*
- **🇬🇧 English Script:**
  > *"Whenever you are near, the entire world seems to soften into quiet peace. In all this chaos, being right here with you is the only place that truly feels like home."*

---

## 🎬 5. Filmora Timeline Workflow

1. **Step-by-Step Scene Generation**:
   - For Scene 1 (The opening narration): Select `🎭 Custom: Gaurav — Neutral / Storyteller`. Paste dialogue and click **🚀 Generate**.
   - For Scene 2 (Character receives bad news): Select `🎭 Custom: Gaurav — Sad & Grieving`. Paste dialogue and click **🚀 Generate**.
   - For Scene 3 (Emotional breakdown): Select `🎭 Custom: Gaurav — Crying & Choked`. Paste dialogue and click **🚀 Generate**.
   - For Scene 4 (Confrontation): Select `🎭 Custom: Gaurav — Angry & Furious`. Paste dialogue and click **🚀 Generate**.
2. **Audio File Organization**:
   - Every file in `outputs/` is timestamped and prefixed with the character and emotion (e.g. `Custom__Gaurav___Crying___20261112_104500.mp3`).
3. **Filmora Timeline**:
   - Drag the `.mp3` files in sequence directly into the audio track of your Filmora project.
   - The character maintains the exact same voice identity across the entire film while delivering authentic, realistic emotions for each scene!

---

## ⚡ 6. Universal Hindi & Devanagari Linguistic Normalization Engine

To eliminate mispronunciations, tokenization stutter, and alignment glitches across all Hindi texts, `app.py` runs a 10-layer pre-processing engine:

1. **Universal Suffix & Conjunct Normalization (`-िया`, `-ियों`, `-ियां`)**:
   - In XTTS-v2's 515-token Devanagari vocabulary, the subword `िया` is an isolated suffix morpheme. When preceded by any conjunct (`प्र`, `क्र`, `त्र`) or feminine plural stem (`कहानियां`, `गाड़ियां`, `रोटियां`, `बेटियां`, `छुट्टियां`), XTTS treats the stem as a bare consonant and stumbles.
   - The engine automatically maps:
     - Names & Conjuncts: `प्रिया` ➔ `प्रीया`, `सुप्रिया` ➔ `सुप्रीया`, `क्रिया` ➔ `क्रीया`, `शुक्रिया` ➔ `शुक्रीया`, `प्रतिक्रिया` ➔ `प्रतिक्रीया`, `स्त्रियां` ➔ `स्त्रीयां`.
     - Feminine Plurals: `कहानियां` ➔ `कहानीयां`, `गाड़ियां` ➔ `गाड़ीयां`, `रोटियां` ➔ `रोटीयां`, `घड़ियां` ➔ `घड़ीयां`, `छुट्टियां` ➔ `छुट्टीयां`, `बेटियां` ➔ `बेटीयां`, `खुशियां` ➔ `खुशीयां`.
   - Core root verbs (`किया`, `दिया`, `लिया`, `पिया`, `जिया`, `सिया`) are protected.

2. **Nukta Normalization (`़` - U+093C)**:
   - Standalone nuktas force XTTS into single-letter token splits (`ख़ास` ➔ `['ख', '़', 'ा', 'स']`), causing clicks and hesitation.
   - The engine automatically normalizes: `क़` ➔ `क`, `ख़` ➔ `ख`, `ग़` ➔ `ग`, `ज़ि` ➔ `जि` (`ज़िंदगी` ➔ `जिंदगी`), `फ़ि` ➔ `फि` (`फ़िक्र` ➔ `फिक्र`), `साफ़` ➔ `साफ`.

3. **Chandrabindu (`ँ`) to Anusvara (`ं`)**:
   - `ँ` is an isolated single token in XTTS (e.g. `हँसना` ➔ `['ह', 'ँ', 'स', 'ना']`).
   - Normalizing to `ं` allows XTTS to use native pre-fused subwords like `ंस` (`हंसना` ➔ `['ह', 'ंस', 'ना']`), `आंखें`, `गांव`, `चांद`.

4. **Visarga (`ः`) Cleanup**:
   - Eliminates mid-word tokenization breaks (`दुःख` / `दु:ख` ➔ `दुख`, `स्वतः` ➔ `स्वत`, `क्रमशः` ➔ `क्रमश`).

5. **Invisible Unicode & Formatting Stripping**:
   - Removes zero-width non-joiners (`\u200c`), zero-width joiners (`\u200d`), zero-width spaces (`\u200b`), and BOMs (`\ufeff`) that frequently corrupt pasted text from WhatsApp, Word, or web pages.

6. **Numbers, Times, Percentages, Fractions & Currency**:
   - Devanagari numerals (`०-९`) ➔ `0-9`
   - Numbers ➔ Spoken Hindi words (`1` ➔ `एक`, `100` ➔ `एक सौ`)
   - Clock times: `1:30` / `10:00 बजे` ➔ `एक बजकर तीस मिनट` / `दस बजे`
   - Fractions: `1/2` ➔ `आधा`, `1/4` ➔ `एक चौथाई`, `1.5` ➔ `डेढ़`, `2.5` ➔ `ढाई`
   - Currencies & Percentages: `₹500` ➔ `पांच सौ रुपये`, `25%` ➔ `पच्चीस प्रतिशत`

7. **Hyphenated Reduplicated Words**:
   - Unifies hyphenated word pairs (`गरमा-गरम` ➔ `गरमा गरम`, `धीरे-धीरे` ➔ `धीरे धीरे`, `साथ-साथ` ➔ `साथ साथ`) to eliminate mid-phrase pauses.

8. **Automatic Hinglish Loanword Transliteration (150+ words)**:
   - Everyday English words written in Latin characters (`desk`, `tiffin`, `office`, `hospital`, `doctor`, `school`, `room`, `phone`, `call`, `car`, `train`, etc.) are automatically converted to clean Devanagari (`डेस्क`, `टिफिन`, `ऑफिस`, `अस्पताल`).

9. **Natural Storytelling Breath Cadence**:
   - Sentences are segmented beat-by-beat using Purna Viram (`।`) and punctuation boundaries. Trailing vocoder air is trimmed from each clause and combined with a realistic 280ms breathing pause for tight Filmora pacing.

10. **Broadcast Audio Normalization**:
    - Reference voice recordings and final MP3 exports undergo automated silence trimming and EBU R128 loudness normalization (`-16 LUFS`), ensuring crystal-clear voice cloning and zero dead air.

---

## 🗂️ 6. Project Workspaces & Media Library Admin Panel

AudioAI includes a complete multi-project workspace system designed for organizing full storytelling series, film episodes, and commercial spots.

### 📁 1. Dedicated Project Workspaces:
- **Active Project Selector**: Located in the top navigation bar. Every generated audio take is automatically routed into `outputs/<project_name>/`.
- **Instant Project Creation**: Enter a project name (e.g., `Horror_Ep1`, `Podcast_Episode_5`, `Commercial_Ad`) and click **➕ Create**. The workspace folder is immediately created and made active.
- **Persistent Project Isolation**: Switch between different projects anytime from the homepage dropdown to instantly access older takes and recordings without cluttering a single directory.

### 🎛️ 2. Media Library & Admin Panel:
Navigate to the **🗂️ Project Media Library & Admin Panel** tab:
1. **Audio Browser**: Browse all audio takes generated inside the active project workspace.
2. **Instant Preview**: Listen to any take using the built-in waveform player.
3. **Direct Renaming**: Rename any audio file directly from the UI (e.g. rename `Custom_Test01_20261112.mp3` to `Scene_1_Take_3_Final`). File extensions (`.mp3`) are automatically preserved.
4. **Track Deletion**: Remove unwanted takes with 1-click using **🗑️ Delete Selected Audio**.
5. **Direct Download**: Download individual high-grade 192kbps MP3s straight to your Mac.

### 📦 3. One-Click Batch ZIP Export:
- In the top navigation bar or Admin Panel, click **📦 Download All Audio as ZIP**.
- AudioAI compresses all audio takes in the active project into a clean archive (e.g., `Horror_Ep1_Audio_Export_20261112.zip`) for instant download and archiving.

---

## ⚡ 7. Non-Blocking Background Synthesis & Real-Time ETA Engine

Voiceover synthesis operates on a dedicated background worker thread pool (`job_manager.py`) so the React frontend **never hangs, locks, or freezes**.

### 🚀 Key Technical Features:
1. **Instant Enqueue (<30ms)**:
   - When clicking **Generate MP3 Audio for Filmora**, the request is immediately dispatched into the background queue.
   - The user can continue browsing projects, auditioning voices in the Character Vault, or editing script lines without any UI delay.
2. **Real-Time Sentence-Level Progress Tracking**:
   - XTTS splits the input script into sentences. As each sentence renders on Apple Silicon, progress ticks up smoothly (e.g. `12%` ➔ `45%` ➔ `78%` ➔ `92%` ➔ `100%`).
3. **Dynamic Apple Silicon ETA Countdown**:
   - The engine measures synthesis velocity on each sentence and continuously calculates remaining seconds:
     $$\text{ETA} = (\text{Remaining Sentences} \times \text{Avg Sentence Time}) + \text{Encoding Overhead}$$
   - Displays live in the UI: `ETA: ~8.4s`, `ETA: ~3.2s`, etc.
4. **Server-Sent Events (SSE) + Polling Fallback**:
   - Connects to `/api/jobs/<job_id>/stream` for 60fps streaming telemetry. Automatically falls back to high-frequency polling if the network drops.
5. **Auto-Arrival in Media Library**:
   - Once synthesis finishes, the new take is immediately cataloged into `outputs/<project_name>/`, the audio preview loads automatically, and a completion alert notifies the user.

---

## 📖 8. Universal Devanagari Punctuation & Special Character Sanitization

AudioAI includes automated linguistic normalization for all standard Hindi punctuation marks and Devanagari special characters to prevent tokenizer hallucinations, clicks, and awkward audio artifacts:

| Category | Input Symbols | Automated Transformation & Acoustical Handling |
| :--- | :--- | :--- |
| **Sentence Boundaries** | `।` (Purna Viram), `॥` (Double Purna Viram) | `॥` is normalized to `। ` with 280ms natural diaphragm breathing space. |
| **Clause Pauses** | `,` (Alpa Viram), `;` (Ardha Viram), `:` (Dialogue Colon) | `;` and `:` normalized to `, ` to eliminate glottal stops and awkward pauses. |
| **Dramatic Silence** | `…` (Ellipsis), `...` | Normalized to sentence pause (`। `) to create dramatic suspense without audio clicks. |
| **Dashes & Connectors** | `-` (Yojak), `—` (Em-dash), `–` (En-dash) | Reduplicated words (`धीरे-धीरे` ➔ `धीरे धीरे`) unified to space; dashes converted to clause pause `, `. |
| **Acting Directions** | `(हंसते हुए)`, `(रोते हुए)`, `(धीमे स्वर में)`, `[pause]` | Detected via regex and converted into natural breath pauses (silence), preventing the model from speaking the instruction! |
| **Brackets & Quotes** | `()`, `[]`, `""`, `‘’`, `“”` | Stripped cleanly to prevent BPE token fragmentation. |
| **Sacred Symbol** | `ॐ` (Om / Aum) | Transliterated to `ओम` to leverage native high-frequency Devanagari subwords for smooth, resonant chanting. |
| **Vowel Prolongation** | `ऽ` (Avagraha) | Stripped (e.g. `अरेऽऽऽ` ➔ `अरे`, `शिवोऽहम्` ➔ `शिवोहम`) to prevent `[UNK]` token crashes. |
| **Abbreviations** | `॰` (Sankshep Chihn), `.` | Expanded: `डॉ॰` ➔ `डॉक्टर `, `पं॰` ➔ `पंडित `, `प्रो॰` ➔ `प्रोफेसर `, `क्र॰` ➔ `क्रमांक `. |
| **Word-Final Halant** | `्` on word ends (`अर्थात्`, `भगवान्`, `विद्वान्`) | Normalized to open consonant (`अर्थात`, `भगवान`, `विद्वान`) while preserving mid-word conjuncts (`क्या`, `वाक्य`). |
| **Vedic Accents** | `॒` (Anudatta U+0952), `॑` (Udatta U+0951) | Stripped completely to prevent audio pops and token breaks. |
| **Nuktas & Visarga** | `़` (Nukta), `ः` (Visarga) | Nuktas mapped to native subwords (`क़` ➔ `क`, `ज़ि` ➔ `जि`); `दुःख` ➔ `दुख`. |
| **Chandrabindu** | `ँ` | Converted to `ं` (Anusvara) to leverage fused subwords (`हंसना`, `आंख`, `चांद`, `गांव`). |
| **Devanagari Digits** | `० १ २ ३ ४ ५ ६ ७ ८ ९` | Converted to standard digits ➔ spoken Hindi words via `hindi_num2words`. |



