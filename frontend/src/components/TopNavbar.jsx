import React, { useState } from 'react'
import {
  Folder,
  Plus,
  Archive,
  CheckCircle2,
  ChevronDown,
  Layers,
  Sparkles
} from 'lucide-react'

export default function TopNavbar({
  currentTab,
  projects,
  activeProject,
  setActiveProject,
  onOpenNewProjectModal,
  onExportZip,
  isExportingZip,
}) {
  const [dropdownOpen, setDropdownOpen] = useState(false)

  const tabTitles = {
    studio: { title: 'Voiceover Studio', subtitle: 'Generate multi-character voiceovers with 10 acting emotions' },
    dashboard: { title: 'Executive Audio Dashboard', subtitle: 'Overview metrics across projects, cloned voices, and exports' },
    projects: { title: 'Project Workspaces', subtitle: 'Manage isolated audio folders for episodes, stories, and scenes' },
    media: { title: 'Project Media Library', subtitle: `Browse, audition, rename, and download audio takes in ${activeProject}` },
    vault: { title: 'Character Voice Vault', subtitle: 'View emotion coverage matrix and audition character voices' },
    record: { title: 'Character Voice Cloner', subtitle: 'Step-by-step vocal coach to clone emotions with acting scripts' },
  }

  const currentInfo = tabTitles[currentTab] || { title: 'Studio', subtitle: '' }

  return (
    <header className="h-20 bg-[#0d1322]/80 backdrop-blur-md border-b border-slate-800/80 px-8 flex items-center justify-between sticky top-0 z-20">
      {/* Title & Subtitle */}
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          {currentInfo.title}
        </h2>
        <p className="text-xs text-slate-400">{currentInfo.subtitle}</p>
      </div>

      {/* Right Controls: Project Workspace Dropdown, New Project, Zip Export */}
      <div className="flex items-center space-x-3">
        {/* Project Selector Dropdown */}
        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center space-x-2.5 px-3.5 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700/80 text-sm font-medium text-slate-200 transition-all shadow-sm"
          >
            <Folder className="w-4 h-4 text-sky-400" />
            <span className="text-xs text-slate-400 font-normal">Project:</span>
            <span className="font-semibold text-white max-w-[140px] truncate">{activeProject}</span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-56 rounded-xl bg-[#0f172a] border border-slate-700/80 shadow-2xl py-1.5 z-30 animate-in fade-in duration-100">
              <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
                Switch Workspace
              </div>
              <div className="max-h-56 overflow-y-auto py-1">
                {projects.map((p) => (
                  <button
                    key={p}
                    onClick={() => {
                      setActiveProject(p)
                      setDropdownOpen(false)
                    }}
                    className={`w-full text-left px-3.5 py-2 text-xs flex items-center justify-between hover:bg-slate-800/60 transition-colors ${
                      p === activeProject ? 'text-sky-400 font-bold bg-sky-500/10' : 'text-slate-300'
                    }`}
                  >
                    <span className="truncate">{p}</span>
                    {p === activeProject && <CheckCircle2 className="w-3.5 h-3.5 text-sky-400" />}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* New Project Button */}
        <button
          onClick={onOpenNewProjectModal}
          className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-xs font-semibold text-slate-200 transition-all"
        >
          <Plus className="w-3.5 h-3.5 text-sky-400" />
          <span>New Project</span>
        </button>

        {/* Download Project ZIP */}
        <button
          onClick={onExportZip}
          disabled={isExportingZip}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-sky-600/20 transition-all disabled:opacity-50"
        >
          <Archive className="w-3.5 h-3.5" />
          <span>{isExportingZip ? 'Compressing...' : 'Export ZIP'}</span>
        </button>
      </div>
    </header>
  )
}

