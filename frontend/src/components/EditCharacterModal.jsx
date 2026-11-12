import React, { useState, useEffect, useRef } from 'react'
import {
  X,
  User,
  GitBranch,
  Upload,
  Mic,
  Square,
  Play,
  Pause,
  Trash2,
  Save,
  AlertTriangle,
  CheckCircle2,
  Sparkles
} from 'lucide-react'

export default function EditCharacterModal({
  isOpen,
  onClose,
  character,
  emotionsGuide,
  onSaveSuccess,
  onDeleteSuccess,
  showToast,
}) {
  if (!isOpen || !character) return null

  const [name, setName] = useState(character.name || '')
  const [age, setAge] = useState(character.age || 30)
  const [gender, setGender] = useState(character.gender || 'male')
  const [description, setDescription] = useState(character.description || '')
  const [pushToGit, setPushToGit] = useState(true)

  // Audio update states
  const [audioMode, setAudioMode] = useState('keep') // 'keep', 'record', 'upload'
  const [selectedEmotion, setSelectedEmotion] = useState('neutral')
  const [uploadedFile, setUploadedFile] = useState(null)
  const [isRecording, setIsRecording] = useState(false)
  const [recordedBlob, setRecordedBlob] = useState(null)
  const [audioUrl, setAudioUrl] = useState(null)
  const [recordDuration, setRecordDuration] = useState(0)

  // Saving states
  const [isSaving, setIsSaving] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const timerRef = useRef(null)

  useEffect(() => {
    if (character) {
      setName(character.name || '')
      setAge(character.age || 30)
      setGender(character.gender || 'male')
      setDescription(character.description || '')
      setAudioMode('keep')
      setUploadedFile(null)
      setRecordedBlob(null)
      setAudioUrl(null)
      setShowDeleteConfirm(false)
    }
  }, [character])

  // Mic Recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      audioChunksRef.current = []
      const recorder = new MediaRecorder(stream)
      mediaRecorderRef.current = recorder

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data)
      }

      recorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        setRecordedBlob(blob)
        setAudioUrl(URL.createObjectURL(blob))
        stream.getTracks().forEach((track) => track.stop())
      }

      recorder.start()
      setIsRecording(true)
      setRecordDuration(0)
      timerRef.current = setInterval(() => {
        setRecordDuration((prev) => prev + 1)
      }, 1000)
    } catch (err) {
      showToast?.('Microphone access denied: ' + err.message, 'error')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      clearInterval(timerRef.current)
    }
  }

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      setUploadedFile(file)
      setAudioUrl(URL.createObjectURL(file))
    }
  }

  const handleAgeBracket = (targetAge) => {
    setAge(targetAge)
  }

  const handleSave = async () => {
    if (!name.trim()) {
      showToast?.('Please enter a character name.', 'error')
      return
    }

    setIsSaving(true)
    try {
      const formData = new FormData()
      formData.append('char_name', character.name)
      formData.append('new_name', name.trim())
      formData.append('age', String(age))
      formData.append('gender', gender)
      formData.append('description', description.trim())
      formData.append('push_to_git', pushToGit ? 'true' : 'false')

      if (audioMode === 'upload' && uploadedFile) {
        formData.append('audio_file', uploadedFile)
        formData.append('emotion', selectedEmotion)
      } else if (audioMode === 'record' && recordedBlob) {
        const audioFile = new File([recordedBlob], `${name.trim()}_${selectedEmotion}.wav`, {
          type: 'audio/wav',
        })
        formData.append('audio_file', audioFile)
        formData.append('emotion', selectedEmotion)
      }

      const res = await fetch('/api/characters/update', {
        method: 'POST',
        body: formData,
      })

      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to update character')
      }

      showToast?.(
        data.git_sync?.message || `Character '${data.character?.name || name}' saved successfully!`,
        'success'
      )
      onSaveSuccess?.()
      onClose()
    } catch (err) {
      showToast?.('Failed to update character: ' + err.message, 'error')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDelete = async () => {
    setIsDeleting(true)
    try {
      const res = await fetch(`/api/characters/${encodeURIComponent(character.name)}`, {
        method: 'DELETE',
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to delete character')
      }
      showToast?.(`Character '${character.name}' deleted.`, 'info')
      onDeleteSuccess?.()
      onClose()
    } catch (err) {
      showToast?.('Failed to delete character: ' + err.message, 'error')
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-2xl bg-[#0d1322] border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-800/80 flex items-center justify-between bg-gradient-to-r from-[#0d1322] to-[#121a30]">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white font-bold text-base shadow-md shadow-sky-500/20">
              {name ? name.charAt(0).toUpperCase() : 'C'}
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                Edit Character Profile
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 font-medium border border-sky-500/20">
                  {character.name}
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Modify voice parameters, rename character, or update reference audio takes.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-6 overflow-y-auto flex-1 text-sm">
          {/* 1. Character Name */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Character Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Vikram, Sunita, Kabir..."
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-sky-500 transition-colors"
            />
            {name.trim() !== character.name && (
              <p className="text-[11px] text-amber-400 flex items-center gap-1 mt-1">
                <AlertTriangle className="w-3.5 h-3.5" />
                Renaming will automatically update all existing audio take files to match the new name.
              </p>
            )}
          </div>

          {/* 2. Age & Age Groups */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Character Age (Years)
              </label>
              <span className="text-xs font-mono text-sky-400 font-semibold">{age} years</span>
            </div>

            {/* Quick Bracket Buttons */}
            <div className="grid grid-cols-4 gap-2">
              {[
                { label: '👦 Child (5-12)', ageVal: 8 },
                { label: '🧑 Young (13-24)', ageVal: 20 },
                { label: '👨 Adult (25-55)', ageVal: 32 },
                { label: '👴 Elder (56+)', ageVal: 65 },
              ].map((bracket) => (
                <button
                  key={bracket.label}
                  type="button"
                  onClick={() => handleAgeBracket(bracket.ageVal)}
                  className={`px-2.5 py-2 rounded-xl text-xs font-medium border text-center transition-all ${
                    (bracket.ageVal === 8 && age <= 12) ||
                    (bracket.ageVal === 20 && age >= 13 && age <= 24) ||
                    (bracket.ageVal === 32 && age >= 25 && age <= 55) ||
                    (bracket.ageVal === 65 && age >= 56)
                      ? 'bg-sky-500/20 border-sky-500/50 text-sky-300 font-semibold shadow-sm'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                  }`}
                >
                  {bracket.label}
                </button>
              ))}
            </div>

            <input
              type="range"
              min="5"
              max="90"
              value={age}
              onChange={(e) => setAge(parseInt(e.target.value, 10))}
              className="w-full accent-sky-500 bg-slate-800 h-1.5 rounded-lg cursor-pointer"
            />
          </div>

          {/* 3. Gender */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Gender
            </label>
            <div className="grid grid-cols-3 gap-2">
              {['male', 'female', 'neutral'].map((g) => (
                <button
                  key={g}
                  type="button"
                  onClick={() => setGender(g)}
                  className={`py-2 rounded-xl text-xs font-semibold border capitalize transition-all ${
                    gender === g
                      ? 'bg-sky-500/20 border-sky-500/50 text-sky-300 shadow-sm'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                  }`}
                >
                  {g === 'male' ? '👨 Male' : g === 'female' ? '👩 Female' : '✨ Neutral'}
                </button>
              ))}
            </div>
          </div>

          {/* 4. Description / Role */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Persona Role / Description (Optional)
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g. Village elder, inquisitive school child, dramatic hero..."
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-sky-500 transition-colors"
            />
          </div>

          {/* 5. Reference Audio Update (Optional) */}
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Reference Audio Sample
              </span>
              <span className="text-[11px] text-slate-400">
                {audioMode === 'keep' ? 'Preserving existing recordings' : 'Updating sample'}
              </span>
            </div>

            {/* Mode selection tabs */}
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setAudioMode('keep')}
                className={`py-1.5 rounded-lg text-xs font-medium border transition-all ${
                  audioMode === 'keep'
                    ? 'bg-sky-500/20 border-sky-500/40 text-sky-300'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-300'
                }`}
              >
                Keep Current
              </button>
              <button
                type="button"
                onClick={() => setAudioMode('upload')}
                className={`py-1.5 rounded-lg text-xs font-medium border transition-all flex items-center justify-center gap-1 ${
                  audioMode === 'upload'
                    ? 'bg-sky-500/20 border-sky-500/40 text-sky-300'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-300'
                }`}
              >
                <Upload className="w-3.5 h-3.5" /> Upload File
              </button>
              <button
                type="button"
                onClick={() => setAudioMode('record')}
                className={`py-1.5 rounded-lg text-xs font-medium border transition-all flex items-center justify-center gap-1 ${
                  audioMode === 'record'
                    ? 'bg-sky-500/20 border-sky-500/40 text-sky-300'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-300'
                }`}
              >
                <Mic className="w-3.5 h-3.5" /> Record Mic
              </button>
            </div>

            {audioMode !== 'keep' && (
              <div className="space-y-3 pt-2">
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-slate-400">Assign to Emotion:</span>
                  <select
                    value={selectedEmotion}
                    onChange={(e) => setSelectedEmotion(e.target.value)}
                    className="px-2 py-1 rounded bg-slate-800 border border-slate-700 text-xs text-slate-200 capitalize"
                  >
                    {Object.keys(emotionsGuide || { neutral: {} }).map((k) => (
                      <option key={k} value={k}>
                        {k.charAt(0).toUpperCase() + k.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                {audioMode === 'upload' && (
                  <label className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-slate-700 hover:border-sky-500 rounded-xl cursor-pointer bg-slate-900/50 transition-colors">
                    <Upload className="w-6 h-6 text-slate-400 mb-1" />
                    <span className="text-xs text-slate-300 font-medium">
                      {uploadedFile ? uploadedFile.name : 'Click to select audio file (WAV / MP3)'}
                    </span>
                    <span className="text-[10px] text-slate-500 mt-0.5">Recommended 10–20 sec speech</span>
                    <input
                      type="file"
                      accept="audio/*"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                  </label>
                )}

                {audioMode === 'record' && (
                  <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 text-center space-y-3">
                    <p className="text-xs text-slate-400 font-mono">
                      {isRecording ? `Recording: ${recordDuration}s` : 'Speak naturally for 10-15 seconds'}
                    </p>
                    <div className="flex justify-center">
                      {!isRecording ? (
                        <button
                          type="button"
                          onClick={startRecording}
                          className="px-4 py-2 rounded-xl bg-rose-500 hover:bg-rose-600 text-white text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-rose-500/20"
                        >
                          <Mic className="w-4 h-4" /> Start Recording
                        </button>
                      ) : (
                        <button
                          type="button"
                          onClick={stopRecording}
                          className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white text-xs font-semibold flex items-center gap-1.5 animate-pulse"
                        >
                          <Square className="w-4 h-4 text-rose-400 fill-current" /> Stop Recording
                        </button>
                      )}
                    </div>
                  </div>
                )}

                {audioUrl && (
                  <div className="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700/80 flex items-center justify-between">
                    <span className="text-xs text-emerald-400 flex items-center gap-1.5 font-medium">
                      <CheckCircle2 className="w-4 h-4" /> New audio sample ready
                    </span>
                    <audio src={audioUrl} controls className="h-7 w-48" />
                  </div>
                )}
              </div>
            )}
          </div>

          {/* 6. Push to GitHub Option */}
          <div className="p-3.5 rounded-xl bg-[#090e1a] border border-sky-500/20 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <GitBranch className="w-4 h-4 text-sky-400" />
              <div>
                <p className="text-xs font-semibold text-slate-200">Commit & Push to GitHub</p>
                <p className="text-[11px] text-slate-400">
                  Safely commits character profile and audio models to your GitHub repository.
                </p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={pushToGit}
                onChange={(e) => setPushToGit(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-9 h-5 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-sky-500"></div>
            </label>
          </div>

          {/* 7. Danger Zone: Delete Character */}
          <div className="pt-2 border-t border-slate-800/80">
            {!showDeleteConfirm ? (
              <button
                type="button"
                onClick={() => setShowDeleteConfirm(true)}
                className="text-xs text-rose-400 hover:text-rose-300 font-medium flex items-center gap-1.5 transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" /> Delete Character
              </button>
            ) : (
              <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/30 flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-rose-300">Are you sure?</p>
                  <p className="text-[11px] text-slate-400">
                    This will permanently delete {character.name} and all recorded takes.
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    type="button"
                    onClick={() => setShowDeleteConfirm(false)}
                    className="px-2.5 py-1 rounded-lg text-xs bg-slate-800 text-slate-300 hover:bg-slate-700"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleDelete}
                    disabled={isDeleting}
                    className="px-2.5 py-1 rounded-lg text-xs bg-rose-600 hover:bg-rose-500 text-white font-semibold disabled:opacity-50"
                  >
                    {isDeleting ? 'Deleting...' : 'Yes, Delete'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800/80 flex items-center justify-end space-x-3 bg-slate-900/60">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            disabled={isSaving}
            className="px-5 py-2 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-sky-500/20 transition-all flex items-center gap-1.5 disabled:opacity-50"
          >
            <Save className="w-3.5 h-3.5" />
            <span>{isSaving ? 'Saving Changes...' : 'Save Character Profile'}</span>
          </button>
        </div>
      </div>
    </div>
  )
}
