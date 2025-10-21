'use client'

import { useEffect, useState } from 'react'

interface ProgressViewProps {
  taskId: string
  onComplete: () => void
  onError: (error: string) => void
}

interface ProgressUpdate {
  type: string
  stage: string
  progress: number
  message: string
}

const STAGE_LABELS: Record<string, string> = {
  'initialization': 'Initializing',
  'ideation': 'Ideation',
  'comparative_insight': 'Comparative Insight',
  'pitch_writing': 'Pitch Writing',
  'prompt_forge': 'Prompt Forge',
  'media_generation': 'Media Generation',
  'qa_validation': 'QA Validation',
  'publishing': 'Publishing',
  'completed': 'Completed!'
}

export default function ProgressView({ taskId, onComplete, onError }: ProgressViewProps) {
  const [progress, setProgress] = useState(0)
  const [stage, setStage] = useState('initialization')
  const [message, setMessage] = useState('Starting pipeline...')
  const [logs, setLogs] = useState<string[]>(['Pipeline started...'])

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//localhost:8000/ws/progress/${taskId}`

    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('WebSocket connected')
      addLog('Connected to stream')
    }

    ws.onmessage = (event) => {
      try {
        const data: ProgressUpdate = JSON.parse(event.data)

        if (data.type === 'progress' || data.type === 'status') {
          setProgress(data.progress || 0)
          setStage(data.stage || 'unknown')
          setMessage(data.message || 'Processing...')
          addLog(`${STAGE_LABELS[data.stage] || data.stage}: ${Math.round(data.progress || 0)}%`)
        } else if (data.type === 'final') {
          setProgress(100)
          setStage('completed')
          setMessage('Your pitch deck has been successfully generated!')
          addLog('Pipeline complete!')
          setTimeout(onComplete, 1500)
        } else if (data.type === 'error') {
          onError(data.message || 'An error occurred')
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      onError('Connection error. Please refresh and try again.')
    }

    return () => {
      ws.close()
    }
  }, [taskId, onComplete, onError])

  const addLog = (message: string) => {
    const time = new Date().toLocaleTimeString()
    setLogs(prev => [...prev, `[${time}] ${message}`])
  }

  return (
    <div className="max-w-4xl mx-auto mt-8 space-y-6">
      <div className="bg-slate-800 border border-slate-700 rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-bold text-white mb-6">Generating Your Pitch Deck</h2>
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-slate-300 font-medium">Progress</span>
            <span className="text-indigo-400 font-bold text-lg">{Math.round(progress)}%</span>
          </div>
          <div className="relative w-full h-4 bg-slate-900 rounded-full overflow-hidden border border-slate-600">
            <div
              className="h-full bg-gradient-to-r from-green-500 to-blue-500 transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
        <div className="bg-slate-900 border-l-4 border-indigo-500 rounded p-4 mb-6">
          <p className="text-sm text-slate-400 mb-1">Current Stage</p>
          <p className="text-xl font-semibold text-indigo-400 mb-2">{STAGE_LABELS[stage] || stage}</p>
          <p className="text-slate-300">{message}</p>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-slate-300 mb-3">Live Log</h3>
          <div className="bg-slate-900 border border-slate-700 rounded p-4 max-h-48 overflow-y-auto space-y-1">
            {logs.map((log, idx) => (
              <p key={idx} className="text-xs text-slate-400 font-mono">
                {log}
              </p>
            ))}
          </div>
        </div>
      </div>
      <div className="text-center text-slate-400 text-sm">
        <p>⏱️ Typical generation time: 2-3 minutes</p>
      </div>
    </div>
  )
}
