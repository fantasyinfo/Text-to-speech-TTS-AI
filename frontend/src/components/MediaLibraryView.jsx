import React, { useState } from 'react'
import {
  FileAudio,
  Play,
  Pause,
  Download,
  Edit2,
  Trash2,
  Search,
  Archive,
  RefreshCw,
  Check,
  X
} from 'lucide-react'

export default function MediaLibraryView({
  activeProject,
  files,
  onRefreshFiles,
  onPlayAudio,
  currentPlayingUrl,
  isPlaying,
  onRenameAudio,
  onDeleteAudio,
  onExportZip,
  isExportingZip,
}) {
  const [searchQuery, setSearchQuery] = useState('')
  const [editingFile, setEditingFile] = useState(null)
  const [newFileName, setNewFileName] = useState('')

  const filteredFiles = files.filter((f) =>
    f.filename.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleStartRename = (filename) => {
    setEditingFile(filename)
    // strip extension for cleaner editing
    const stem = filename.replace(/\.[^/.]+$/, '')
    setNewFileName(stem)
  }

  const handleSaveRename = (oldName) => {
    if (!newFileName.trim()) return
    onRenameAudio(activeProject, oldName, newFileName.trim())
    setEditingFile(null)
    setNewFileName('')
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header with Search and Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0d1322] border border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-xl font-bold text-white tracking-tight">Project Media Library</h2>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20 font-mono font-medium">
              {activeProject}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Browse, play, rename, and manage all high-grade 192kbps MP3 takes in <code className="text-sky-300">outputs/{activeProject}/</code>.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onRefreshFiles}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-slate-300 transition-colors"
            title="Refresh Files"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={onExportZip}
            disabled={isExportingZip || files.length === 0}
            className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-sky-600/20 transition-all disabled:opacity-50"
          >
            <Archive className="w-4 h-4" />
            <span>{isExportingZip ? 'Compressing...' : 'Export Project ZIP'}</span>
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="w-4 h-4 text-slate-500 absolute left-4 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder={`Search ${files.length} audio tracks in ${activeProject}...`}
          className="w-full pl-11 pr-4 py-3 rounded-xl bg-[#0d1322] border border-slate-800 focus:border-sky-500 focus:ring-1 focus:ring-sky-500 text-slate-200 text-xs outline-none"
        />
      </div>

      {/* Tracks Table */}
      <div className="rounded-2xl bg-[#0d1322] border border-slate-800 overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 bg-slate-900/40 flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
          <span>Track Details</span>
          <div className="hidden sm:flex items-center space-x-8 pr-4">
            <span>Size</span>
            <span>Created</span>
            <span>Actions</span>
          </div>
        </div>

        {filteredFiles.length > 0 ? (
          <div className="divide-y divide-slate-800/60">
            {filteredFiles.map((f) => (
              <div
                key={f.filename}
                className="p-4 flex flex-col sm:flex-row sm:items-center justify-between hover:bg-slate-900/50 transition-colors gap-3"
              >
                {/* Left: Player & Title / Rename Form */}
                <div className="flex items-center space-x-3 min-w-0 flex-1">
                  <button
                    onClick={() => onPlayAudio(f.url, f.filename)}
                    className="w-10 h-10 rounded-xl bg-sky-500/20 hover:bg-sky-500 text-sky-400 hover:text-white flex items-center justify-center flex-shrink-0 transition-all"
                  >
                    {isPlaying && currentPlayingUrl === f.url ? (
                      <Pause className="w-4 h-4 fill-current" />
                    ) : (
                      <Play className="w-4 h-4 fill-current ml-0.5" />
                    )}
                  </button>

                  <div className="min-w-0 flex-1">
                    {editingFile === f.filename ? (
                      <div className="flex items-center space-x-2">
                        <input
                          type="text"
                          value={newFileName}
                          onChange={(e) => setNewFileName(e.target.value)}
                          className="px-2.5 py-1 text-xs bg-slate-950 border border-sky-500 rounded-lg text-white outline-none flex-1 max-w-xs"
                          autoFocus
                        />
                        <button
                          onClick={() => handleSaveRename(f.filename)}
                          className="p-1 rounded bg-sky-500 text-white hover:bg-sky-400"
                          title="Save Rename"
                        >
                          <Check className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => setEditingFile(null)}
                          className="p-1 rounded bg-slate-800 text-slate-400 hover:text-white"
                          title="Cancel"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <p className="text-xs font-semibold text-slate-200 truncate" title={f.filename}>
                          {f.filename}
                        </p>
                        <button
                          onClick={() => handleStartRename(f.filename)}
                          className="p-1 text-slate-500 hover:text-sky-400 rounded transition-colors"
                          title="Rename Track"
                        >
                          <Edit2 className="w-3 h-3" />
                        </button>
                      </div>
                    )}
                    <div className="flex items-center space-x-2 text-[11px] text-slate-500 mt-0.5 sm:hidden">
                      <span>{f.size_kb}</span>
                      <span>•</span>
                      <span>{f.modified}</span>
                    </div>
                  </div>
                </div>

                {/* Right: Metadata & Actions */}
                <div className="flex items-center justify-between sm:justify-end space-x-6 sm:pl-4">
                  <span className="text-xs text-slate-400 font-mono hidden sm:inline">{f.size_kb}</span>
                  <span className="text-xs text-slate-500 hidden sm:inline">{f.modified}</span>

                  <div className="flex items-center space-x-2">
                    <a
                      href={f.url}
                      download={f.filename}
                      className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
                      title="Download MP3"
                    >
                      <Download className="w-4 h-4" />
                    </a>
                    <button
                      onClick={() => {
                        if (confirm(`Delete audio take '${f.filename}' permanently?`)) {
                          onDeleteAudio(activeProject, f.filename)
                        }
                      }}
                      className="p-2 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                      title="Delete Track"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-16 text-center text-xs text-slate-500 space-y-2">
            <FileAudio className="w-10 h-10 text-slate-600 mx-auto" />
            <p className="font-semibold text-slate-400">No audio takes found in this project.</p>
            <p className="text-slate-600">Switch to the Voiceover Studio to synthesize your first scene!</p>
          </div>
        )}
      </div>
    </div>
  )
}

