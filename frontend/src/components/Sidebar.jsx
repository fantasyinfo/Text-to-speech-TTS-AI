import React from 'react'
import {
  Mic2,
  LayoutDashboard,
  FolderKanban,
  Library,
  Users,
  PlusCircle,
  Cpu,
  Sparkles,
  Volume2,
  HardDrive
} from 'lucide-react'

export default function Sidebar({ currentTab, setCurrentTab, activeProject, stats }) {
  const workspaceItems = [
    { id: 'studio', label: 'Voiceover Studio', icon: Mic2, badge: 'Studio' },
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'projects', label: 'Projects', icon: FolderKanban, count: stats?.total_projects },
    { id: 'media', label: 'Media Library', icon: Library, count: stats?.total_audio_tracks },
  ]

  const voiceLabItems = [
    { id: 'vault', label: 'Character Vault', icon: Users, count: stats?.total_characters },
    { id: 'record', label: 'Clone New Voice', icon: PlusCircle, badge: '10 Emotions' },
  ]

  return (
    <aside className="w-64 bg-[#0d1322] border-r border-slate-800/80 flex flex-col flex-shrink-0 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/70 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-sky-500/20 text-white font-bold">
            <Volume2 className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-white text-base tracking-tight flex items-center gap-1.5">
              VoxStudio <span className="text-[10px] px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-400 font-semibold border border-sky-500/30">AI</span>
            </h1>
            <p className="text-[11px] text-slate-400 leading-none">AI Voice Studio</p>
          </div>
        </div>
      </div>

      {/* Nav List */}
      <div className="flex-1 py-5 px-3 space-y-6 overflow-y-auto">
        {/* Workspace Section */}
        <div>
          <p className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Workspace
          </p>
          <div className="space-y-1">
            {workspaceItems.map((item) => {
              const Icon = item.icon
              const isActive = currentTab === item.id
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-800 text-slate-400 font-medium border border-slate-700">
                      {item.badge}
                    </span>
                  )}
                  {item.count !== undefined && !item.badge && (
                    <span className="text-[11px] text-slate-400 font-medium px-2 py-0.5 rounded bg-slate-800/80">
                      {item.count}
                    </span>
                  )}
                </button>
              )
            })}
          </div>
        </div>

        {/* Voice Lab Section */}
        <div>
          <p className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Voice Lab
          </p>
          <div className="space-y-1">
            {voiceLabItems.map((item) => {
              const Icon = item.icon
              const isActive = currentTab === item.id
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-sky-500/20 text-sky-300 font-medium border border-sky-500/30">
                      {item.badge}
                    </span>
                  )}
                  {item.count !== undefined && !item.badge && (
                    <span className="text-[11px] text-slate-400 font-medium px-2 py-0.5 rounded bg-slate-800/80">
                      {item.count}
                    </span>
                  )}
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {/* Active Workspace / Neural Audio Engine Status Card */}
      <div className="p-3 border-t border-slate-800/70 bg-[#0a0f1d]">
        <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium text-slate-400 flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-emerald-400" /> Neural Audio Engine
            </span>
            <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Offline Ready
            </span>
          </div>
          <div className="pt-1 border-t border-slate-800/60">
            <p className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Active Folder</p>
            <p className="text-[12px] font-mono text-sky-400 truncate" title={`outputs/${activeProject}/`}>
              outputs/{activeProject}/
            </p>
          </div>
        </div>
      </div>
    </aside>
  )
}

