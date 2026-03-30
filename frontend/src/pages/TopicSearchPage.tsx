import React, { useState } from 'react'
import { topiclensAPI, SearchRequest, JobStatus } from '@/api'

export default function TopicSearchPage() {
  const [topic, setTopic] = useState('')
  const [selectedSources, setSelectedSources] = useState<string[]>([])
  const [deepAnalysis, setDeepAnalysis] = useState(false)
  const [loading, setLoading] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null)
  const [error, setError] = useState<string | null>(null)

  const availableSources = [
    'youtube', 'github', 'reddit', 'twitter', 'blogs',
    'linkedin', 'facebook', 'instagram', 'quora', 'events'
  ]

  const handleSourceToggle = (source: string) => {
    setSelectedSources(prev =>
      prev.includes(source)
        ? prev.filter(s => s !== source)
        : [...prev, source]
    )
  }

  const handleSearch = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic')
      return
    }

    if (selectedSources.length === 0) {
      setError('Please select at least one source')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const request: SearchRequest = {
        topic: topic.trim(),
        sources: selectedSources,
        deep_analysis: deepAnalysis,
      }

      const response = await topiclensAPI.search(request)
      setJobId(response.job_id)
      
      // Start polling for job status
      pollJobStatus(response.job_id)
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to start search')
      setLoading(false)
    }
  }

  const pollJobStatus = async (id: string) => {
    const interval = setInterval(async () => {
      try {
        const status = await topiclensAPI.getJobStatus(id)
        setJobStatus(status)

        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(interval)
          setLoading(false)
        }
      } catch (err: any) {
        console.error('Error polling status:', err)
        clearInterval(interval)
        setLoading(false)
      }
    }, 2000) // Poll every 2 seconds
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Topic Search & Analysis</h1>

        {/* Search Form */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">
              Topic or Keyword
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Artificial Intelligence, Climate Change..."
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">
              Select Sources
            </label>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
              {availableSources.map((source) => (
                <button
                  key={source}
                  onClick={() => handleSourceToggle(source)}
                  className={`px-3 py-2 rounded-lg border text-sm font-medium transition ${
                    selectedSources.includes(source)
                      ? 'bg-blue-500 text-white border-blue-500'
                      : 'bg-white text-gray-700 border-gray-300 hover:border-blue-500'
                  }`}
                >
                  {source}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={deepAnalysis}
                onChange={(e) => setDeepAnalysis(e.target.checked)}
                className="w-4 h-4"
              />
              <span className="text-sm font-medium">
                Enable Deep Analysis (uses local LLM for detailed insights)
              </span>
            </label>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-300 text-red-700 rounded">
              {error}
            </div>
          )}

          <button
            onClick={handleSearch}
            disabled={loading}
            className="w-full bg-blue-500 text-white py-3 rounded-lg font-medium hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
            {loading ? 'Searching...' : 'Start Search'}
          </button>
        </div>

        {/* Job Status */}
        {jobId && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold mb-4">Search Status</h2>
            
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Job ID:</span>
                <span className="text-sm text-gray-600 font-mono">{jobId}</span>
              </div>
              
              {jobStatus && (
                <>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Status:</span>
                    <span
                      className={`text-sm font-medium px-3 py-1 rounded-full ${
                        jobStatus.status === 'completed'
                          ? 'bg-green-100 text-green-700'
                          : jobStatus.status === 'failed'
                          ? 'bg-red-100 text-red-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }`}
                    >
                      {jobStatus.status}
                    </span>
                  </div>

                  {jobStatus.status === 'completed' && jobStatus.result && (
                    <div className="mt-4">
                      <h3 className="font-medium mb-2">Results:</h3>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <pre className="text-sm overflow-auto max-h-96">
                          {JSON.stringify(jobStatus.result, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}

                  {jobStatus.status === 'failed' && (
                    <div className="mt-4 p-3 bg-red-100 border border-red-300 text-red-700 rounded">
                      Search failed. Please try again.
                    </div>
                  )}
                </>
              )}
            </div>

            {loading && (
              <div className="flex items-center justify-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
