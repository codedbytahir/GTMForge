'use client'

import { useEffect, useState } from 'react'

interface ResultsViewProps {
  taskId: string
  onReset: () => void
}

interface Asset {
  asset_id: string
  asset_type: 'image' | 'video' | 'deck'
  gcs_url: string
  quality_score: number
}

interface Manifest {
  manifest_id: string
  assets: Asset[]
  total_assets: number
  created_at: string
}

export default function ResultsView({ taskId, onReset }: ResultsViewProps) {
  const [manifest, setManifest] = useState<Manifest | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await fetch(`/api/results/${taskId}`)
        if (!response.ok) throw new Error('Failed to fetch results')

        const data = await response.json()
        console.log('Results data:', data) 
        if (data.manifest) {
          setManifest(data.manifest)
        }
      } catch (error) {
        console.error('Error fetching results:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchResults()
  }, [taskId])

  const downloadManifest = () => {
    if (!manifest) return

    const dataStr = JSON.stringify(manifest, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `manifest_${manifest.manifest_id}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto mt-8 text-center">
        <p className="text-slate-400">Loading results...</p>
      </div>
    )
  }

  if (!manifest) {
    return (
      <div className="max-w-4xl mx-auto mt-8 bg-slate-800 border border-slate-700 rounded-lg p-8 text-center">
        <p className="text-slate-300 mb-4">No results found</p>
        <button
          onClick={onReset}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg"
        >
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto mt-8">
      <div className="bg-slate-800 border border-slate-700 rounded-lg shadow-lg p-8">
        <h2 className="text-3xl font-bold text-white mb-2">Your Generated Assets</h2>
        <p className="text-slate-400 mb-8">Your complete pitch deck is ready! Below are all the generated assets.</p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {manifest.assets.map((asset) => {
            const typeEmoji = asset.asset_type === 'image' ? '🖼️' : asset.asset_type === 'video' ? '🎬' : '📊'

            return (
              <div key={asset.asset_id} className="bg-slate-900 border border-slate-700 rounded-lg overflow-hidden hover:border-indigo-500 transition-colors">
                <div className="h-48 bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center">
                  {asset.asset_type === 'image' ? (
                    <img src={asset.gcs_url} alt={asset.asset_id} className="w-full h-full object-cover" />
                  ) : asset.asset_type === 'video' ? (
                    <video src={asset.gcs_url} controls className="w-full h-full object-cover" />
                  ) : (
                    <div className="text-4xl">{typeEmoji}</div>
                  )}
                </div>

                <div className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="inline-block bg-indigo-600 text-white text-xs px-3 py-1 rounded">
                      {typeEmoji} {asset.asset_type}
                    </span>
                    <span className="text-sm text-slate-400">
                      Quality: {Math.round(asset.quality_score * 100)}%
                    </span>
                  </div>

                  <p className="text-xs text-slate-500 break-all mb-3">{asset.asset_id}</p>

                  <a
                    href={asset.gcs_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block text-sm text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    View on GCS →
                  </a>
                </div>
              </div>
            )
          })}
        </div>
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-6 mb-8">
          <h3 className="text-lg font-semibold text-white mb-4">📋 Manifest Information</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-slate-400">Manifest ID</p>
              <p className="text-white font-mono text-xs">{manifest.manifest_id}</p>
            </div>
            <div>
              <p className="text-slate-400">Total Assets</p>
              <p className="text-white text-lg font-semibold">{manifest.total_assets}</p>
            </div>
            <div>
              <p className="text-slate-400">Created</p>
              <p className="text-white">{new Date(manifest.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        </div>
        <div className="flex gap-4 justify-center">
          <button
            onClick={downloadManifest}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
          >
            📥 Download Manifest.json
          </button>
          <button
            onClick={onReset}
            className="bg-slate-700 hover:bg-slate-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
          >
            🔄 Generate Another Deck
          </button>
        </div>
      </div>
    </div>
  )
}
