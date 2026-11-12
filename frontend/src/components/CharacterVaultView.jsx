import React from 'react'
import {
  Users,
  Play,
  Pause,
  PlusCircle,
  CheckCircle2,
  Mic,
  Sparkles,
  Volume2
} from 'lucide-react'

export default function CharacterVaultView({
  characters,
  onOpenVoiceCloner,
  onPlayAudio,
  currentPlayingUrl,
  isPlaying,
}) {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0d1322] border border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Character Voice Vault</h2>
          <p className="text-xs text-slate-400 mt-1">
            Build multi-emotion vocal profiles so characters sound authentic when crying, angry, laughing, or exhausted.
          </p>
        </div>

        <button
          onClick={() => onOpenVoiceCloner()}
          className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-sky-500/20 transition-all"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Clone New Character / Emotion</span>
        </button>
      </div>

      {/* Characters List */}
      {characters.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {characters.map((char) => (
            <div
              key={char.name}
              className="p-6 rounded-2xl bg-[#0d1322] border border-slate-800 space-y-5 shadow-xl"
            >
              {/* Character Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-white font-bold text-lg shadow-md shadow-sky-500/20">
                    {char.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white">{char.name}</h3>
                    <p className="text-xs text-slate-400">
                      {char.recorded_count} of {char.total_emotions} emotions recorded
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-sm font-bold text-sky-400 font-mono">
                    {char.completeness_percent}%
                  </span>
                  <div className="w-20 h-1.5 rounded-full bg-slate-800 mt-1 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-sky-500 to-indigo-500 rounded-full"
                      style={{ width: `${char.completeness_percent}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* 10 Emotion Badges Matrix */}
              <div className="space-y-2 pt-2 border-t border-slate-800/80">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  Emotional Profiles:
                </span>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(char.emotions).map(([emoKey, emoData]) => (
                    <div
                      key={emoKey}
                      className={`p-2.5 rounded-xl border flex items-center justify-between text-xs transition-colors ${
                        emoData.recorded
                          ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                          : 'bg-slate-900/40 border-slate-800 text-slate-500'
                      }`}
                    >
                      <div className="flex items-center space-x-1.5 truncate">
                        {emoData.recorded ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                        ) : (
                          <div className="w-3.5 h-3.5 rounded-full border border-slate-700 flex-shrink-0" />
                        )}
                        <span className="truncate capitalize">{emoData.title || emoKey}</span>
                      </div>

                      {emoData.recorded ? (
                        <button
                          onClick={() => onPlayAudio(emoData.audio_url, `${char.name} - ${emoKey}`)}
                          className="p-1 rounded-md text-emerald-400 hover:text-white hover:bg-emerald-500/20 transition-colors"
                          title="Audition Sample"
                        >
                          {isPlaying && currentPlayingUrl === emoData.audio_url ? (
                            <Pause className="w-3.5 h-3.5 fill-current" />
                          ) : (
                            <Play className="w-3.5 h-3.5 fill-current" />
                          )}
                        </button>
                      ) : (
                        <button
                          onClick={() => onOpenVoiceCloner(char.name, emoKey)}
                          className="text-[10px] text-sky-400 hover:text-sky-300 font-semibold px-1.5 py-0.5 rounded bg-sky-500/10 hover:bg-sky-500/20 transition-colors"
                        >
                          + Record
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="py-20 text-center rounded-2xl bg-[#0d1322] border border-slate-800 space-y-3">
          <Users className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-semibold text-slate-300">No Custom Characters Yet</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Click "Clone New Character" to record your first 10-15s sample and build your emotional cast!
          </p>
          <button
            onClick={() => onOpenVoiceCloner()}
            className="px-4 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 text-white font-semibold text-xs shadow-md shadow-sky-500/20 transition-all inline-flex items-center gap-1.5"
          >
            <Mic className="w-4 h-4" />
            <span>Record Base Voice</span>
          </button>
        </div>
      )}
    </div>
  )
}

