import React from 'react'
import {
  Sparkles,
  Clock,
  CheckCircle2,
  AlertCircle,
  Play,
  Download,
  X,
  Cpu,
  Layers,
  ChevronDown,
  ChevronUp
} from 'lucide-react'

export default function JobProgressWidget({
  job,
  onCancelJob,
  onDismiss,
  onPlayResult,
}) {
  const [isMinimized, setIsMinimized] = React.useState(false)

  if (!job) return null

  const isCompleted = job.status === 'completed'
  const isFailed = job.status === 'failed'
  const isProcessing = job.status === 'processing' || job.status === 'queued'

  return (
    <div className="rounded-2xl bg-[#0d1322]/95 border border-sky-500/30 p-5 shadow-2xl backdrop-blur-xl animate-in slide-in-from-top-2 duration-200">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="relative">
            {isProcessing && (
              <div className="w-9 h-9 rounded-xl bg-sky-500/20 border border-sky-500/30 flex items-center justify-center text-sky-400">
                <div className="w-4 h-4 border-2 border-sky-400 border-t-transparent rounded-full animate-spin" />
              </div>
            )}
            {isCompleted && (
              <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <CheckCircle2 className="w-5 h-5" />
              </div>
            )}
            {isFailed && (
              <div className="w-9 h-9 rounded-xl bg-rose-500/20 border border-rose-500/30 flex items-center justify-center text-rose-400">
                <AlertCircle className="w-5 h-5" />
              </div>
            )}
          </div>

          <div>
            <div className="flex items-center space-x-2">
              <h4 className="text-sm font-bold text-white tracking-tight">
                {isCompleted
                  ? 'Voiceover Ready'
                  : isFailed
                  ? 'Synthesis Failed'
                  : 'Synthesizing in Background'}
              </h4>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                {job.project}
              </span>
            </div>
            <p className="text-xs text-slate-400 truncate max-w-md">
              {job.step || 'Processing...'}
            </p>
          </div>
        </div>

        {/* Right Badges & Controls */}
        <div className="flex items-center space-x-3">
          {isProcessing && (
            <div className="flex items-center space-x-2">
              {/* ETA Badge */}
              <div className="flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-mono font-semibold">
                <Clock className="w-3.5 h-3.5" />
                <span>
                  {job.eta_seconds > 0 ? `ETA: ~${job.eta_seconds}s` : 'Finalizing...'}
                </span>
              </div>

              {/* Progress Percentage */}
              <span className="text-xs font-mono font-bold text-white px-2 py-1 rounded-lg bg-slate-800 border border-slate-700">
                {job.progress}%
              </span>
            </div>
          )}

          {isCompleted && (
            <div className="flex items-center space-x-2">
              {job.result && (
                <button
                  onClick={() => onPlayResult(job.result.audio_url, job.result.filename)}
                  className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-white text-xs font-semibold shadow-md shadow-sky-500/20 transition-all"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Play Track</span>
                </button>
              )}
              {job.result && (
                <a
                  href={job.result.audio_url}
                  download={job.result.filename}
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                  title="Download MP3"
                >
                  <Download className="w-4 h-4" />
                </a>
              )}
            </div>
          )}

          {/* Dismiss button */}
          {(isCompleted || isFailed) && onDismiss && (
            <button
              onClick={onDismiss}
              className="p-1 text-slate-500 hover:text-slate-300 rounded-lg"
            >
              <X className="w-4 h-4" />
            </button>
          )}

          {isProcessing && onCancelJob && (
            <button
              onClick={() => onCancelJob(job.id)}
              className="text-[11px] text-rose-400 hover:text-rose-300 font-semibold px-2 py-1 rounded hover:bg-rose-500/10 transition-colors"
            >
              Cancel
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar (Visible when processing) */}
      {isProcessing && (
        <div className="mt-4 space-y-1.5">
          <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden relative">
            <div
              className="h-full bg-gradient-to-r from-sky-500 via-indigo-500 to-sky-400 rounded-full transition-all duration-300 ease-out relative"
              style={{ width: `${Math.max(5, job.progress)}%` }}
            >
              <div className="absolute inset-0 bg-white/20 animate-pulse" />
            </div>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
            <span>
              {job.current_sentence > 0 && job.total_sentences > 0
                ? `Sentence ${job.current_sentence} of ${job.total_sentences}`
                : 'Devanagari Normalization & Timbre Matching'}
            </span>
            <span>Elapsed: {job.elapsed_seconds || 0}s</span>
          </div>
        </div>
      )}
    </div>
  )
}

