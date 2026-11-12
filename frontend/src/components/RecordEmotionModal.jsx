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
  HelpCircle
} from 'lucide-react'

export default function RecordEmotionModal({
  isOpen,
  onClose,
  initialCharacter = '',
  initialEmotion = 'neutral',
  characters = [],
  emotionsGuide = {},
  onSaveSuccess,
}) {
  const [characterName, setCharacterName] = useState(initialCharacter)
  const [isNewChar, setIsNewChar] = useState(!initialCharacter)
  const [selectedEmotion, setSelectedEmotion] = useState(initialEmotion)
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
    }
    if (initialEmotion) {
      setSelectedEmotion(initialEmotion)
    }
  }, [initialCharacter, initialEmotion])

  const emotionData = emotionsGuide[selectedEmotion] || {
    title: 'Neutral / Storyteller',
    tip: 'Sit tall with relaxed shoulders. Keep your pitch in a comfortable mid-range.',
    hindi: 'पुराने जमाने की बात है, जब घने जंगलों के बीच एक शांत नदी बहती थी...',
    english: 'Deep within the ancient mountains, where the mist never seemed to clear...',
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
        // stop tracks
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
              <h3 className="text-sm font-bold text-white">Character Emotion Voice Studio</h3>
              <p className="text-[11px] text-slate-400">Clone authentic emotional delivery for Filmora</p>
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

          {/* Character & Emotion Selectors */}
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
                    placeholder="e.g. Gaurav, Mohan, Priya"
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
                    onChange={(e) => setCharacterName(e.target.value)}
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
              <label className="text-xs font-semibold text-slate-300">2. Emotion to Record</label>
              <select
                value={selectedEmotion}
                onChange={(e) => setSelectedEmotion(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white outline-none capitalize"
              >
                {Object.keys(emotionsGuide).map((key) => (
                  <option key={key} value={key}>
                    {emotionsGuide[key]?.badge || key}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Vocal Coach Advice Box */}
          <div className="p-4 rounded-xl bg-sky-950/20 border border-sky-500/20 space-y-1.5">
            <span className="text-[11px] font-semibold text-sky-400 uppercase tracking-wider flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5" /> Vocal Coach Direction
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

