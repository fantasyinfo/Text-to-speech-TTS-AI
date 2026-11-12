import React, { useState, useEffect, useRef } from 'react'
import Sidebar from './components/Sidebar'
import TopNavbar from './components/TopNavbar'
import StudioView from './components/StudioView'
import DashboardView from './components/DashboardView'
import ProjectsView from './components/ProjectsView'
import MediaLibraryView from './components/MediaLibraryView'
import CharacterVaultView from './components/CharacterVaultView'
import RecordEmotionModal from './components/RecordEmotionModal'
import EditCharacterModal from './components/EditCharacterModal'
import NewProjectModal from './components/NewProjectModal'
import AudioPlayerBar from './components/AudioPlayerBar'
import JobProgressWidget from './components/JobProgressWidget'

export default function App() {
  const [currentTab, setCurrentTab] = useState('studio')
  const [projects, setProjects] = useState(['Default_Project'])
  const [activeProject, setActiveProject] = useState('Default_Project')
  const [voices, setVoices] = useState([])
  const [characters, setCharacters] = useState([])
  const [emotionsGuide, setEmotionsGuide] = useState({})
  const [emotionCategories, setEmotionCategories] = useState([])
  const [stats, setStats] = useState(null)
  const [files, setFiles] = useState([])
  const [lastGenerated, setLastGenerated] = useState(null)
  const [isExportingZip, setIsExportingZip] = useState(false)

  // Background Job State
  const [activeJob, setActiveJob] = useState(null)
  const eventSourceRef = useRef(null)
  const pollIntervalRef = useRef(null)

  // Audio Player State
  const [currentPlayingUrl, setCurrentPlayingUrl] = useState(null)
  const [currentPlayingTitle, setCurrentPlayingTitle] = useState('')
  const [isPlaying, setIsPlaying] = useState(false)

  // Modals
  const [isNewProjectModalOpen, setIsNewProjectModalOpen] = useState(false)
  const [isRecordModalOpen, setIsRecordModalOpen] = useState(false)
  const [recordInitialChar, setRecordInitialChar] = useState('')
  const [recordInitialEmotion, setRecordInitialEmotion] = useState('neutral')
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [editingCharacter, setEditingCharacter] = useState(null)
  const [isPushingGit, setIsPushingGit] = useState(false)

  // Toast feedback
  const [toast, setToast] = useState(null)
  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 4500)
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
      if (emoData.categories) {
        setEmotionCategories(emoData.categories)
      }

      // 5. Dashboard Stats
      const statsRes = await fetch('/api/stats')
      const statsData = await statsRes.json()
      setStats(statsData)

      // 6. Check if any jobs are currently active in background
      checkActiveJobs()
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

  // Check if any jobs are already running in background
  const checkActiveJobs = async () => {
    try {
      const res = await fetch('/api/jobs/active')
      const data = await res.json()
      if (data.active_jobs && data.active_jobs.length > 0) {
        const runningJob = data.active_jobs[0]
        setActiveJob(runningJob)
        trackJobProgress(runningJob.id, runningJob.project)
      }
    } catch (e) {
      console.error('Failed to check active jobs:', e)
    }
  }

  useEffect(() => {
    fetchAllData()
    return () => {
      if (eventSourceRef.current) eventSourceRef.current.close()
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)
    }
  }, [])

  useEffect(() => {
    if (activeProject) {
      fetchProjectFiles(activeProject)
    }
  }, [activeProject])

  // Real-Time Job Progress Tracker (SSE with Polling Fallback)
  const trackJobProgress = (jobId, projectName) => {
    if (eventSourceRef.current) eventSourceRef.current.close()
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)

    const onJobFinished = (job) => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current)
        pollIntervalRef.current = null
      }

      if (job.status === 'completed' && job.result) {
        setLastGenerated(job.result)
        showToast(`🎉 ${job.step || 'Voiceover generated successfully!'}`, 'success')
        fetchProjectFiles(projectName || activeProject)
        // Refresh dashboard stats
        fetch('/api/stats')
          .then((r) => r.json())
          .then((s) => setStats(s))
          .catch(() => {})
      } else if (job.status === 'failed') {
        showToast(`❌ Synthesis failed: ${job.error || 'Unknown error'}`, 'error')
      }
    }

    try {
      const es = new EventSource(`/api/jobs/${jobId}/stream`)
      eventSourceRef.current = es

      es.onmessage = (event) => {
        try {
          const updatedJob = JSON.parse(event.data)
          setActiveJob(updatedJob)
          if (
            updatedJob.status === 'completed' ||
            updatedJob.status === 'failed' ||
            updatedJob.status === 'cancelled'
          ) {
            onJobFinished(updatedJob)
          }
        } catch (e) {
          console.error('Error parsing SSE data:', e)
        }
      }

      es.onerror = () => {
        // Fallback to polling every 450ms
        if (eventSourceRef.current) {
          eventSourceRef.current.close()
          eventSourceRef.current = null
        }
        if (!pollIntervalRef.current) {
          pollIntervalRef.current = setInterval(async () => {
            try {
              const res = await fetch(`/api/jobs/${jobId}`)
              if (res.ok) {
                const updated = await res.json()
                setActiveJob(updated)
                if (
                  updated.status === 'completed' ||
                  updated.status === 'failed' ||
                  updated.status === 'cancelled'
                ) {
                  onJobFinished(updated)
                }
              }
            } catch (err) {
              console.error('Polling error:', err)
            }
          }, 450)
        }
      }
    } catch (err) {
      console.error('SSE initialization failed, using polling fallback', err)
      pollIntervalRef.current = setInterval(async () => {
        try {
          const res = await fetch(`/api/jobs/${jobId}`)
          if (res.ok) {
            const updated = await res.json()
            setActiveJob(updated)
            if (
              updated.status === 'completed' ||
              updated.status === 'failed' ||
              updated.status === 'cancelled'
            ) {
              onJobFinished(updated)
            }
          }
        } catch (e) {}
      }, 500)
    }
  }

  // Audio Playback
  const handlePlayAudio = (url, title) => {
    if (currentPlayingUrl === url) {
      setIsPlaying(!isPlaying)
    } else {
      setCurrentPlayingUrl(url)
      setCurrentPlayingTitle(title)
      setIsPlaying(true)
    }
  }

  // Non-Blocking Background Audio Generation
  const handleGenerateAudio = async (payload) => {
    try {
      showToast('⚡ Enqueueing background synthesis...', 'info')
      const res = await fetch('/api/jobs/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Synthesis failed.')
      }

      const jobId = data.job_id
      setActiveJob(data.job)
      showToast('🎙️ Voiceover is rendering in the background!', 'success')
      trackJobProgress(jobId, payload.project_name)
    } catch (err) {
      showToast(err.message, 'error')
    }
  }

  const handleCancelJob = async (jobId) => {
    try {
      await fetch(`/api/jobs/${jobId}/cancel`, { method: 'POST' })
      setActiveJob((prev) =>
        prev ? { ...prev, status: 'cancelled', step: 'Cancelled by user', eta_seconds: 0 } : null
      )
      showToast('Background synthesis cancelled.', 'info')
    } catch (err) {
      console.error('Failed to cancel job:', err)
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

  const handleOpenEditCharacter = (charOrVoice) => {
    if (typeof charOrVoice === 'object' && charOrVoice !== null) {
      setEditingCharacter(charOrVoice)
      setIsEditModalOpen(true)
      return
    }
    if (typeof charOrVoice === 'string') {
      let extracted = ''
      const match = charOrVoice.match(/Custom:\s*([^(—[]+)/i)
      if (match && match[1]) {
        extracted = match[1].trim()
      }
      const found = characters.find(
        (c) =>
          c.name?.toLowerCase() === extracted.toLowerCase() ||
          c.id?.toLowerCase() === extracted.toLowerCase()
      )
      if (found) {
        setEditingCharacter(found)
      } else {
        setEditingCharacter({
          name: extracted || 'Custom Character',
          age: 30,
          age_group: 'adult',
          gender: 'male',
        })
      }
      setIsEditModalOpen(true)
    }
  }

  const handleDeleteCharacter = async (char) => {
    try {
      const res = await fetch(`/api/characters/${encodeURIComponent(char.name)}`, {
        method: 'DELETE',
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail)
      showToast(data.message, 'info')
      fetchAllData()
    } catch (err) {
      showToast('Failed to delete character: ' + err.message, 'error')
    }
  }

  const handleGitPush = async () => {
    setIsPushingGit(true)
    showToast('Syncing & pushing character voice models to GitHub...', 'info')
    try {
      const res = await fetch('/api/git/push', { method: 'POST' })
      const data = await res.json()
      if (data.success) {
        showToast(
          data.pushed ? data.message : `Saved locally (${data.commit}). Note: ${data.message}`,
          data.pushed ? 'success' : 'info'
        )
        fetchAllData()
      } else {
        showToast(data.message || 'Git sync encountered an issue', 'error')
      }
    } catch (err) {
      showToast('Failed to push to GitHub: ' + err.message, 'error')
    } finally {
      setIsPushingGit(false)
    }
  }

  const isJobRunning =
    activeJob && (activeJob.status === 'processing' || activeJob.status === 'queued')

  return (
    <div className="flex h-screen bg-[#070b14] text-slate-100 overflow-hidden font-sans">
      {/* Toast Notification */}
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-xl border text-xs font-semibold shadow-2xl flex items-center space-x-2 animate-in slide-in-from-top duration-200 ${
            toast.type === 'error'
              ? 'bg-rose-950/90 border-rose-500/50 text-rose-300'
              : toast.type === 'info'
              ? 'bg-slate-900/90 border-slate-700 text-slate-200'
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

        {/* Global Floating Background Job Progress Banner (Visible in All Tabs) */}
        {activeJob && (
          <div className="px-8 pt-4 pb-1">
            <JobProgressWidget
              job={activeJob}
              onCancelJob={handleCancelJob}
              onDismiss={() => setActiveJob(null)}
              onPlayResult={handlePlayAudio}
            />
          </div>
        )}

        {/* Dynamic Tab Body */}
        <main className="flex-1 overflow-y-auto p-8 pb-32">
          {currentTab === 'studio' && (
            <StudioView
              voices={voices}
              activeProject={activeProject}
              onGenerateAudio={handleGenerateAudio}
              isGenerating={isJobRunning}
              activeJob={activeJob}
              lastGenerated={lastGenerated}
              onPlayAudio={handlePlayAudio}
              currentPlayingUrl={currentPlayingUrl}
              isPlaying={isPlaying}
              onOpenVoiceCloner={() => handleOpenVoiceCloner()}
              onEditVoice={handleOpenEditCharacter}
              emotionsGuide={emotionsGuide}
              emotionCategories={emotionCategories}
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
              onEditCharacter={handleOpenEditCharacter}
              onDeleteCharacter={handleDeleteCharacter}
              onGitPush={handleGitPush}
              isPushingGit={isPushingGit}
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

      {/* Edit Character Profile Modal */}
      {isEditModalOpen && (
        <EditCharacterModal
          isOpen={isEditModalOpen}
          onClose={() => {
            setIsEditModalOpen(false)
            setEditingCharacter(null)
          }}
          character={editingCharacter}
          emotionsGuide={emotionsGuide}
          onSaveSuccess={() => {
            fetchAllData()
            showToast('Character profile saved and updated!')
          }}
          onDeleteSuccess={() => {
            fetchAllData()
            showToast('Character removed successfully.')
          }}
          showToast={showToast}
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
