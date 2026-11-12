import React, { useState } from 'react'
import {
  FolderKanban,
  FolderPlus,
  Archive,
  ArrowRight,
  CheckCircle,
  FileAudio,
  HardDrive
} from 'lucide-react'

export default function ProjectsView({
  projects,
  activeProject,
  setActiveProject,
  onCreateProject,
  setCurrentTab,
  onExportZip,
  isExportingZip,
  projectFilesCount,
}) {
  const [newProjectName, setNewProjectName] = useState('')

  const handleCreate = (e) => {
    e.preventDefault()
    if (!newProjectName.trim()) return
    onCreateProject(newProjectName.trim())
    setNewProjectName('')
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0d1322] border border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Project Workspaces</h2>
          <p className="text-xs text-slate-400 mt-1">
            Organize storytelling dialogues, podcast segments, and character takes into isolated folders.
          </p>
        </div>

        {/* Create Project Quick Form */}
        <form onSubmit={handleCreate} className="flex items-center space-x-2">
          <input
            type="text"
            value={newProjectName}
            onChange={(e) => setNewProjectName(e.target.value)}
            placeholder="New Project Name (e.g. Horror_Ep1)..."
            className="px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 text-xs outline-none focus:border-sky-500 w-56 sm:w-64"
          />
          <button
            type="submit"
            disabled={!newProjectName.trim()}
            className="flex items-center space-x-1.5 px-4 py-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-white font-semibold text-xs transition-all shadow-md shadow-sky-500/20 disabled:opacity-50"
          >
            <FolderPlus className="w-4 h-4" />
            <span>Create</span>
          </button>
        </form>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {projects.map((proj) => {
          const isCurrent = proj === activeProject
          const fileCount = projectFilesCount?.[proj] ?? '—'
          return (
            <div
              key={proj}
              className={`p-6 rounded-2xl border transition-all space-y-4 flex flex-col justify-between ${
                isCurrent
                  ? 'bg-gradient-to-br from-slate-900 via-sky-950/20 to-[#0d1322] border-sky-500/40 shadow-xl shadow-sky-500/10'
                  : 'bg-[#0d1322] border-slate-800 hover:border-slate-700'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-sky-400">
                    <FolderKanban className="w-5 h-5" />
                  </div>
                  {isCurrent ? (
                    <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-sky-500/20 text-sky-400 border border-sky-500/30 flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" /> ACTIVE
                    </span>
                  ) : (
                    <button
                      onClick={() => setActiveProject(proj)}
                      className="text-xs text-slate-400 hover:text-sky-400 font-medium px-2 py-1 rounded hover:bg-slate-800 transition-colors"
                    >
                      Make Active
                    </button>
                  )}
                </div>

                <h3 className="text-base font-bold text-white tracking-tight truncate">{proj}</h3>
                <p className="text-xs font-mono text-slate-400 mt-0.5">outputs/{proj}/</p>
              </div>

              <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between">
                <button
                  onClick={() => {
                    setActiveProject(proj)
                    setCurrentTab('media')
                  }}
                  className="text-xs font-medium text-sky-400 hover:text-sky-300 flex items-center gap-1"
                >
                  <span>Open Media</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>

                <button
                  onClick={() => onExportZip(proj)}
                  disabled={isExportingZip}
                  className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-slate-200 transition-colors"
                  title="Download Project ZIP"
                >
                  <Archive className="w-3.5 h-3.5" />
                  <span>ZIP</span>
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

