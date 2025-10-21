'use client'

interface ErrorViewProps {
  error: string | null
  onReset: () => void
}

export default function ErrorView({ error, onReset }: ErrorViewProps) {
  return (
    <div className="max-w-2xl mx-auto mt-8">
      <div className="bg-slate-800 border-l-4 border-red-500 rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-bold text-red-400 mb-2">❌ Error Occurred</h2>
        <p className="text-slate-300 mb-6 break-words">{error || 'An unexpected error occurred'}</p>

        <button
          onClick={onReset}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
        >
          🔄 Try Again
        </button>

        <div className="mt-6 pt-6 border-t border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">Troubleshooting:</h3>
          <ul className="space-y-2 text-sm text-slate-400">
            <li>✓ Ensure the FastAPI backend is running</li>
            <li>✓ Check your internet connection</li>
            <li>✓ Verify GCP credentials are set</li>
            <li>✓ Check browser console for more details (F12)</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
