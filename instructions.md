# 🎙️ Local Multi-Character Voice Studio (macOS Apple Silicon)

A local, 100% free, private, and unlimited Text-to-Speech (TTS) and Voice Cloning web studio powered by **Coqui XTTS-v2**, **Gradio**, and **FFmpeg** (`libmp3lame`).

Engineered specifically for **macOS Apple Silicon (M1 / M2 / M3 / M4)** to generate high-quality **Hindi (`hi`)** and **English (`en`)** storytelling tracks with **10 distinct character emotions** and direct **192kbps MP3 export** ready for **Filmora**, **Premiere Pro**, and **DaVinci Resolve**.

---

## 📁 1. Project Directory Layout

```text
audioAI/
├── app.py                 # Gradio web UI & XTTS-v2 multi-emotion synthesis engine
├── requirements.txt       # Dependencies (PyTorch, Coqui XTTS-v2, Gradio, FFmpeg)
├── .venv/                 # Dedicated Apple Silicon Python 3.11 virtual environment
├── voices/                # Stored character voice reference files by emotion
│   ├── README.md          # Guide for reference voice files
│   ├── gaurav_neutral.wav # (Example) Base storytelling voice
│   ├── gaurav_sad.wav     # (Example) Sad/heartbroken voice
│   ├── gaurav_crying.wav  # (Example) Choked/crying voice
│   └── gaurav_angry.wav   # (Example) Angry confrontation voice
├── outputs/               # Auto-saved 192kbps MP3 audio files for Filmora
└── instructions.md        # Comprehensive studio guide & vocal scripts
```

---

## ⚡ 2. Quick Start

### Step 1: Activate Virtual Environment
Open your terminal in `/Users/gauravsharma/Documents/audioAI` and run:

```bash
cd /Users/gauravsharma/Documents/audioAI
source .venv/bin/activate
```

### Step 2: Launch the Studio
```bash
python app.py
```

Open your browser at:
👉 **http://127.0.0.1:7860**

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
