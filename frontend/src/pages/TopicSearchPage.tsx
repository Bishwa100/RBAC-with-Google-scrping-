import React, { useState } from 'react'
import { Share2 } from 'lucide-react'
import { topiclensAPI, TopicSearchRequest, JobStatus } from '@/api'
import ShareModal from '@/components/shared/ShareModal'
import { useAuthStore } from '@/store/authStore'

interface SearchResult {
  id: number
  job_id: string
  source: string
  url: string
  title: string | null
  content: string | null
  summary: string | null
}

export default function TopicSearchPage() {
  const [topic, setTopic] = useState('')
  const [selectedSources, setSelectedSources] = useState<string[]>([])
  const [deepAnalysis, setDeepAnalysis] = useState(false)
  const [loading, setLoading] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [shareModalOpen, setShareModalOpen] = useState(false)
  const [selectedResult, setSelectedResult] = useState<SearchResult | null>(null)
  const { user } = useAuthStore()

  const availableSources = [
    'youtube', 'github', 'reddit', 'twitter', 'blogs',
    'linkedin', 'facebook', 'instagram', 'quora', 'events'
  ]

  // Check if user is root
  const isRootUser = user?.roles.some(
    role => role.name.toLowerCase() === 'root' || 
            role.name.toLowerCase() === 'admin' || 
            role.level === 0
  )

  const handleSourceToggle = (source: string) => {
    setSelectedSources(prev =>
      prev.includes(source)
        ? prev.filter(s => s !== source)
        : [...prev, source]
    )
  }

  const handleShare = (result: SearchResult) => {
    setSelectedResult(result)
    setShareModalOpen(true)
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
      const request: TopicSearchRequest = {
        topic: topic.trim(),
        sources: selectedSources,
        deep_analysis: deepAnalysis,
      }

      const response = await topiclensAPI.search(request)
      setJobId(response.data.job_id)
      
      // Start polling for job status
      pollJobStatus(response.data.job_id)
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to start search')
      setLoading(false)
    }
  }

  const pollJobStatus = async (id: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await topiclensAPI.getJobStatus(id)
        const status = response.data
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

  // Parse results from job status
  const results: SearchResult[] = jobStatus?.result?.results || []

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Share Modal */}
      {selectedResult && (
        <ShareModal
          isOpen={shareModalOpen}
          onClose={() => {
            setShareModalOpen(false)
            setSelectedResult(null)
          }}
          resultId={selectedResult.id}
          jobId={selectedResult.job_id}
          resultTitle={selectedResult.title || selectedResult.url}
          onShareSuccess={() => {
            // Optional: Show success notification
          }}
        />
      )}
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-text font-syne">Topic Search & Analysis</h1>

        {/* Search Form */}
        <div className="bg-bg-surface rounded-lg border border-border p-6 mb-6">
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-muted">
              Topic or Keyword
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Artificial Intelligence, Climate Change..."
              className="w-full px-4 py-2 bg-bg-surface2 border border-border rounded-lg focus:ring-2 focus:ring-accent focus:border-accent text-text placeholder-dim"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-muted">
              Select Sources
            </label>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
              {availableSources.map((source) => (
                <button
                  key={source}
                  onClick={() => handleSourceToggle(source)}
                  className={`px-3 py-2 rounded-lg border text-sm font-medium transition ${
                    selectedSources.includes(source)
                      ? 'bg-accent text-white border-accent'
                      : 'bg-bg-surface2 text-muted border-border hover:border-accent hover:text-text'
                  }`}
                >
                  {source}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <label className="flex items-center gap-2 text-muted">
              <input
                type="checkbox"
                checked={deepAnalysis}
                onChange={(e) => setDeepAnalysis(e.target.checked)}
                className="w-4 h-4 rounded border-border bg-bg-surface2"
              />
              <span className="text-sm font-medium">
                Enable Deep Analysis (uses local LLM for detailed insights)
              </span>
            </label>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-danger/20 border border-danger text-danger rounded">
              {error}
            </div>
          )}

          <button
            onClick={handleSearch}
            disabled={loading}
            className="w-full bg-accent text-white py-3 rounded-lg font-medium font-syne hover:bg-accent/80 disabled:bg-dim disabled:cursor-not-allowed transition"
          >
            {loading ? 'Searching...' : 'Start Search'}
          </button>
        </div>

        {/* Job Status */}
        {jobId && (
          <div className="bg-bg-surface rounded-lg border border-border p-6">
            <h2 className="text-xl font-bold mb-4 text-text font-syne">Search Status</h2>
            
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-muted">Job ID:</span>
                <span className="text-sm text-muted font-mono">{jobId}</span>
              </div>
              
              {jobStatus && (
                <>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-muted">Status:</span>
                    <span
                      className={`text-sm font-medium px-3 py-1 rounded-full ${
                        jobStatus.status === 'completed'
                          ? 'bg-success/20 text-success'
                          : jobStatus.status === 'failed'
                          ? 'bg-danger/20 text-danger'
                          : 'bg-warning/20 text-warning'
                      }`}
                    >
                      {jobStatus.status}
                    </span>
                  </div>

                  {jobStatus.status === 'completed' && results.length > 0 && (
                    <div className="mt-4">
                      <h3 className="font-medium mb-4 text-text">Results ({results.length}):</h3>
                      <div className="space-y-4">
                        {results.map((result) => (
                          <div key={result.id} className="bg-bg-surface2 p-4 rounded-lg border border-border">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="px-2 py-1 bg-accent/20 text-accent text-xs rounded-full font-medium">
                                    {result.source}
                                  </span>
                                </div>
                                <h4 className="font-medium text-text mb-1">
                                  {result.title || 'Untitled'}
                                </h4>
                                <a 
                                  href={result.url} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="text-sm text-accent hover:underline break-all"
                                >
                                  {result.url}
                                </a>
                                {result.summary && (
                                  <p className="mt-2 text-sm text-muted line-clamp-2">
                                    {result.summary}
                                  </p>
                                )}
                              </div>
                              
                              {isRootUser && (
                                <button
                                  onClick={() => handleShare(result)}
                                  className="ml-4 flex items-center gap-2 px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent/80 transition"
                                >
                                  <Share2 className="w-4 h-4" />
                                  Share
                                </button>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {jobStatus.status === 'completed' && jobStatus.result && results.length === 0 && (
                    <div className="mt-4 p-4 bg-warning/20 border border-warning text-warning rounded">
                      No results found for this search.
                    </div>
                  )}

                  {jobStatus.status === 'failed' && (
                    <div className="mt-4 p-3 bg-danger/20 border border-danger text-danger rounded">
                      Search failed. Please try again.
                    </div>
                  )}
                </>
              )}
            </div>

            {loading && (
              <div className="flex items-center justify-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
