import React, { useState, useMemo } from 'react'
import {
  Play,
  Pause,
  Download,
  Sparkles,
  Sliders,
  Volume2,
  Mic,
  Clock,
  CheckCircle,
  FileAudio,
  Film,
  Zap,
  RotateCcw,
  Pencil,
  Search,
  ChevronDown,
  ChevronUp,
  Layers
} from 'lucide-react'

export default function StudioView({
  voices,
  activeProject,
  onGenerateAudio,
  isGenerating,
  activeJob,
  lastGenerated,
  onPlayAudio,
  currentPlayingUrl,
  isPlaying,
  onOpenVoiceCloner,
  onEditVoice,
  emotionsGuide = {},
  emotionCategories = [],
}) {
  const [scriptText, setScriptText] = useState(
    'दोपहर का 1 बजा है। प्रिया की desk पर मम्मी का बनाया गरमागरम टिफिन रखा है।'
  )
  const [selectedVoice, setSelectedVoice] = useState(voices[0] || '')
  const [selectedEmotion, setSelectedEmotion] = useState('storytelling')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [emotionSearch, setEmotionSearch] = useState('')
  const [isEmotionDrawerOpen, setIsEmotionDrawerOpen] = useState(false)
  const [removeSilence, setRemoveSilence] = useState(false)
  const [language, setLanguage] = useState('hi')
  const [speed, setSpeed] = useState(1.0)
  const [clipTitle, setClipTitle] = useState('')

  const QUICK_EMOTIONS = [
    { id: 'storytelling', label: 'Storytelling', emoji: '🎙️', desc: 'Natural Narration' },
    { id: 'dramatic', label: 'Dramatic', emoji: '🎭', desc: 'Theatrical Delivery' },
    { id: 'suspenseful', label: 'Suspenseful', emoji: '⚡', desc: 'Building Tension' },
    { id: 'whispering', label: 'Whispering', emoji: '🤫', desc: 'Soft & Low Volume' },
    { id: 'happy', label: 'Happy', emoji: '😊', desc: 'Pleasant & Joyful' },
    { id: 'sad', label: 'Sad', emoji: '😢', desc: 'Sorrow & Grief' },
    { id: 'angry', label: 'Angry', emoji: '😡', desc: 'Intense & Furious' },
    { id: 'excited', label: 'Excited', emoji: '✨', desc: 'High Energy' },
    { id: 'calm', label: 'Calm', emoji: '🧘', desc: 'Peaceful & Composed' },
    { id: 'crying', label: 'Crying', emoji: '😭', desc: 'Emotional Distress' },
    { id: 'urgent', label: 'Urgent', emoji: '⏱️', desc: 'Fast & Pressing' },
    { id: 'funny', label: 'Funny', emoji: '😂', desc: 'Naturally Humorous' },
  ]

  // Active emotion metadata
  const activeEmotionInfo = emotionsGuide[selectedEmotion] || {
    title: selectedEmotion.charAt(0).toUpperCase() + selectedEmotion.slice(1).replace('_', ' '),
    meaning: 'Custom storytelling expression',
    category_name: 'Custom',
  }

  // Filtered emotions
  const allEmotionsList = useMemo(() => Object.values(emotionsGuide), [emotionsGuide])

  const filteredEmotions = useMemo(() => {
    return allEmotionsList.filter((emo) => {
      if (emo.key === 'neutral' || emo.key === 'whisper') return false
      const matchesCategory = selectedCategory === 'all' || emo.category_id === selectedCategory
      const query = emotionSearch.toLowerCase().trim()
      const matchesQuery =
        !query ||
        emo.title?.toLowerCase().includes(query) ||
        emo.meaning?.toLowerCase().includes(query) ||
        emo.category_name?.toLowerCase().includes(query)
      return matchesCategory && matchesQuery
    })
  }, [allEmotionsList, selectedCategory, emotionSearch])

  // Sync selected voice if voices array updates
  React.useEffect(() => {
    if (!selectedVoice && voices.length > 0) {
      setSelectedVoice(voices[0])
    }
  }, [voices, selectedVoice])

  const handleGenerate = (e) => {
    e.preventDefault()
    if (!scriptText.trim()) return
    onGenerateAudio({
      script_text: scriptText,
      voice_choice: selectedVoice || voices[0],
      language,
      speed,
      project_name: activeProject,
      clip_title: clipTitle,
      emotion: selectedEmotion,
      remove_silence: removeSilence,
    })
  }

  const speedPresets = [0.85, 1.0, 1.15, 1.3, 1.5, 2.0]

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Studio Banner */}
      <div className="flex items-center justify-between p-4 rounded-2xl bg-gradient-to-r from-sky-950/40 via-slate-900 to-indigo-950/30 border border-sky-500/20">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-sky-500/20 border border-sky-500/30 flex items-center justify-center text-sky-400">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              Studio Voiceover & AI Speech
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                192kbps Master MP3
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Devanagari Normalization active — conjuncts, English loanwords, and numbers expand automatically.
            </p>
          </div>
        </div>
        <div className="text-right hidden sm:block">
          <span className="text-xs text-slate-400">Target Workspace:</span>
          <p className="text-xs font-mono font-semibold text-sky-400">outputs/{activeProject}/</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* LEFT COLUMN: Input & Generation Settings */}
        <div className="lg:col-span-8 space-y-5">
          <form onSubmit={handleGenerate} className="p-6 rounded-2xl bg-[#0d1322] border border-slate-800 space-y-5 shadow-xl">
            {/* Dialogue / Script Input */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <FileAudio className="w-3.5 h-3.5 text-sky-400" /> Script / Dialogue (संवाद)
                </label>
                <div className="flex items-center space-x-2">
                  <div className="inline-flex p-0.5 rounded-lg bg-slate-800 border border-slate-700">
                    <button
                      type="button"
                      onClick={() => setLanguage('hi')}
                      className={`px-2.5 py-1 text-xs rounded-md font-medium transition-all ${
                        language === 'hi' ? 'bg-sky-500 text-white font-semibold' : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      🇮🇳 Hindi
                    </button>
                    <button
                      type="button"
                      onClick={() => setLanguage('en')}
                      className={`px-2.5 py-1 text-xs rounded-md font-medium transition-all ${
                        language === 'en' ? 'bg-sky-500 text-white font-semibold' : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      🇬🇧 English
                    </button>
                  </div>
                  <span className="text-[11px] text-slate-500">{scriptText.length} chars</span>
                </div>
              </div>

              <textarea
                value={scriptText}
                onChange={(e) => setScriptText(e.target.value)}
                placeholder="Paste Hindi or English script here... e.g. दोपहर का 1 बजा है। प्रिया की desk पर मम्मी का बनाया गरमागरम टिफिन रखा है।"
                rows={5}
                className="w-full p-4 rounded-xl bg-[#070b14] border border-slate-800 focus:border-sky-500 focus:ring-1 focus:ring-sky-500 text-slate-100 text-sm leading-relaxed resize-none outline-none placeholder:text-slate-600 transition-all font-sans"
              />
            </div>

            {/* Scene Title & Character Voice Selector */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Optional Clip Title */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">
                  Take / Scene Title <span className="text-slate-500 font-normal">(Optional)</span>
                </label>
                <input
                  type="text"
                  value={clipTitle}
                  onChange={(e) => setClipTitle(e.target.value)}
                  placeholder="e.g. Scene_1_Intro or Priya_Reaction"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#070b14] border border-slate-800 focus:border-sky-500 focus:ring-1 focus:ring-sky-500 text-slate-200 text-xs outline-none"
                />
              </div>

              {/* Voice Dropdown */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-semibold text-slate-300">Character Voice</label>
                  <div className="flex items-center space-x-2">
                    {selectedVoice?.includes('🎭 Custom:') && onEditVoice && (
                      <button
                        type="button"
                        onClick={() => onEditVoice(selectedVoice)}
                        className="text-[11px] text-sky-400 hover:text-sky-300 font-medium flex items-center gap-1 transition-colors"
                        title="Edit Character Voice Parameters"
                      >
                        <Pencil className="w-3 h-3" /> Edit Profile
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={onOpenVoiceCloner}
                      className="text-[11px] text-slate-400 hover:text-slate-200 font-medium flex items-center gap-1 transition-colors"
                    >
                      + Clone
                    </button>
                  </div>
                </div>
                <select
                  value={selectedVoice}
                  onChange={(e) => setSelectedVoice(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-[#070b14] border border-slate-800 focus:border-sky-500 focus:ring-1 focus:ring-sky-500 text-slate-200 text-xs outline-none cursor-pointer"
                >
                  {voices.map((v) => (
                    <option key={v} value={v}>
                      {v}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Emotion & Delivery Style Selector (15 Categories & 121 Emotions) */}
            <div className="space-y-3 p-4 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-sky-400" /> Vocal Emotion & Delivery Style
                </span>
                <span className="text-[11px] text-sky-400 font-medium">
                  {activeEmotionInfo.title}{' '}
                  <span className="text-slate-400 font-normal">
                    ({activeEmotionInfo.meaning || activeEmotionInfo.desc || 'Natural narration'})
                  </span>
                </span>
              </div>

              {/* Quick Storytelling Presets */}
              <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2">
                {QUICK_EMOTIONS.map((emo) => {
                  const isSel = selectedEmotion === emo.id
                  return (
                    <button
                      key={emo.id}
                      type="button"
                      onClick={() => setSelectedEmotion(emo.id)}
                      className={`flex items-center space-x-1.5 px-2.5 py-2 rounded-lg text-xs font-medium transition-all border ${
                        isSel
                          ? 'bg-sky-500/20 text-sky-300 border-sky-500/40 shadow-sm'
                          : 'bg-slate-900/70 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800/50'
                      }`}
                    >
                      <span className="text-sm">{emo.emoji}</span>
                      <span className="truncate">{emo.label}</span>
                    </button>
                  )
                })}
              </div>

              {/* Toggle to browse all 15 categories & 121 delivery styles */}
              <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => setIsEmotionDrawerOpen(!isEmotionDrawerOpen)}
                  className="text-xs text-sky-400 hover:text-sky-300 font-semibold flex items-center gap-1.5 transition-colors"
                >
                  <Layers className="w-3.5 h-3.5" />
                  <span>
                    {isEmotionDrawerOpen
                      ? 'Hide Detailed Emotions Catalog'
                      : 'Browse All 15 Categories & 121 Emotions'}
                  </span>
                  {isEmotionDrawerOpen ? (
                    <ChevronUp className="w-3.5 h-3.5" />
                  ) : (
                    <ChevronDown className="w-3.5 h-3.5" />
                  )}
                </button>
                <span className="text-[10px] text-slate-500">
                  {allEmotionsList.length > 0 ? `${allEmotionsList.length} Styles Available` : ''}
                </span>
              </div>

              {/* Collapsible 15-Category & 121-Emotion Browser */}
              {isEmotionDrawerOpen && (
                <div className="space-y-3 pt-2 border-t border-slate-800/80 animate-in fade-in duration-200">
                  {/* Search Input */}
                  <div className="relative">
                    <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
                    <input
                      type="text"
                      value={emotionSearch}
                      onChange={(e) => setEmotionSearch(e.target.value)}
                      placeholder="Search all 121 emotions (e.g. whisper, heartbroken, sarcastic, urgent, joyful)..."
                      className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700/80 text-xs text-white placeholder-slate-500 outline-none focus:border-sky-500"
                    />
                  </div>

                  {/* Category Pills */}
                  <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 text-xs">
                    <button
                      type="button"
                      onClick={() => setSelectedCategory('all')}
                      className={`px-2.5 py-1 rounded-full whitespace-nowrap text-[11px] font-medium transition-all ${
                        selectedCategory === 'all'
                          ? 'bg-sky-500 text-white font-semibold shadow-sm'
                          : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      All Categories
                    </button>
                    {emotionCategories.map((cat) => (
                      <button
                        key={cat.id}
                        type="button"
                        onClick={() => setSelectedCategory(cat.id)}
                        className={`px-2.5 py-1 rounded-full whitespace-nowrap text-[11px] font-medium transition-all ${
                          selectedCategory === cat.id
                            ? 'bg-sky-500 text-white font-semibold shadow-sm'
                            : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        {cat.icon} {cat.name.replace(/^\d+\.\s*/, '')}
                      </button>
                    ))}
                  </div>

                  {/* Filtered Emotions Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 max-h-60 overflow-y-auto pr-1">
                    {filteredEmotions.map((emo) => {
                      const isSel = selectedEmotion === emo.key
                      return (
                        <button
                          key={emo.key}
                          type="button"
                          onClick={() => setSelectedEmotion(emo.key)}
                          className={`p-2.5 rounded-xl border text-left transition-all ${
                            isSel
                              ? 'bg-sky-500/20 border-sky-500/50 text-white shadow-sm ring-1 ring-sky-500/30'
                              : 'bg-slate-950/70 border-slate-800/80 text-slate-300 hover:border-slate-700 hover:bg-slate-900'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-xs text-slate-100">{emo.title}</span>
                            <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 uppercase font-mono">
                              {emo.category_id}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">{emo.meaning}</p>
                        </button>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>

            {/* Speed Control Slider & Presets */}
            <div className="space-y-2 p-4 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <Sliders className="w-3.5 h-3.5 text-sky-400" /> Speaking Speed (Pacing)
                </span>
                <span className="text-xs font-mono font-bold text-sky-400 px-2 py-0.5 rounded bg-sky-500/10 border border-sky-500/20">
                  {speed.toFixed(2)}x
                </span>
              </div>

              <div className="flex items-center space-x-4">
                <input
                  type="range"
                  min="0.75"
                  max="3.0"
                  step="0.05"
                  value={speed}
                  onChange={(e) => setSpeed(parseFloat(e.target.value))}
                  className="flex-1 accent-sky-500 cursor-pointer"
                />
                <button
                  type="button"
                  onClick={() => setSpeed(1.0)}
                  title="Reset to 1.0x"
                  className="p-1 text-slate-500 hover:text-slate-300 transition-colors"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
              </div>

              <div className="flex items-center space-x-1.5 pt-1">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold mr-1">Presets:</span>
                {speedPresets.map((p) => (
                  <button
                    key={p}
                    type="button"
                    onClick={() => setSpeed(p)}
                    className={`px-2 py-0.5 text-[11px] rounded-md font-medium transition-all ${
                      Math.abs(speed - p) < 0.01
                        ? 'bg-sky-500 text-white font-bold'
                        : 'bg-slate-800 text-slate-400 hover:text-white'
                    }`}
                  >
                    {p}x
                  </button>
                ))}
              </div>
            </div>

            {/* Remove Silence Checkbox */}
            <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <label htmlFor="removeSilence" className="flex items-center space-x-3 cursor-pointer select-none">
                <input
                  type="checkbox"
                  id="removeSilence"
                  checked={removeSilence}
                  onChange={(e) => setRemoveSilence(e.target.checked)}
                  className="w-4 h-4 rounded text-sky-500 bg-slate-800 border-slate-700 focus:ring-sky-500 cursor-pointer accent-sky-500"
                />
                <div>
                  <span className="text-xs font-semibold text-slate-200">Remove Silent Gaps</span>
                  <p className="text-[11px] font-normal text-slate-400">
                    Automatically trims pauses and dead silence between sentences for tight, fast pacing
                  </p>
                </div>
              </label>
              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                removeSilence ? 'bg-sky-500/20 text-sky-300 border-sky-500/30' : 'bg-slate-800 text-slate-500 border-slate-700'
              }`}>
                {removeSilence ? 'Silence Trimmed' : 'Natural Pauses'}
              </span>
            </div>

            {/* Primary Generate Button */}
            <button
              type="submit"
              disabled={isGenerating || !scriptText.trim()}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-sky-500 via-sky-600 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-semibold text-sm shadow-lg shadow-sky-500/25 transition-all flex items-center justify-center space-x-2 disabled:opacity-75 disabled:cursor-not-allowed"
            >
              {isGenerating && activeJob ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  <span>
                    Rendering in Background ({activeJob.progress}% • ETA: ~{activeJob.eta_seconds}s)
                  </span>
                </>
              ) : isGenerating ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  <span>Submitting to Background Queue...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Generate Voiceover (192kbps MP3)</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* RIGHT COLUMN: Real-Time Audio Player & Workflow Card */}
        <div className="lg:col-span-4 space-y-5">
          {/* Latest Generated Take Card */}
          <div className="p-5 rounded-2xl bg-[#0d1322] border border-slate-800 space-y-4 shadow-xl">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Volume2 className="w-4 h-4 text-sky-400" /> Active Audio Preview
            </h4>

            {isGenerating && activeJob ? (
              <div className="p-4 rounded-xl bg-slate-900 border border-sky-500/40 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-medium text-sky-400 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-sky-400 animate-ping" />
                    Rendering Take...
                  </span>
                  <span className="text-xs font-mono font-bold text-sky-400">
                    {activeJob.progress}%
                  </span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-sky-500 to-indigo-500 rounded-full transition-all duration-300"
                    style={{ width: `${Math.max(5, activeJob.progress)}%` }}
                  />
                </div>
                <p className="text-xs text-slate-300 truncate">{activeJob.step}</p>
                <div className="flex items-center justify-between text-[11px] font-mono text-slate-500">
                  <span>ETA: ~{activeJob.eta_seconds}s</span>
                  <span>Elapsed: {activeJob.elapsed_seconds}s</span>
                </div>
              </div>
            ) : lastGenerated ? (
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-medium text-emerald-400 flex items-center gap-1">
                      <CheckCircle className="w-3.5 h-3.5" /> Master Audio Ready
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">192kbps MP3</span>
                  </div>

                  <p className="text-xs font-semibold text-slate-100 truncate" title={lastGenerated.filename}>
                    {lastGenerated.filename}
                  </p>

                  {/* Play / Pause Button with Waveform visualizer */}
                  <div className="flex items-center space-x-3 pt-1">
                    <button
                      onClick={() => onPlayAudio(lastGenerated.audio_url, lastGenerated.filename)}
                      className="w-11 h-11 rounded-xl bg-sky-500 hover:bg-sky-400 text-white flex items-center justify-center shadow-lg shadow-sky-500/25 transition-all flex-shrink-0"
                    >
                      {isPlaying && currentPlayingUrl === lastGenerated.audio_url ? (
                        <Pause className="w-5 h-5 fill-current" />
                      ) : (
                        <Play className="w-5 h-5 fill-current ml-0.5" />
                      )}
                    </button>

                    <div className="flex-1 flex items-center space-x-1 h-8 px-2 rounded-lg bg-slate-950/60 border border-slate-800">
                      {[40, 80, 20, 90, 60, 30, 70, 100, 45, 85, 30, 95, 60, 40].map((h, i) => (
                        <div
                          key={i}
                          className={`flex-1 rounded-full transition-all duration-300 ${
                            isPlaying && currentPlayingUrl === lastGenerated.audio_url
                              ? 'bg-sky-400 animate-wave-bar'
                              : 'bg-slate-700'
                          }`}
                          style={{
                            height: `${h}%`,
                            animationDelay: `${i * 70}ms`,
                          }}
                        />
                      ))}
                    </div>
                  </div>
                </div>

                <a
                  href={lastGenerated.audio_url}
                  download={lastGenerated.filename}
                  className="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-xs font-semibold text-slate-200 transition-all flex items-center justify-center space-x-2"
                >
                  <Download className="w-4 h-4 text-sky-400" />
                  <span>Download Master MP3</span>
                </a>
              </div>
            ) : (
              <div className="py-12 px-4 rounded-xl bg-slate-900/50 border border-dashed border-slate-800 text-center space-y-2">
                <FileAudio className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-xs text-slate-400">No audio generated yet.</p>
                <p className="text-[11px] text-slate-600">Enter a script and click Generate to create your first track!</p>
              </div>
            )}
          </div>

          {/* Storytelling & Audio Tips */}
          <div className="p-5 rounded-2xl bg-[#0d1322] border border-slate-800 space-y-3">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-indigo-400" /> Audio Storytelling Tips
            </h4>
            <div className="space-y-2 text-xs text-slate-400 leading-relaxed">
              <div className="flex items-start space-x-2">
                <span className="text-sky-400 font-bold">•</span>
                <span><strong>Multi-Emotion Delivery:</strong> Select matching emotions line-by-line (e.g. Calm narrative ➔ Angry confrontation ➔ Emotional conclusion).</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="text-sky-400 font-bold">•</span>
                <span><strong>Age & Gender Adaptation:</strong> Custom character age (child, young, adult, elder) and gender tone adjustments are automatically applied.</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="text-sky-400 font-bold">•</span>
                <span><strong>Silence Control:</strong> Toggle "Remove Silent Gaps" for snappy, fast-paced dialogue or keep natural pauses for cinematic storytelling.</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

