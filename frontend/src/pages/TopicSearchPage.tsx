import React, { useState } from 'react'
import { Share2, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react'
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
  rank?: number
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

  // Parse results from job status - the result contains { results: { youtube: [...], github: [...], ... } }
  const parseResults = (): SearchResult[] => {
    if (!jobStatus?.result?.results) return []
    
    const allResults: SearchResult[] = []
    const resultData = jobStatus.result.results
    
    // Iterate through each source (youtube, github, etc.)
    // Skip 'top_10_overall' as it's a duplicate aggregation of other sources
    Object.entries(resultData).forEach(([source, items]) => {
      if (source === 'top_10_overall' || source === 'Top_10_overall') return
      
      if (Array.isArray(items)) {
        items.forEach((item: any, index: number) => {
          allResults.push({
            id: item.id || index + 1,
            job_id: jobId || '',
            source: source,
            url: item.url || item.link || '',
            title: item.title || item.name || null,
            content: item.content || item.description || null,
            summary: item.summary || item.snippet || null,
            rank: item.rank || index + 1
          })
        })
      }
    })
    
    // Sort by rank if available
    return allResults.sort((a, b) => (a.rank || 999) - (b.rank || 999))
  }
  
  const results = parseResults()

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

                  {/* Progress Bar */}
                  {(jobStatus.status === 'pending' || jobStatus.status === 'running') && (
                    <div className="mt-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-muted">Progress:</span>
                        <span className="text-sm font-bold text-accent">{jobStatus.progress || 0}%</span>
                      </div>
                      <div className="w-full bg-bg-surface2 rounded-full h-3 overflow-hidden">
                        <div 
                          className="bg-gradient-to-r from-accent to-accent2 h-3 rounded-full transition-all duration-500 ease-out"
                          style={{ width: `${jobStatus.progress || 0}%` }}
                        />
                      </div>
                      <p className="text-xs text-dim mt-2">
                        {jobStatus.progress === 0 
                          ? 'Starting search...' 
                          : jobStatus.progress < 50 
                          ? 'Scraping sources...' 
                          : jobStatus.progress < 90 
                          ? 'Processing results...' 
                          : 'Finalizing...'}
                      </p>
                    </div>
                  )}

                  {/* Insights Section */}
                  {jobStatus.status === 'completed' && jobStatus.result?.insights && (
                    <div className="mt-4 p-4 bg-accent/10 border border-accent/30 rounded-lg">
                      <h3 className="font-bold text-text mb-2 font-syne">AI Insights</h3>
                      {jobStatus.result.insights.summary && (
                        <p className="text-sm text-muted mb-2">{jobStatus.result.insights.summary}</p>
                      )}
                      {jobStatus.result.insights.trends && jobStatus.result.insights.trends.length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs font-medium text-accent mb-1">Trends:</p>
                          <ul className="text-xs text-muted list-disc list-inside">
                            {jobStatus.result.insights.trends.slice(0, 3).map((trend: string, i: number) => (
                              <li key={i}>{trend}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Results Section */}
                  {jobStatus.status === 'completed' && results.length > 0 && (
                    <div className="mt-6">
                      <h3 className="font-bold mb-4 text-text font-syne">Results ({results.length})</h3>
                      <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                        {results.map((result, idx) => (
                          <div key={`${result.source}-${idx}`} className="bg-bg-surface2 p-4 rounded-lg border border-border hover:border-accent/50 transition">
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-2 flex-wrap">
                                  <span className="px-2 py-1 bg-accent/20 text-accent text-xs rounded-full font-medium capitalize">
                                    {result.source}
                                  </span>
                                  {result.rank && (
                                    <span className="px-2 py-1 bg-success/20 text-success text-xs rounded-full font-medium">
                                      #{result.rank}
                                    </span>
                                  )}
                                </div>
                                <h4 className="font-medium text-text mb-1 line-clamp-2">
                                  {result.title || 'Untitled'}
                                </h4>
                                <a 
                                  href={result.url} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-1 text-sm text-accent hover:underline break-all"
                                >
                                  <ExternalLink className="w-3 h-3 flex-shrink-0" />
                                  <span className="truncate">{result.url}</span>
                                </a>
                                {(result.summary || result.content) && (
                                  <p className="mt-2 text-sm text-muted line-clamp-3">
                                    {result.summary || result.content}
                                  </p>
                                )}
                              </div>
                              
                              {isRootUser && (
                                <button
                                  onClick={() => handleShare(result)}
                                  className="flex-shrink-0 flex items-center gap-2 px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent/80 transition"
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

                  {/* No results but data exists */}
                  {jobStatus.status === 'completed' && jobStatus.result && results.length === 0 && (
                    <div className="mt-4">
                      <div className="p-4 bg-warning/20 border border-warning text-warning rounded mb-4">
                        No parseable results found. Raw data may be available.
                      </div>
                      {/* Show raw counts if available */}
                      {jobStatus.result.counts && (
                        <div className="p-4 bg-bg-surface2 rounded-lg border border-border">
                          <h4 className="font-medium text-text mb-2">Data Summary:</h4>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                            {Object.entries(jobStatus.result.counts).map(([source, count]) => (
                              <div key={source} className="text-sm">
                                <span className="text-muted capitalize">{source}:</span>{' '}
                                <span className="text-text font-medium">{String(count)}</span>
                              </div>
                            ))}
                          </div>
                          <p className="text-xs text-dim mt-2">Total: {jobStatus.result.total_results || 0} items</p>
                        </div>
                      )}
                    </div>
                  )}

                  {jobStatus.status === 'failed' && (
                    <div className="mt-4 p-3 bg-danger/20 border border-danger text-danger rounded">
                      Search failed: {jobStatus.error_message || 'Unknown error. Please try again.'}
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
