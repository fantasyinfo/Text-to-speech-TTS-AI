import React, { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import TopNavbar from './components/TopNavbar'
import StudioView from './components/StudioView'
import DashboardView from './components/DashboardView'
import ProjectsView from './components/ProjectsView'
import MediaLibraryView from './components/MediaLibraryView'
import CharacterVaultView from './components/CharacterVaultView'
import RecordEmotionModal from './components/RecordEmotionModal'
import NewProjectModal from './components/NewProjectModal'
import AudioPlayerBar from './components/AudioPlayerBar'

export default function App() {
  const [currentTab, setCurrentTab] = useState('studio')
  const [projects, setProjects] = useState(['Default_Project'])
  const [activeProject, setActiveProject] = useState('Default_Project')
  const [voices, setVoices] = useState([])
  const [characters, setCharacters] = useState([])
  const [emotionsGuide, setEmotionsGuide] = useState({})
  const [stats, setStats] = useState(null)
  const [files, setFiles] = useState([])
  const [lastGenerated, setLastGenerated] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isExportingZip, setIsExportingZip] = useState(false)

  // Audio Player State
  const [currentPlayingUrl, setCurrentPlayingUrl] = useState(null)
  const [currentPlayingTitle, setCurrentPlayingTitle] = useState('')
  const [isPlaying, setIsPlaying] = useState(false)

  // Modals
  const [isNewProjectModalOpen, setIsNewProjectModalOpen] = useState(false)
  const [isRecordModalOpen, setIsRecordModalOpen] = useState(false)
  const [recordInitialChar, setRecordInitialChar] = useState('')
  const [recordInitialEmotion, setRecordInitialEmotion] = useState('neutral')

  // Toast feedback
  const [toast, setToast] = useState(null)
  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 4000)
  }

  // Load initial data
  const fetchAllData = async () => {
    try {
      // 1. Projects
      const projRes = await fetch('/api/projects')
      const projData = await projRes.json()
      if (projData.projects) {
        setProjects(projData.projects)
        if (!projData.projects.includes(activeProject)) {
          setActiveProject(projData.default || projData.projects[0])
        }
      }

      // 2. Voices
      const voicesRes = await fetch('/api/voices')
      const voicesData = await voicesRes.json()
      if (voicesData.voices) {
        setVoices(voicesData.voices)
      }

      // 3. Characters Roster
      const charRes = await fetch('/api/characters')
      const charData = await charRes.json()
      if (charData.characters) {
        setCharacters(charData.characters)
      }

      // 4. Emotions Guide
      const emoRes = await fetch('/api/emotions-guide')
      const emoData = await emoRes.json()
      if (emoData.emotions) {
        setEmotionsGuide(emoData.emotions)
      }

      // 5. Dashboard Stats
      const statsRes = await fetch('/api/stats')
      const statsData = await statsRes.json()
      setStats(statsData)
    } catch (err) {
      console.error('Error fetching initial data:', err)
    }
  }

  // Load files whenever active project changes
  const fetchProjectFiles = async (projName) => {
    try {
      const res = await fetch(`/api/projects/${projName}/files`)
      const data = await res.json()
      setFiles(data.files || [])
    } catch (err) {
      console.error('Error fetching project files:', err)
    }
  }

  useEffect(() => {
    fetchAllData()
  }, [])

  useEffect(() => {
    if (activeProject) {
      fetchProjectFiles(activeProject)
    }
  }, [activeProject])

  // Handlers
  const handlePlayAudio = (url, title) => {
    if (currentPlayingUrl === url) {
      setIsPlaying(!isPlaying)
    } else {
      setCurrentPlayingUrl(url)
      setCurrentPlayingTitle(title)
      setIsPlaying(true)
    }
  }

  const handleGenerateAudio = async (payload) => {
    setIsGenerating(true)
    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Synthesis failed.')
      }

      setLastGenerated(data)
      showToast(data.status || `Saved ${data.filename}`)
      fetchProjectFiles(activeProject)
      // refresh stats
      const statsRes = await fetch('/api/stats')
      setStats(await statsRes.json())
    } catch (err) {
      showToast(err.message, 'error')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleCreateProject = async (name) => {
    try {
      const res = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      })
      const data = await res.json()
      if (data.projects) {
        setProjects(data.projects)
        setActiveProject(data.name)
        showToast(data.message)
      }
    } catch (err) {
      showToast('Failed to create project: ' + err.message, 'error')
    }
  }

  const handleRenameAudio = async (project, oldName, newName) => {
    try {
      const res = await fetch(`/api/projects/${project}/rename`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ old_filename: oldName, new_filename: newName }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail)
      showToast(data.message)
      fetchProjectFiles(project)
    } catch (err) {
      showToast(err.message, 'error')
    }
  }

  const handleDeleteAudio = async (project, filename) => {
    try {
      const res = await fetch(`/api/projects/${project}/files/${filename}`, {
        method: 'DELETE',
      })
      const data = await res.json()
      showToast(data.message)
      fetchProjectFiles(project)
      if (currentPlayingUrl?.includes(filename)) {
        setIsPlaying(false)
        setCurrentPlayingUrl(null)
      }
    } catch (err) {
      showToast('Failed to delete audio: ' + err.message, 'error')
    }
  }

  const handleExportZip = async (project = activeProject) => {
    setIsExportingZip(true)
    try {
      const targetUrl = `/api/projects/${project}/export-zip`
      const a = document.createElement('a')
      a.href = targetUrl
      a.download = `${project}_Audio_Export.zip`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      showToast(`Exporting ZIP archive for ${project}...`)
    } catch (err) {
      showToast('Failed to export ZIP: ' + err.message, 'error')
    } finally {
      setIsExportingZip(false)
    }
  }

  const handleOpenVoiceCloner = (charName = '', emoKey = 'neutral') => {
    setRecordInitialChar(charName)
    setRecordInitialEmotion(emoKey)
    setIsRecordModalOpen(true)
  }

  return (
    <div className="flex h-screen bg-[#070b14] text-slate-100 overflow-hidden font-sans">
      {/* Toast Notification */}
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-xl border text-xs font-semibold shadow-2xl flex items-center space-x-2 animate-in slide-in-from-top duration-200 ${
            toast.type === 'error'
              ? 'bg-rose-950/90 border-rose-500/50 text-rose-300'
              : 'bg-sky-950/90 border-sky-500/50 text-sky-200'
          }`}
        >
          <span>{toast.msg}</span>
        </div>
      )}

      {/* Left Sidebar */}
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        activeProject={activeProject}
        stats={stats}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Navbar */}
        <TopNavbar
          currentTab={currentTab}
          projects={projects}
          activeProject={activeProject}
          setActiveProject={setActiveProject}
          onOpenNewProjectModal={() => setIsNewProjectModalOpen(true)}
          onExportZip={() => handleExportZip(activeProject)}
          isExportingZip={isExportingZip}
        />

        {/* Dynamic Tab Body */}
        <main className="flex-1 overflow-y-auto p-8 pb-32">
          {currentTab === 'studio' && (
            <StudioView
              voices={voices}
              activeProject={activeProject}
              onGenerateAudio={handleGenerateAudio}
              isGenerating={isGenerating}
              lastGenerated={lastGenerated}
              onPlayAudio={handlePlayAudio}
              currentPlayingUrl={currentPlayingUrl}
              isPlaying={isPlaying}
              onOpenVoiceCloner={() => handleOpenVoiceCloner()}
            />
          )}

          {currentTab === 'dashboard' && (
            <DashboardView
              stats={stats}
              projects={projects}
              activeProject={activeProject}
              setActiveProject={setActiveProject}
              setCurrentTab={setCurrentTab}
              onPlayAudio={handlePlayAudio}
              currentPlayingUrl={currentPlayingUrl}
              isPlaying={isPlaying}
              onOpenVoiceCloner={() => handleOpenVoiceCloner()}
            />
          )}

          {currentTab === 'projects' && (
            <ProjectsView
              projects={projects}
              activeProject={activeProject}
              setActiveProject={setActiveProject}
              onCreateProject={handleCreateProject}
              setCurrentTab={setCurrentTab}
              onExportZip={handleExportZip}
              isExportingZip={isExportingZip}
            />
          )}

          {currentTab === 'media' && (
            <MediaLibraryView
              activeProject={activeProject}
              files={files}
              onRefreshFiles={() => fetchProjectFiles(activeProject)}
              onPlayAudio={handlePlayAudio}
              currentPlayingUrl={currentPlayingUrl}
              isPlaying={isPlaying}
              onRenameAudio={handleRenameAudio}
              onDeleteAudio={handleDeleteAudio}
              onExportZip={() => handleExportZip(activeProject)}
              isExportingZip={isExportingZip}
            />
          )}

          {currentTab === 'vault' && (
            <CharacterVaultView
              characters={characters}
              onOpenVoiceCloner={handleOpenVoiceCloner}
              onPlayAudio={handlePlayAudio}
              currentPlayingUrl={currentPlayingUrl}
              isPlaying={isPlaying}
            />
          )}

          {currentTab === 'record' && (
            <div className="max-w-3xl mx-auto">
              <RecordEmotionModal
                isOpen={true}
                onClose={() => setCurrentTab('vault')}
                initialCharacter=""
                initialEmotion="neutral"
                characters={characters}
                emotionsGuide={emotionsGuide}
                onSaveSuccess={() => {
                  fetchAllData()
                  showToast('Emotion voice recorded & saved successfully!')
                  setCurrentTab('vault')
                }}
              />
            </div>
          )}
        </main>
      </div>

      {/* Floating Record Emotion Modal */}
      {isRecordModalOpen && (
        <RecordEmotionModal
          isOpen={isRecordModalOpen}
          onClose={() => setIsRecordModalOpen(false)}
          initialCharacter={recordInitialChar}
          initialEmotion={recordInitialEmotion}
          characters={characters}
          emotionsGuide={emotionsGuide}
          onSaveSuccess={() => {
            fetchAllData()
            showToast('Character emotion sample saved successfully!')
          }}
        />
      )}

      {/* New Project Modal */}
      <NewProjectModal
        isOpen={isNewProjectModalOpen}
        onClose={() => setIsNewProjectModalOpen(false)}
        onCreateProject={handleCreateProject}
      />

      {/* Persistent Bottom Audio Player Bar */}
      <AudioPlayerBar
        audioUrl={currentPlayingUrl}
        trackTitle={currentPlayingTitle}
        isPlaying={isPlaying}
        setIsPlaying={setIsPlaying}
        onClose={() => {
          setIsPlaying(false)
          setCurrentPlayingUrl(null)
        }}
      />
    </div>
  )
}

