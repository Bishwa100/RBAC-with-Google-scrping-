import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { getEditRequests, EditRequest } from '../../api/editRequests'
import PageWrapper from '../../components/layout/PageWrapper'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import ApprovalTimeline from '../../components/approvals/ApprovalTimeline'
import { useAuthStore } from '../../store/authStore'
import { useNavigate } from 'react-router-dom'
import { FileEdit, Clock, CheckCircle2, XCircle, AlertTriangle, Eye } from 'lucide-react'
import { format } from 'date-fns'
import clsx from 'clsx'

const statusConfig = {
  pending: { icon: Clock, color: 'text-warning', bg: 'bg-warning/5 border-warning/20', label: 'PENDING' },
  approved: { icon: CheckCircle2, color: 'text-success', bg: 'bg-success/5 border-success/20', label: 'APPROVED' },
  rejected: { icon: XCircle, color: 'text-danger', bg: 'bg-danger/5 border-danger/20', label: 'REJECTED' },
  completed: { icon: CheckCircle2, color: 'text-muted', bg: 'bg-muted/5 border-muted/20', label: 'COMPLETED' },
}

const EditRequestListPage: React.FC = () => {
  const navigate = useNavigate()
  const { minRoleLevel } = useAuthStore()
  const isApprover = minRoleLevel <= 2

  const { data: requestsResponse, isLoading } = useQuery({
    queryKey: ['edit-requests'],
    queryFn: () => getEditRequests(),
  })

  const requests = requestsResponse?.data || []

  // Sort: pending first, then by created_at desc
  const sortedRequests = [...requests].sort((a, b) => {
    if (a.status === 'pending' && b.status !== 'pending') return -1
    if (a.status !== 'pending' && b.status === 'pending') return 1
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })

  const pendingCount = requests.filter(r => r.status === 'pending').length

  return (
    <PageWrapper title="Edit Requests">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-end">
          <div>
            <h3 className="text-2xl font-syne font-extrabold text-text uppercase tracking-tight">
              {isApprover ? 'Approval Queue' : 'My Edit Requests'}
            </h3>
            <p className="text-muted font-mono text-sm">
              {isApprover 
                ? 'Review and authorize pending data modification requests from your department.' 
                : 'Track the status of your data modification requests.'}
            </p>
          </div>
          {pendingCount > 0 && (
            <div className="flex items-center space-x-2 px-4 py-2 bg-warning/10 border border-warning/30 rounded-lg">
              <div className="w-2 h-2 bg-warning rounded-full animate-pulse" />
              <span className="font-mono text-xs text-warning font-bold">{pendingCount} PENDING</span>
            </div>
          )}
        </div>

        {/* Loading */}
        {isLoading && (
          <div className="text-center py-20">
            <div className="animate-pulse font-mono text-muted text-sm">LOADING_REQUESTS...</div>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && requests.length === 0 && (
          <div className="text-center py-20 border border-dashed border-border rounded-lg">
            <FileEdit size={48} className="mx-auto text-dim mb-4" />
            <h4 className="font-syne font-extrabold text-lg text-dim mb-2">NO_REQUESTS_FOUND</h4>
            <p className="font-mono text-xs text-muted">
              {isApprover ? 'No pending requests in your department.' : 'You have not submitted any edit requests.'}
            </p>
          </div>
        )}

        {/* Request Cards */}
        <div className="space-y-4">
          {sortedRequests.map(req => {
            const config = statusConfig[req.status] || statusConfig.pending
            const StatusIcon = config.icon

            return (
              <div 
                key={req.id}
                className={clsx(
                  "border rounded-lg overflow-hidden transition-all",
                  req.status === 'pending' ? "border-warning/30 bg-bg-surface" : "border-border bg-bg-surface/50"
                )}
              >
                {/* Card Header */}
                <div className="p-5 flex items-start justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center space-x-3">
                      <StatusIcon size={18} className={config.color} />
                      <span className="font-mono text-xs font-bold text-accent">
                        REQ-#{String(req.id).slice(0, 8)}
                      </span>
                      <Badge variant={
                        req.status === 'approved' ? 'success' : 
                        req.status === 'rejected' ? 'danger' : 
                        req.status === 'completed' ? 'muted' : 'warning'
                      }>
                        {config.label}
                      </Badge>
                    </div>
                    <p className="text-xs italic text-muted font-mono pl-8">"{req.reason}"</p>
                    <div className="flex items-center space-x-4 text-[10px] font-mono text-dim pl-8">
                      <span>Created: {format(new Date(req.created_at), 'yyyy-MM-dd HH:mm')}</span>
                      <span>Approvals: {req.approvals_received}/{req.approvals_required}</span>
                    </div>
                  </div>

                  <Button 
                    variant="secondary" 
                    size="sm" 
                    className="shrink-0 space-x-2"
                    onClick={() => navigate(`/records/${req.record_id}`)}
                  >
                    <Eye size={14} />
                    <span>VIEW_RECORD</span>
                  </Button>
                </div>

                {/* Approval Timeline (expanded for pending requests or if user is approver) */}
                {(req.status === 'pending' || req.steps.some(s => s.decision !== null)) && (
                  <div className="px-5 pb-5 border-t border-border/30 pt-4">
                    <ApprovalTimeline request={req} />
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </PageWrapper>
  )
}

export default EditRequestListPage
