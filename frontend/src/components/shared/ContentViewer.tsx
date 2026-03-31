import React from 'react'
import { ExternalLink, Github, Video, FileText, Twitter, Linkedin, Facebook, Instagram } from 'lucide-react'
import { SharedContentItem } from '@/types'

interface ContentViewerProps {
  item: SharedContentItem
  showSharedMetadata?: boolean
}

export default function ContentViewer({ item, showSharedMetadata = true }: ContentViewerProps) {
  const getSourceIcon = (source: string) => {
    switch (source.toLowerCase()) {
      case 'github':
        return <Github className="w-5 h-5" />
      case 'youtube':
        return <Video className="w-5 h-5" />
      case 'twitter':
        return <Twitter className="w-5 h-5" />
      case 'linkedin':
        return <Linkedin className="w-5 h-5" />
      case 'facebook':
        return <Facebook className="w-5 h-5" />
      case 'instagram':
        return <Instagram className="w-5 h-5" />
      default:
        return <FileText className="w-5 h-5" />
    }
  }

  const getYouTubeEmbedUrl = (url: string): string | null => {
    try {
      const urlObj = new URL(url)
      let videoId = null

      if (urlObj.hostname === 'youtu.be') {
        videoId = urlObj.pathname.slice(1)
      } else if (urlObj.hostname.includes('youtube.com')) {
        videoId = urlObj.searchParams.get('v')
      }

      return videoId ? `https://www.youtube.com/embed/${videoId}` : null
    } catch {
      return null
    }
  }

  const renderContent = () => {
    if (item.source.toLowerCase() === 'youtube') {
      const embedUrl = getYouTubeEmbedUrl(item.url)
      
      if (embedUrl) {
        return (
          <div className="aspect-video w-full bg-black rounded-lg overflow-hidden">
            <iframe
              src={embedUrl}
              title={item.title || 'YouTube video'}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              className="w-full h-full"
            />
          </div>
        )
      }
    }

    return (
      <a
        href={item.url}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-2 text-accent hover:text-accent/80 hover:underline"
      >
        <ExternalLink className="w-4 h-4" />
        Open Content
      </a>
    )
  }

  return (
    <div className="bg-bg-surface rounded-lg border border-border p-6 hover:border-accent/50 transition">
      {/* Source Badge */}
      <div className="flex items-center gap-3 mb-4">
        <div className="flex items-center gap-2 px-3 py-1 bg-bg-surface2 rounded-full text-sm font-medium text-muted">
          {getSourceIcon(item.source)}
          <span className="capitalize">{item.source}</span>
        </div>
        
        {item.sentiment && (
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              item.sentiment === 'positive'
                ? 'bg-success/20 text-success'
                : item.sentiment === 'negative'
                ? 'bg-danger/20 text-danger'
                : 'bg-bg-surface2 text-muted'
            }`}
          >
            {item.sentiment}
          </span>
        )}
      </div>

      {/* Title */}
      <h3 className="text-xl font-bold font-syne mb-3 text-text">
        {item.title || item.topic}
      </h3>

      {/* Content (Video or Link) */}
      <div className="mb-4">
        {renderContent()}
      </div>

      {/* Summary */}
      {item.summary && (
        <div className="mb-4 p-4 bg-bg-surface2 rounded-lg">
          <h4 className="text-sm font-medium text-muted mb-2">Summary</h4>
          <p className="text-sm text-text/80">{item.summary}</p>
        </div>
      )}

      {/* Content Preview */}
      {item.content && !item.summary && (
        <div className="mb-4">
          <p className="text-sm text-muted line-clamp-3">{item.content}</p>
        </div>
      )}

      {/* Keywords */}
      {item.keywords && item.keywords.length > 0 && (
        <div className="mb-4">
          <div className="flex flex-wrap gap-2">
            {item.keywords.slice(0, 5).map((keyword, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-accent/20 text-accent text-xs rounded-full"
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Shared Metadata */}
      {showSharedMetadata && (
        <div className="pt-4 border-t border-border mt-4">
          <div className="flex items-center justify-between text-sm text-muted">
            <div>
              <span className="font-medium text-text">Shared by:</span> {item.shared_by_username}
            </div>
            <div>
              <span className="font-medium text-text">To:</span> {item.shared_with_role_name}
            </div>
          </div>
          {item.notes && (
            <div className="mt-2 p-3 bg-warning/10 border border-warning/30 rounded text-sm text-text">
              <span className="font-medium">Note:</span> {item.notes}
            </div>
          )}
          <div className="mt-2 text-xs text-dim">
            Shared on {new Date(item.shared_at).toLocaleDateString()} at{' '}
            {new Date(item.shared_at).toLocaleTimeString()}
          </div>
        </div>
      )}
    </div>
  )
}
