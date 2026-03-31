import React, { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { topiclensAPI } from '@/api'
import api from '@/api/client'
import { Role } from '@/types'

interface ShareModalProps {
  isOpen: boolean
  onClose: () => void
  jobId: string
  source: string
  url: string
  resultTitle?: string
  content?: string
  rank?: number
  onShareSuccess?: () => void
}

export default function ShareModal({
  isOpen,
  onClose,
  jobId,
  source,
  url,
  resultTitle,
  content,
  rank,
  onShareSuccess
}: ShareModalProps) {
  const [roles, setRoles] = useState<Role[]>([])
  const [selectedRoleIds, setSelectedRoleIds] = useState<string[]>([])
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingRoles, setLoadingRoles] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (isOpen) {
      fetchRoles()
      setSelectedRoleIds([])
      setNotes('')
      setError(null)
      setSuccess(false)
    }
  }, [isOpen])

  const fetchRoles = async () => {
    setLoadingRoles(true)
    try {
      const response = await api.get('/api/v1/roles')
      if (response.success && response.data) {
        // Handle both formats: { roles: [...] } or direct array [...]
        const rolesData = response.data.roles || (Array.isArray(response.data) ? response.data : [])
        setRoles(rolesData)
      }
    } catch (err: any) {
      setError('Failed to load roles')
      console.error('Error loading roles:', err)
    } finally {
      setLoadingRoles(false)
    }
  }

  const handleToggleRole = (roleId: string) => {
    setSelectedRoleIds(prev =>
      prev.includes(roleId)
        ? prev.filter(id => id !== roleId)
        : [...prev, roleId]
    )
  }

  const handleShare = async () => {
    if (selectedRoleIds.length === 0) {
      setError('Please select at least one role')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await topiclensAPI.shareContent({
        job_id: jobId,
        role_ids: selectedRoleIds,
        source: source,
        url: url,
        title: resultTitle,
        content: content,
        rank: rank,
        notes: notes.trim() || undefined
      })

      if (response.success) {
        setSuccess(true)
        setTimeout(() => {
          onClose()
          if (onShareSuccess) onShareSuccess()
        }, 1500)
      } else {
        setError(response.detail || 'Failed to share content')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to share content')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-bg-surface rounded-lg border border-border max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h2 className="text-2xl font-bold font-syne text-text">Share Content</h2>
          <button
            onClick={onClose}
            className="text-muted hover:text-text transition"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
          {/* Result Info */}
          {resultTitle && (
            <div className="mb-6 p-4 bg-accent/10 rounded-lg border border-accent/30">
              <p className="text-sm text-muted mb-1">Sharing:</p>
              <p className="font-medium text-text">{resultTitle}</p>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="mb-4 p-4 bg-success/20 border border-success text-success rounded-lg">
              Content shared successfully!
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-4 bg-danger/20 border border-danger text-danger rounded-lg">
              {error}
            </div>
          )}

          {/* Roles Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-3 text-muted">
              Select Roles to Share With
            </label>
            
            {loadingRoles ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
              </div>
            ) : roles.length === 0 ? (
              <p className="text-muted text-center py-4">No roles available</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {roles.map((role) => (
                  <button
                    key={role.id}
                    onClick={() => handleToggleRole(role.id)}
                    disabled={loading || success}
                    className={`p-4 rounded-lg border-2 text-left transition ${
                      selectedRoleIds.includes(role.id)
                        ? 'border-accent bg-accent/10'
                        : 'border-border hover:border-accent/50 bg-bg-surface2'
                    } ${loading || success ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="font-medium text-text">{role.name}</p>
                        {role.description && (
                          <p className="text-sm text-muted mt-1">{role.description}</p>
                        )}
                        <p className="text-xs text-dim mt-1">Level: {role.level}</p>
                      </div>
                      {selectedRoleIds.includes(role.id) && (
                        <div className="ml-2 w-6 h-6 bg-accent rounded-full flex items-center justify-center">
                          <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Optional Notes */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-muted">
              Notes (Optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              disabled={loading || success}
              placeholder="Add a message for users receiving this content..."
              rows={3}
              className="w-full px-4 py-2 border border-border rounded-lg bg-bg-surface2 text-text placeholder-dim focus:ring-2 focus:ring-accent focus:border-transparent disabled:bg-dim/20"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-border bg-bg-surface2">
          <button
            onClick={onClose}
            disabled={loading}
            className="px-6 py-2 border border-border rounded-lg text-muted hover:bg-bg-surface hover:text-text transition disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleShare}
            disabled={loading || success || selectedRoleIds.length === 0}
            className="px-6 py-2 bg-accent text-white rounded-lg hover:bg-accent/80 transition disabled:bg-dim disabled:cursor-not-allowed"
          >
            {loading ? 'Sharing...' : success ? 'Shared!' : `Share with ${selectedRoleIds.length} Role${selectedRoleIds.length !== 1 ? 's' : ''}`}
          </button>
        </div>
      </div>
    </div>
  )
}
