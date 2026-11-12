import React from 'react'
import {
  FileAudio,
  AlertTriangle,
  FolderKanban,
  ShieldCheck,
  Play,
  Pause,
  Download,
  Plus,
  Mic,
  ArrowUpRight,
  Clock,
  Sparkles
} from 'lucide-react'

export default function DashboardView({
  stats,
  projects,
  activeProject,
  setActiveProject,
  setCurrentTab,
  onPlayAudio,
  currentPlayingUrl,
  isPlaying,
  onOpenVoiceCloner,
}) {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Executive Overview Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-[#0d1322] to-[#11192e] border border-slate-800">
        <div>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20 mb-2">
            Executive Voice Engine Overview
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Multi-Character Storytelling & Voice Synthesis
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time local neural synthesis across Hindi Devanagari & English storytelling scripts.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onOpenVoiceCloner}
            className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-xs font-semibold text-slate-200 transition-all shadow-sm"
          >
            <Mic className="w-4 h-4 text-sky-400" />
            <span>Clone Voice</span>
          </button>
          <button
            onClick={() => setCurrentTab('studio')}
            className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-sky-500/20 transition-all"
          >
            <Sparkles className="w-4 h-4" />
            <span>Launch Studio</span>
          </button>
        </div>
      </div>

      {/* 4 SaaS Stat Cards (Matching Image 2) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Stat 1: Generated Audio Tracks */}
        <div className="p-5 rounded-2xl bg-[#0d1322] border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Generated Tracks</span>
            <FileAudio className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">
            {stats?.total_audio_tracks ?? 0}
          </div>
          <div className="flex items-center space-x-2 text-[11px] text-slate-500">
            <span className="text-emerald-400 font-semibold">100% Local</span>
            <span>• 192kbps MP3s</span>
          </div>
        </div>

        {/* Stat 2: Active Projects */}
        <div className="p-5 rounded-2xl bg-[#0d1322] border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Project Workspaces</span>
            <FolderKanban className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">
            {stats?.total_projects ?? 1}
          </div>
          <div className="flex items-center space-x-2 text-[11px] text-slate-500">
            <span className="text-sky-400 font-semibold">{activeProject}</span>
            <span>active</span>
          </div>
        </div>

        {/* Stat 3: Cloned Characters */}
        <div className="p-5 rounded-2xl bg-[#0d1322] border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Cloned Characters</span>
            <Mic className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">
            {stats?.total_characters ?? 0}
          </div>
          <div className="flex items-center space-x-2 text-[11px] text-slate-500">
            <span className="text-emerald-400 font-semibold">
              {stats?.total_emotion_samples ?? 0}
            </span>
            <span>emotions recorded</span>
          </div>
        </div>

        {/* Stat 4: Devanagari Engine Status */}
        <div className="p-5 rounded-2xl bg-[#0d1322] border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Engine Normalizers</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 font-mono">
            15 Rules
          </div>
          <div className="text-[11px] text-slate-500 truncate" title="Conjuncts, Loanwords, Nukta, Chandrabindu, Times">
            Conjuncts, Numbers, Hinglish
          </div>
        </div>
      </div>

      {/* Lower Dashboard Grid: Recent Tracks & Project Workspaces */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recent Voiceover Generations */}
        <div className="lg:col-span-8 p-6 rounded-2xl bg-[#0d1322] border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-sky-400" /> Recent Voiceover Takes
            </h3>
            <button
              onClick={() => setCurrentTab('media')}
              className="text-xs font-medium text-sky-400 hover:text-sky-300 flex items-center gap-1"
            >
              <span>View All Files</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {stats?.recent_generations?.length ? (
            <div className="space-y-2">
              {stats.recent_generations.map((track) => (
                <div
                  key={track.url}
                  className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/70 hover:bg-slate-900 border border-slate-800 transition-colors"
                >
                  <div className="flex items-center space-x-3 min-w-0">
                    <button
                      onClick={() => onPlayAudio(track.url, track.filename)}
                      className="w-9 h-9 rounded-lg bg-sky-500/20 hover:bg-sky-500/30 text-sky-400 flex items-center justify-center flex-shrink-0 transition-colors"
                    >
                      {isPlaying && currentPlayingUrl === track.url ? (
                        <Pause className="w-4 h-4 fill-current" />
                      ) : (
                        <Play className="w-4 h-4 fill-current ml-0.5" />
                      )}
                    </button>
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-slate-200 truncate">{track.filename}</p>
                      <div className="flex items-center space-x-2 text-[11px] text-slate-500 mt-0.5">
                        <span className="px-1.5 py-0.2 rounded bg-slate-800 text-sky-400 font-mono text-[10px]">
                          {track.project}
                        </span>
                        <span>•</span>
                        <span>{track.size_kb}</span>
                        <span>•</span>
                        <span>{track.modified}</span>
                      </div>
                    </div>
                  </div>

                  <a
                    href={track.url}
                    download={track.filename}
                    className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
                    title="Download MP3"
                  >
                    <Download className="w-4 h-4" />
                  </a>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-12 text-center text-xs text-slate-500 border border-dashed border-slate-800 rounded-xl">
              No recent generations yet. Generate speech in the studio to see them here!
            </div>
          )}
        </div>

        {/* Right Side: Project Workspaces Queue */}
        <div className="lg:col-span-4 p-6 rounded-2xl bg-[#0d1322] border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <FolderKanban className="w-4 h-4 text-indigo-400" /> Workspaces
            </h3>
            <button
              onClick={() => setCurrentTab('projects')}
              className="text-xs font-medium text-sky-400 hover:text-sky-300"
            >
              Manage
            </button>
          </div>

          <div className="space-y-2">
            {projects.map((proj) => {
              const isCurrent = proj === activeProject
              return (
                <div
                  key={proj}
                  onClick={() => setActiveProject(proj)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                    isCurrent
                      ? 'bg-sky-500/10 border-sky-500/30'
                      : 'bg-slate-900/60 border-slate-800 hover:bg-slate-800/60'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <p className={`text-xs font-semibold truncate ${isCurrent ? 'text-sky-400' : 'text-slate-200'}`}>
                      {proj}
                    </p>
                    {isCurrent && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-sky-500/20 text-sky-400 border border-sky-500/30">
                        ACTIVE
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] font-mono text-slate-500 mt-1">outputs/{proj}/</p>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

