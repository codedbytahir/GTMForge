'use client'

import { useState } from 'react'

interface IdeaFormProps {
  onStartGeneration: (taskId: string) => void
  onComplete: (result: any) => void
  onError: (error: string) => void
}

export default function IdeaForm({ onStartGeneration, onComplete, onError }: IdeaFormProps) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!input.trim()) {
      onError('Please enter a startup idea')
      return
    }

    setLoading(true)
    try {
      const parts = input.split(' in ')
      const idea = parts[0].trim()
      const industry = parts.length > 1 ? parts[1].trim() : 'Technology'

      const response = await fetch('/api/generate_idea', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea, industry })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to start pipeline')
      }

      const data = await response.json()
      const taskId = data.task_id
      
      await new Promise(resolve => setTimeout(resolve, 100)) 
      
      const statusResponse = await fetch(`/api/status/${taskId}`)
      if (!statusResponse.ok) {
        throw new Error('Failed to check task status')
      }
      
      const statusData = await statusResponse.json()
      
      if (statusData.status === 'completed') {
        const resultsResponse = await fetch(`/api/results/${taskId}`)
        if (resultsResponse.ok) {
          const results = await resultsResponse.json()
          onComplete(results)
        } else {
          throw new Error('Failed to fetch results')
        }
      } else {
        onStartGeneration(taskId)
      }
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Failed to start pipeline')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto mt-8">
      <div className="bg-slate-800 border border-slate-700 rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-bold text-white mb-2">Describe Your Startup Idea</h2>
        <p className="text-slate-400 mb-6">Tell us about your startup and we'll generate a complete pitch deck with images, videos, and slides.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Example: 'AI for restaurant staffing in the hospitality industry' or 'SaaS for remote design teams in software'"
            className="w-full h-32 px-4 py-3 bg-slate-900 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 resize-none"
            disabled={loading}
          />

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-105 disabled:hover:scale-100"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Generating Pitch Deck...
              </span>
            ) : (
              'Generate Pitch Deck'
            )}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">Example Ideas:</h3>
          <ul className="space-y-2 text-sm text-slate-400">
            <li>• AI for restaurant staffing in the hospitality industry</li>
            <li>• SaaS for remote design teams in software</li>
            <li>• Blockchain supply chain tracking in logistics</li>
            <li>• Machine learning for medical diagnosis in healthcare</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
