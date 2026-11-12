import React, { useState, useRef, useEffect } from 'react'
import {
  Mic,
  Square,
  Upload,
  Play,
  Pause,
  Save,
  X,
  Sparkles,
  CheckCircle2,
  Volume2,
  HelpCircle,
  Sliders,
  ChevronDown,
  Layers
} from 'lucide-react'

const DEFAULT_CORE_EMOTIONS = [
  {
    id: 'neutral',
    title: 'Base Voice / Storyteller',
    badge: '🎙️ Base Voice / Storyteller (Default & Recommended)',
    desc: 'Natural conversational voice for standard dialogue & narration (Only 1 take needed!)',
    tip: '🎯 Vocal Coach Tip: Speak naturally with relaxed shoulders in your normal conversational pitch and pace.',
    hindi: 'पुराने जमाने की बात है, जब घने जंगलों के बीच एक शांत नदी बहती थी। वहां के लोग कहते थे कि उस नदी में एक अनोखा जादू है।',
    english: 'Deep within the ancient mountains, where the mist never seemed to clear, an old traveler began his long journey toward the silent valley.'
  },
  {
    id: 'happy',
    title: 'Happy / Upbeat',
    badge: '😊 Happy / Upbeat (प्रसन्न / खुश)',
    desc: 'Positive, joyful, energetic, and humorous delivery',
    tip: '🎯 Vocal Coach Tip: Smile with your cheekbones lifted to brighten acoustic vocal tract resonance.',
    hindi: 'अरे वाह! मुझे तो यकीन ही नहीं हो रहा कि हमने ये कर दिखाया! आज तो पूरे गाँव में जश्न मनाने का दिन है!',
    english: 'Yes! We actually did it! Grab your bags right now, the grand adventure is finally beginning!'
  },
  {
    id: 'sad',
    title: 'Sad / Emotional',
    badge: '😢 Sad / Emotional (उदास / गमगीन)',
    desc: 'Sorrow, grief, heartbreak, and tender emotional moments',
    tip: '🎯 Vocal Coach Tip: Drop vocal energy, soften volume, and speak with slow, solemn exhalations.',
    hindi: 'सब कुछ इतनी जल्दी खत्म हो जाएगा, मैंने कभी सपने में भी नहीं सोचा था... अब इन वीरान रास्तों पर मेरा कोई नहीं रहा।',
    english: 'Everything slipped away so quickly... I never imagined standing here alone in the cold silence.'
  },
  {
    id: 'angry',
    title: 'Angry / Intense',
    badge: '😡 Angry / Intense (क्रोधित / आक्रामक)',
    desc: 'Commanding, sharp, frustrated, and forceful delivery',
    tip: '🎯 Vocal Coach Tip: Deliver with sharp consonants, forward projection, and assertive chest voice.',
    hindi: 'बस, बहुत हो चुका! तुम्हारी इतनी हिम्मत कैसे हुई मेरे पीठ पीछे यह सब करने की? निकल जाओ मेरी नज़रों के सामने से!',
    english: 'Enough! How dare you stand there and look me in the eye after what you did! Don\'t you dare say another word!'
  },
  {
    id: 'whisper',
    title: 'Whispering / Suspense',
    badge: '🤫 Whispering / Suspense (फुसफुसाहट / खौफ)',
    desc: 'Soft, low-volume, secretive, and tense delivery',
    tip: '🎯 Vocal Coach Tip: Drop volume to an intimate stage whisper with rapid, suspenseful breath cadence.',
    hindi: '(धीमी कांपती आवाज़ में) श्शश... बिल्कुल चुप रहो... कोई है जो अँधेरे में हमारे बिल्कुल पीछे खड़ा है...',
    english: '(Tense whisper) Shh... be completely quiet! Someone is turning the doorknob right now...'
  },
  {
    id: 'dramatic',
    title: 'Dramatic / Theatrical',
    badge: '🎭 Dramatic / Theatrical (नाटकीय / सस्पेंस)',
    desc: 'Building tension, cliffhangers, urgency, and authoritative storytelling',
    tip: '🎯 Vocal Coach Tip: Use dramatic pauses, deliberate cadence, and rich dynamic contrast.',
    hindi: 'और फिर, अचानक एक गगनभेदी धमाका हुआ! चारों तरफ सन्नाटा छा गया, और वो रहस्यमयी आकृति सामने आई...',
    english: 'And then, in a heartbeat that felt like an eternity, the shadows parted and the truth stood revealed.'
  }
]

export default function RecordEmotionModal({
  isOpen,
  onClose,
  initialCharacter = '',
  initialEmotion = 'neutral',
  characters = [],
  emotionsGuide = {},
  coreEmotions = [],
  onSaveSuccess,
}) {
  const [characterName, setCharacterName] = useState(initialCharacter)
  const [isNewChar, setIsNewChar] = useState(!initialCharacter)
  const [characterAgeGroup, setCharacterAgeGroup] = useState('adult')
  const [characterAgeNumber, setCharacterAgeNumber] = useState('30')
  const [characterGender, setCharacterGender] = useState('male')
  const [selectedEmotion, setSelectedEmotion] = useState(initialEmotion)
  const [showAllEmotions, setShowAllEmotions] = useState(false)

  const activeCoreList = (coreEmotions && coreEmotions.length > 0) ? coreEmotions : DEFAULT_CORE_EMOTIONS

  // Group emotions by category for structured dropdown (advanced mode)
  const groupedEmotions = React.useMemo(() => {
    const groups = {}
    Object.entries(emotionsGuide).forEach(([key, data]) => {
      if (key === 'neutral' || key === 'whisper') return
      const catName = data.category_name || '15. Storytelling & Delivery'
      if (!groups[catName]) groups[catName] = []
      groups[catName].push({ key, ...data })
    })
    return groups
  }, [emotionsGuide])
  const [activeScriptTab, setActiveScriptTab] = useState('hi')

  // Recording State
  const [isRecording, setIsRecording] = useState(false)
  const [recordingSeconds, setRecordingSeconds] = useState(0)
  const [audioBlob, setAudioBlob] = useState(null)
  const [audioUrl, setAudioUrl] = useState(null)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [isSaving, setIsSaving] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')

  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const timerRef = useRef(null)

  useEffect(() => {
    if (initialCharacter) {
      setCharacterName(initialCharacter)
      setIsNewChar(false)
      const existing = characters.find(
        (c) => c.name.toLowerCase() === initialCharacter.toLowerCase()
      )
      if (existing) {
        if (existing.age_group) setCharacterAgeGroup(existing.age_group)
        if (existing.age) setCharacterAgeNumber(String(existing.age))
        if (existing.gender) setCharacterGender(existing.gender)
      }
    }
    if (initialEmotion) {
      setSelectedEmotion(initialEmotion)
    }
  }, [initialCharacter, initialEmotion, characters])

  const handleSelectExistingChar = (name) => {
    setCharacterName(name)
    const existing = characters.find((c) => c.name.toLowerCase() === name.toLowerCase())
    if (existing) {
      if (existing.age_group) setCharacterAgeGroup(existing.age_group)
      if (existing.age) setCharacterAgeNumber(String(existing.age))
      if (existing.gender) setCharacterGender(existing.gender)
    }
  }

  const handleAgeGroupChange = (group) => {
    setCharacterAgeGroup(group)
    if (group === 'child') setCharacterAgeNumber('8')
    else if (group === 'young') setCharacterAgeNumber('20')
    else if (group === 'adult') setCharacterAgeNumber('32')
    else if (group === 'elder') setCharacterAgeNumber('65')
  }

  const handleAgeNumberChange = (val) => {
    setCharacterAgeNumber(val)
    const num = parseInt(val, 10)
    if (!isNaN(num)) {
      if (num <= 12) setCharacterAgeGroup('child')
      else if (num <= 24) setCharacterAgeGroup('young')
      else if (num <= 55) setCharacterAgeGroup('adult')
      else setCharacterAgeGroup('elder')
    }
  }

  const activeCore = activeCoreList
  const foundInCore = activeCore.find((c) => c.id === selectedEmotion)
  const foundInGuide = emotionsGuide[selectedEmotion]

  const emotionData = foundInCore || foundInGuide || {
    title: 'Base Voice / Storyteller',
    tip: '🎯 Vocal Coach Tip: Speak naturally with relaxed shoulders in your normal conversational pitch and pace.',
    hindi: 'पुराने जमाने की बात है, जब घने जंगलों के बीच एक शांत नदी बहती थी। वहां के लोग कहते थे कि उस नदी में एक अनोखा जादू है।',
    english: 'Deep within the ancient mountains, where the mist never seemed to clear, an old traveler began his long journey toward the silent valley.',
  }

  // Start Mic Recording
  const startRecording = async () => {
    setErrorMsg('')
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream)
      audioChunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data)
        }
      }

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        setAudioBlob(blob)
        setAudioUrl(URL.createObjectURL(blob))
        stream.getTracks().forEach((track) => track.stop())
      }

      mediaRecorderRef.current.start()
      setIsRecording(true)
      setRecordingSeconds(0)

      timerRef.current = setInterval(() => {
        setRecordingSeconds((prev) => prev + 1)
      }, 1000)
    } catch (err) {
      setErrorMsg('Microphone access denied or unavailable: ' + err.message)
    }
  }

  // Stop Mic Recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      clearInterval(timerRef.current)
    }
  }

  // Handle File Upload
  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      setUploadedFile(file)
      setAudioBlob(file)
      setAudioUrl(URL.createObjectURL(file))
    }
  }

  // Save to backend
  const handleSave = async () => {
    if (!characterName.trim()) {
      setErrorMsg('Please select or enter a character name.')
      return
    }
    if (!audioBlob) {
      setErrorMsg('Please record audio or upload a sample first.')
      return
    }

    setIsSaving(true)
    setErrorMsg('')

    try {
      const formData = new FormData()
      formData.append('character_name', characterName.trim())
      formData.append('emotion_key', selectedEmotion)
      formData.append('age', characterAgeNumber || characterAgeGroup)
      formData.append('gender', characterGender)
      formData.append('audio_file', audioBlob, 'sample.wav')

      const res = await fetch('/api/characters/record-emotion', {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Failed to save voice sample.')
      }

      onSaveSuccess()
      onClose()
    } catch (err) {
      setErrorMsg(err.message)
    } finally {
      setIsSaving(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-2xl bg-[#0d1322] border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center">
              <Mic className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Custom Character Voice Creation</h3>
              <p className="text-[11px] text-slate-400">Clone authentic multi-emotion character voices with automatic tone adaptation</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5 overflow-y-auto flex-1">
          {errorMsg && (
            <div className="p-3 text-xs bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-xl">
              {errorMsg}
            </div>
          )}

          {/* Character Name & Emotion Selector */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* 1. Character Name */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">1. Character Name</label>
              {isNewChar ? (
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={characterName}
                    onChange={(e) => setCharacterName(e.target.value)}
                    placeholder="e.g. Mohan, Chintu, Priya, Dadi Ji"
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white outline-none focus:border-sky-500"
                  />
                  {characters.length > 0 && (
                    <button
                      type="button"
                      onClick={() => setIsNewChar(false)}
                      className="px-2 text-[10px] text-slate-400 hover:text-white"
                    >
                      Pick
                    </button>
                  )}
                </div>
              ) : (
                <div className="flex space-x-2">
                  <select
                    value={characterName}
                    onChange={(e) => handleSelectExistingChar(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white outline-none"
                  >
                    {characters.map((c) => (
                      <option key={c.name} value={c.name}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    onClick={() => {
                      setIsNewChar(true)
                      setCharacterName('')
                    }}
                    className="px-2 text-[10px] text-sky-400 hover:text-sky-300 font-semibold"
                  >
                    + New
                  </button>
                </div>
              )}
            </div>

            {/* 2. Choose Emotion */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-slate-300">2. Emotion to Record</label>
                <button
                  type="button"
                  onClick={() => setShowAllEmotions((prev) => !prev)}
                  className="text-[10px] text-sky-400 hover:text-sky-300 font-medium transition-colors"
                >
                  {showAllEmotions ? '← Show 6 Core Foundations' : '+ Show all 121 styles (Advanced)'}
                </button>
              </div>

              {!showAllEmotions ? (
                <select
                  value={selectedEmotion}
                  onChange={(e) => setSelectedEmotion(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white outline-none focus:border-sky-500 font-medium"
                >
                  {activeCoreList.map((emo) => (
                    <option key={emo.id} value={emo.id} className="bg-slate-900 text-white py-1">
                      {emo.badge || emo.title}
                    </option>
                  ))}
                </select>
              ) : (
                <select
                  value={selectedEmotion}
                  onChange={(e) => setSelectedEmotion(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white outline-none focus:border-sky-500 font-medium"
                >
                  <optgroup label="⭐ Core Foundation Anchors (Recommended)" className="bg-slate-950 font-bold text-sky-400">
                    {activeCoreList.map((emo) => (
                      <option key={emo.id} value={emo.id} className="bg-slate-900 text-white font-normal">
                        {emo.badge || emo.title}
                      </option>
                    ))}
                  </optgroup>
                  {Object.entries(groupedEmotions).map(([catName, list]) => (
                    <optgroup key={catName} label={catName} className="bg-slate-950 font-bold text-indigo-400">
                      {list.map((emo) => (
                        <option key={emo.key} value={emo.key} className="bg-slate-900 text-white font-normal">
                          {emo.title} — {emo.meaning}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </select>
              )}
            </div>
          </div>

          {/* Smart Foundation Banner */}
          <div className="p-3.5 rounded-xl bg-gradient-to-r from-sky-500/10 via-indigo-500/10 to-transparent border border-sky-500/20 flex items-start gap-2.5">
            <Sparkles className="w-4 h-4 text-sky-400 mt-0.5 flex-shrink-0" />
            <div className="text-xs space-y-0.5">
              <span className="font-semibold text-white">💡 Pro-Tip: Only 1 Base Voice is needed to start!</span>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Record your natural <strong className="text-sky-300">Base Voice / Storyteller</strong> sample once. All 121 delivery styles (Heartbroken, Furious, Panicked, Meditative, etc.) in the Voiceover Studio are immediately unlocked and will automatically adapt from your base voice or closest anchor take using our AI acoustic tone engine.
              </p>
            </div>
          </div>

          {/* Age & Gender Persona Settings */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-sky-400" /> Character Persona: Age & Gender
              </span>
              <span className="text-[10px] text-emerald-400 font-mono">Auto Tone Shaper Active</span>
            </div>

            {/* Age Selection */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-medium text-slate-400">Character Age:</label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {[
                  { id: 'child', label: 'Child (5–12)', emoji: '👦' },
                  { id: 'young', label: 'Young (13–24)', emoji: '🧑' },
                  { id: 'adult', label: 'Adult (25–55)', emoji: '👨' },
                  { id: 'elder', label: 'Elder (56+)', emoji: '👴' },
                ].map((ag) => (
                  <button
                    key={ag.id}
                    type="button"
                    onClick={() => handleAgeGroupChange(ag.id)}
                    className={`px-2.5 py-1.5 rounded-lg text-xs font-medium border flex items-center justify-center gap-1 transition-all ${
                      characterAgeGroup === ag.id
                        ? 'bg-sky-500/20 text-sky-300 border-sky-500/40 shadow-sm'
                        : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
                    }`}
                  >
                    <span>{ag.emoji}</span>
                    <span>{ag.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Gender Selection & Exact Age */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              <div className="space-y-1">
                <label className="text-[11px] font-medium text-slate-400">Character Gender:</label>
                <div className="grid grid-cols-3 gap-1.5">
                  {[
                    { id: 'male', label: 'Male' },
                    { id: 'female', label: 'Female' },
                    { id: 'neutral', label: 'Neutral' },
                  ].map((g) => (
                    <button
                      key={g.id}
                      type="button"
                      onClick={() => setCharacterGender(g.id)}
                      className={`px-2 py-1.5 rounded-lg text-xs font-medium border text-center transition-all ${
                        characterGender === g.id
                          ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40'
                          : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
                      }`}
                    >
                      {g.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[11px] font-medium text-slate-400">Approximate Age (Years):</label>
                <input
                  type="number"
                  min="3"
                  max="100"
                  value={characterAgeNumber}
                  onChange={(e) => handleAgeNumberChange(e.target.value)}
                  className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 outline-none focus:border-sky-500"
                  placeholder="e.g. 8, 22, 35, 70"
                />
              </div>
            </div>

            <p className="text-[11px] text-slate-400 leading-normal pt-1 border-t border-slate-800/80">
              💡 Even if you record using your own voice, the engine will automatically shift pitch, vocal resonance, and formants to authentically sound like a {characterAgeGroup === 'child' ? 'childlike' : characterAgeGroup === 'elder' ? 'mature older' : characterAgeGroup} {characterGender} character!
            </p>
          </div>

          {/* Vocal Coach Advice Box */}
          <div className="p-4 rounded-xl bg-sky-950/20 border border-sky-500/20 space-y-1.5">
            <span className="text-[11px] font-semibold text-sky-400 uppercase tracking-wider flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5" /> Vocal Direction for {emotionData.title}
            </span>
            <p className="text-xs text-slate-300 leading-relaxed">{emotionData.tip}</p>
          </div>

          {/* Acting Script Prompts */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300">
                Acting Script Prompt (10–15 Seconds)
              </span>
              <div className="inline-flex p-0.5 rounded-lg bg-slate-800 border border-slate-700">
                <button
                  type="button"
                  onClick={() => setActiveScriptTab('hi')}
                  className={`px-2.5 py-0.5 text-xs rounded-md font-medium transition-all ${
                    activeScriptTab === 'hi'
                      ? 'bg-sky-500 text-white font-semibold'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  🇮🇳 Hindi
                </button>
                <button
                  type="button"
                  onClick={() => setActiveScriptTab('en')}
                  className={`px-2.5 py-0.5 text-xs rounded-md font-medium transition-all ${
                    activeScriptTab === 'en'
                      ? 'bg-sky-500 text-white font-semibold'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  🇬🇧 English
                </button>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-xs leading-relaxed select-text font-sans">
              {activeScriptTab === 'hi' ? emotionData.hindi : emotionData.english}
            </div>
          </div>

          {/* Audio Capture: Mic or File Upload */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
            <span className="text-xs font-semibold text-slate-300">
              3. Record or Upload 10–15s Audio Sample
            </span>

            <div className="flex flex-col sm:flex-row items-center gap-3">
              {/* Record Button */}
              {!isRecording ? (
                <button
                  type="button"
                  onClick={startRecording}
                  className="w-full sm:w-auto px-4 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold flex items-center justify-center space-x-2 transition-all shadow-md shadow-rose-600/20"
                >
                  <Mic className="w-4 h-4" />
                  <span>Start Microphone Recording</span>
                </button>
              ) : (
                <button
                  type="button"
                  onClick={stopRecording}
                  className="w-full sm:w-auto px-4 py-2.5 rounded-xl bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold flex items-center justify-center space-x-2 animate-pulse"
                >
                  <Square className="w-4 h-4 text-rose-400 fill-current" />
                  <span>Stop Recording ({recordingSeconds}s)</span>
                </button>
              )}

              <span className="text-xs text-slate-500">or upload audio</span>

              {/* Upload Input */}
              <label className="w-full sm:w-auto px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-medium text-slate-300 cursor-pointer flex items-center justify-center space-x-2 transition-colors">
                <Upload className="w-3.5 h-3.5" />
                <span>Choose Audio File</span>
                <input
                  type="file"
                  accept="audio/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>
            </div>

            {/* Audio Preview if available */}
            {audioUrl && (
              <div className="pt-2 flex items-center space-x-3">
                <audio src={audioUrl} controls className="w-full h-8" />
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/60 flex items-center justify-end space-x-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white"
          >
            Cancel
          </button>
          <button
            type="button"
            disabled={isSaving || !audioBlob || !characterName.trim()}
            onClick={handleSave}
            className="px-5 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 text-white text-xs font-semibold shadow-md shadow-sky-500/20 transition-all flex items-center space-x-2 disabled:opacity-50"
          >
            {isSaving ? (
              <span>Normalizing Audio & Saving...</span>
            ) : (
              <>
                <Save className="w-4 h-4" />
                <span>Save to Character Profile</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

