import React, { useState } from 'react'
import { EditRequest, ApprovalStep, approveEditRequest, rejectEditRequest } from '../../api/editRequests'
import Badge from '../ui/Badge'
import Button from '../ui/Button'
import { Check, X, Clock, ChevronRight } from 'lucide-react'
import clsx from 'clsx'
import { useAuthStore } from '../../store/authStore'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { format } from 'date-fns'

interface ApprovalTimelineProps {
  request: EditRequest;
}

const ApprovalTimeline: React.FC<ApprovalTimelineProps> = ({ request }) => {
  const { minRoleLevel } = useAuthStore()
  const queryClient = useQueryClient()
  const [approveComment, setApproveComment] = useState('')

  const approveMutation = useMutation({
    mutationFn: (id: string) => approveEditRequest(id, approveComment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['records'] })
      queryClient.invalidateQueries({ queryKey: ['edit-requests'] })
      toast.success('ACCESS_GRANTED')
      setApproveComment('')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'APPROVAL_FAILED')
    }
  })

  const rejectMutation = useMutation({
    mutationFn: (id: string) => rejectEditRequest(id, approveComment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['records'] })
      queryClient.invalidateQueries({ queryKey: ['edit-requests'] })
      toast.error('ACCESS_DENIED')
      setApproveComment('')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'REJECTION_FAILED')
    }
  })

  const steps = request.steps || []

  const isCurrentStep = (step: ApprovalStep) => {
    if (step.decision !== null) return false
    // All prior steps must be approved
    const previousSteps = steps.filter(s => s.step_level < step.step_level)
    return previousSteps.every(s => s.decision === 'approved')
  }

  const canApprove = (step: ApprovalStep) => {
    if (!isCurrentStep(step)) return false
    return minRoleLevel <= step.required_min_role_level
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h4 className="font-syne font-extrabold text-muted text-xs uppercase tracking-widest">Approval Pipeline</h4>
        <Badge variant={request.status === 'approved' ? 'success' : request.status === 'rejected' ? 'danger' : 'warning'}>
          {request.status}
        </Badge>
      </div>

      <div className="relative pl-8 space-y-8 before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-border/50">
        {steps.sort((a, b) => a.step_level - b.step_level).map((step, index) => {
          const isActive = isCurrentStep(step)
          const isDone = step.decision !== null
          const isApproved = step.decision === 'approved'
          const isRejected = step.decision === 'rejected'

          return (
            <div key={step.id} className="relative">
              {/* Timeline Node */}
              <div className={clsx(
                "absolute -left-8 top-1.5 w-6.5 h-6.5 rounded-full border-2 flex items-center justify-center bg-bg-surface z-10 transition-colors",
                isApproved ? "border-success text-success shadow-[0_0_8px_rgba(79,209,142,0.3)]" :
                isRejected ? "border-danger text-danger shadow-[0_0_8px_rgba(247,95,95,0.3)]" :
                isActive ? "border-accent text-accent animate-pulse" :
                "border-border text-muted"
              )}>
                {isApproved ? <Check size={14} strokeWidth={3} /> :
                 isRejected ? <X size={14} strokeWidth={3} /> :
                 <Clock size={12} />}
              </div>

              {/* Step Content */}
              <div className={clsx(
                "p-4 rounded-lg border transition-all",
                isActive ? "bg-bg-surface2 border-accent/30" : "bg-bg-surface/50 border-border/50"
              )}>
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="text-xs font-mono font-bold uppercase text-muted tracking-widest">
                      Tier {index + 1} Clearance
                    </div>
                    <div className="text-sm font-syne font-bold flex items-center space-x-2">
                      <span>Level ≤ {step.required_min_role_level} Required</span>
                      <ChevronRight size={14} className="text-dim" />
                    </div>
                  </div>
                  
                  {isDone && (
                    <div className="text-[10px] font-mono text-dim text-right">
                      {step.decided_at && format(new Date(step.decided_at), 'HH:mm:ss')}
                    </div>
                  )}
                </div>

                {step.comment && isDone && (
                  <div className="mt-2 text-[10px] italic text-muted/80 font-mono">"{step.comment}"</div>
                )}

                {isActive && canApprove(step) && request.status === 'pending' && (
                  <div className="mt-4 space-y-3">
                    <input
                      type="text"
                      value={approveComment}
                      onChange={(e) => setApproveComment(e.target.value)}
                      placeholder="Optional comment..."
                      className="w-full bg-bg-base border border-border rounded px-3 py-1.5 font-mono text-xs focus:outline-none focus:border-accent transition-colors"
                    />
                    <div className="flex items-center space-x-2">
                      <Button 
                        size="sm" 
                        className="bg-success hover:bg-success/90 text-xs w-full py-1.5"
                        onClick={() => approveMutation.mutate(request.id)}
                        isLoading={approveMutation.isPending}
                      >
                        GRANT_ACCESS
                      </Button>
                      <Button 
                        size="sm" 
                        variant="danger" 
                        className="text-xs w-full py-1.5"
                        onClick={() => rejectMutation.mutate(request.id)}
                        isLoading={rejectMutation.isPending}
                      >
                        DENY_ACCESS
                      </Button>
                    </div>
                  </div>
                )}

                {isActive && !canApprove(step) && request.status === 'pending' && (
                  <div className="mt-3 text-[10px] font-mono text-warning italic uppercase flex items-center space-x-2 bg-warning/5 p-2 rounded">
                    <div className="w-1 h-1 bg-warning rounded-full animate-ping"></div>
                    <span>AWAITING_AUTHORIZED_CLEARANCE</span>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default ApprovalTimeline
