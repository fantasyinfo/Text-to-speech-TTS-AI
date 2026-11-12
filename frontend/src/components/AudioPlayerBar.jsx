import React, { useRef, useState, useEffect } from 'react'
import {
  Play,
  Pause,
  Volume2,
  VolumeX,
  Download,
  X,
  FastForward
} from 'lucide-react'

export default function AudioPlayerBar({
  audioUrl,
  trackTitle,
  isPlaying,
  setIsPlaying,
  onClose,
}) {
  const audioRef = useRef(null)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [playbackRate, setPlaybackRate] = useState(1.0)
  const [isMuted, setIsMuted] = useState(false)

  useEffect(() => {
    if (audioRef.current && audioUrl) {
      audioRef.current.src = audioUrl
      audioRef.current.playbackRate = playbackRate
      audioRef.current.play().then(() => setIsPlaying(true)).catch(() => setIsPlaying(false))
    }
  }, [audioUrl])

  useEffect(() => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.play().catch(() => {})
      } else {
        audioRef.current.pause()
      }
    }
  }, [isPlaying])

  const togglePlay = () => {
    setIsPlaying(!isPlaying)
  }

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime)
      setDuration(audioRef.current.duration || 0)
    }
  }

  const handleSeek = (e) => {
    const time = parseFloat(e.target.value)
    setCurrentTime(time)
    if (audioRef.current) {
      audioRef.current.currentTime = time
    }
  }

  const cycleSpeed = () => {
    const rates = [1.0, 1.25, 1.5, 2.0]
    const next = rates[(rates.indexOf(playbackRate) + 1) % rates.length]
    setPlaybackRate(next)
    if (audioRef.current) {
      audioRef.current.playbackRate = next
    }
  }

  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted
      setIsMuted(!isMuted)
    }
  }

  const formatTime = (sec) => {
    if (!sec || isNaN(sec)) return '0:00'
    const m = Math.floor(sec / 60)
    const s = Math.floor(sec % 60)
    return `${m}:${s < 10 ? '0' : ''}${s}`
  }

  if (!audioUrl) return null

  return (
    <div className="fixed bottom-0 inset-x-0 h-20 bg-[#0d1322]/95 backdrop-blur-xl border-t border-slate-800 px-6 flex items-center justify-between z-40 shadow-2xl animate-in slide-in-from-bottom duration-200">
      <audio
        ref={audioRef}
        onTimeUpdate={handleTimeUpdate}
        onEnded={() => setIsPlaying(false)}
      />

      {/* Left: Track Information */}
      <div className="flex items-center space-x-3 min-w-0 max-w-[280px]">
        <div className="w-10 h-10 rounded-xl bg-sky-500/20 text-sky-400 flex items-center justify-center flex-shrink-0">
          <Volume2 className="w-5 h-5" />
        </div>
        <div className="min-w-0">
          <p className="text-xs font-semibold text-white truncate" title={trackTitle}>
            {trackTitle}
          </p>
          <p className="text-[11px] text-slate-400 font-mono">192kbps MP3</p>
        </div>
      </div>

      {/* Center: Controls & Scrubber */}
      <div className="flex flex-col items-center space-y-1.5 flex-1 max-w-xl px-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={togglePlay}
            className="w-9 h-9 rounded-full bg-sky-500 hover:bg-sky-400 text-white flex items-center justify-center shadow-md shadow-sky-500/20 transition-all"
          >
            {isPlaying ? (
              <Pause className="w-4 h-4 fill-current" />
            ) : (
              <Play className="w-4 h-4 fill-current ml-0.5" />
            )}
          </button>
        </div>

        <div className="w-full flex items-center space-x-2.5 text-[11px] font-mono text-slate-400">
          <span className="w-9 text-right">{formatTime(currentTime)}</span>
          <input
            type="range"
            min={0}
            max={duration || 100}
            value={currentTime}
            onChange={handleSeek}
            className="flex-1 accent-sky-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
          />
          <span className="w-9">{formatTime(duration)}</span>
        </div>
      </div>

      {/* Right: Speed, Mute, Download & Close */}
      <div className="flex items-center space-x-3">
        <button
          onClick={cycleSpeed}
          className="px-2 py-1 rounded-lg bg-slate-800 text-slate-300 hover:text-white text-xs font-mono font-semibold"
          title="Playback Speed"
        >
          {playbackRate}x
        </button>

        <button
          onClick={toggleMute}
          className="p-2 text-slate-400 hover:text-white rounded-lg transition-colors"
        >
          {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
        </button>

        <a
          href={audioUrl}
          download={trackTitle}
          className="p-2 text-slate-400 hover:text-white rounded-lg transition-colors"
          title="Download MP3"
        >
          <Download className="w-4 h-4" />
        </a>

        <button
          onClick={onClose}
          className="p-2 text-slate-500 hover:text-white rounded-lg transition-colors"
          title="Dismiss Player"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

