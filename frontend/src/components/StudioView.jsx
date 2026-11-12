import React, { useState } from 'react'
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
  RotateCcw
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
}) {
  const [scriptText, setScriptText] = useState(
    'दोपहर का 1 बजा है। प्रिया की desk पर मम्मी का बनाया गरमागरम टिफिन रखा है।'
  )
  const [selectedVoice, setSelectedVoice] = useState(voices[0] || '')
  const [language, setLanguage] = useState('hi')
  const [speed, setSpeed] = useState(1.0)
  const [clipTitle, setClipTitle] = useState('')

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
              Apple Silicon Voice Cloning Studio
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                192kbps Broadcast MP3
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Universal Devanagari Normalization active — conjuncts, English loanwords, and numbers expand automatically.
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

              {/* Voice & Emotion Dropdown */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-semibold text-slate-300">Character Voice & Emotion</label>
                  <button
                    type="button"
                    onClick={onOpenVoiceCloner}
                    className="text-[11px] text-sky-400 hover:text-sky-300 font-medium flex items-center gap-1"
                  >
                    + Clone Voice
                  </button>
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
                  <span>Generate MP3 Audio for Filmora</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* RIGHT COLUMN: Real-Time Audio Player & Filmora Workflow Card */}
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
                      <CheckCircle className="w-3.5 h-3.5" /> Ready for Filmora
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
                  <span>Download MP3 Directly</span>
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

          {/* Filmora Storytelling Pro Tips */}
          <div className="p-5 rounded-2xl bg-[#0d1322] border border-slate-800 space-y-3">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Film className="w-4 h-4 text-indigo-400" /> Filmora Timeline Tips
            </h4>
            <div className="space-y-2 text-xs text-slate-400 leading-relaxed">
              <div className="flex items-start space-x-2">
                <span className="text-sky-400 font-bold">•</span>
                <span><strong>Multi-Emotion Beat Matching:</strong> Generate lines sentence-by-sentence with matching emotions (e.g. Calm ➔ Angry Confrontation ➔ Choked Breakdown).</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="text-sky-400 font-bold">•</span>
                <span><strong>Direct Timeline Drag:</strong> MP3s are saved with broadcast -16 LUFS loudness. Drag directly from <code className="text-sky-300">outputs/{activeProject}/</code> into Filmora!</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="text-sky-400 font-bold">•</span>
                <span><strong>Natural Pacing:</strong> 280ms diaphragm breath cadence is pre-calculated between sentences.</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

