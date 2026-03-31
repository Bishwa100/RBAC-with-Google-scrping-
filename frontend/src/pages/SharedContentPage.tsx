import React, { useState, useEffect } from 'react'
import { Inbox, RefreshCw } from 'lucide-react'
import { topiclensAPI } from '@/api'
import ContentViewer from '@/components/shared/ContentViewer'
import { SharedContentItem } from '@/types'
import { useAuthStore } from '@/store/authStore'

export default function SharedContentPage() {
  const [items, setItems] = useState<SharedContentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user } = useAuthStore()

  useEffect(() => {
    fetchSharedContent()
  }, [])

  const fetchSharedContent = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await topiclensAPI.getMySharedContent()
      
      if (response.success && response.data) {
        setItems(response.data.items || [])
      } else {
        setError(response.detail || 'Failed to load shared content')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load shared content')
      console.error('Error fetching shared content:', err)
    } finally {
      setLoading(false)
    }
  }

  // Group items by topic for better organization
  const groupedItems = items.reduce((acc, item) => {
    const topic = item.topic
    if (!acc[topic]) {
      acc[topic] = []
    }
    acc[topic].push(item)
    return acc
  }, {} as Record<string, SharedContentItem[]>)

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold font-syne text-text">Shared Content</h1>
            <p className="text-muted mt-2">
              Content shared with you by administrators
            </p>
          </div>
          <button
            onClick={fetchSharedContent}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent/80 disabled:bg-dim transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* User's Roles */}
        {user && (
          <div className="mb-6 p-4 bg-bg-surface rounded-lg border border-border">
            <p className="text-sm text-muted">
              <span className="font-medium text-text">Your Roles:</span>{' '}
              {user.roles.map(r => r.name).join(', ') || 'No roles assigned'}
            </p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mb-4"></div>
            <p className="text-muted">Loading shared content...</p>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="p-6 bg-danger/10 border border-danger rounded-lg text-center">
            <p className="text-danger mb-4">{error}</p>
            <button
              onClick={fetchSharedContent}
              className="px-4 py-2 bg-danger text-white rounded-lg hover:bg-danger/80 transition"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && items.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 bg-bg-surface rounded-lg border border-border">
            <Inbox className="w-16 h-16 text-dim mb-4" />
            <h3 className="text-xl font-medium text-text mb-2">No Shared Content</h3>
            <p className="text-muted text-center max-w-md">
              No content has been shared with your roles yet. 
              Check back later or contact an administrator.
            </p>
          </div>
        )}

        {/* Content Display */}
        {!loading && !error && items.length > 0 && (
          <div className="space-y-8">
            {/* Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-bg-surface p-4 rounded-lg border border-border">
                <p className="text-sm text-muted">Total Items</p>
                <p className="text-2xl font-bold font-syne text-text">{items.length}</p>
              </div>
              <div className="bg-bg-surface p-4 rounded-lg border border-border">
                <p className="text-sm text-muted">Topics</p>
                <p className="text-2xl font-bold font-syne text-text">{Object.keys(groupedItems).length}</p>
              </div>
              <div className="bg-bg-surface p-4 rounded-lg border border-border">
                <p className="text-sm text-muted">Sources</p>
                <p className="text-2xl font-bold font-syne text-text">
                  {new Set(items.map(i => i.source)).size}
                </p>
              </div>
            </div>

            {/* Grouped Content */}
            {Object.entries(groupedItems).map(([topic, topicItems]) => (
              <div key={topic} className="space-y-4">
                <h2 className="text-xl font-bold font-syne text-text border-b border-border pb-2">
                  {topic}
                  <span className="ml-2 text-sm font-normal text-muted">
                    ({topicItems.length} item{topicItems.length !== 1 ? 's' : ''})
                  </span>
                </h2>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {topicItems.map((item) => (
                    <ContentViewer key={item.share_id} item={item} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
