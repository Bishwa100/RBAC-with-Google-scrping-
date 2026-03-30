import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getRecord, updateRecord } from '../../api/records'
import { getEditRequests } from '../../api/editRequests'
import PageWrapper from '../../components/layout/PageWrapper'
import Button from '../../components/ui/Button'
import Badge from '../../components/ui/Badge'
import FrozenBadge from '../../components/records/FrozenBadge'
import RequestEditModal from '../../components/records/RequestEditModal'
import ApprovalTimeline from '../../components/approvals/ApprovalTimeline'
import RecordForm, { RecordPayload } from '../../components/records/RecordForm'
import { useAuthStore } from '../../store/authStore'
import { 
  ArrowLeft, 
  Database, 
  History, 
  FileEdit, 
  ShieldCheck, 
  Save,
  X,
  ClipboardList
} from 'lucide-react'
import { toast } from 'sonner'

const RecordDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user, minRoleLevel, scopes } = useAuthStore()
  
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState<RecordPayload>({ full_name: '', email: '', notes: '' })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const { data: recordResponse, isLoading: isRecordLoading } = useQuery({
    queryKey: ['records', id],
    queryFn: () => getRecord(id!),
    enabled: !!id,
  })

  const { data: requestsResponse } = useQuery({
    queryKey: ['edit-requests'],
    queryFn: () => getEditRequests(),
    enabled: !!id,
  })

  const record = recordResponse?.data
  
  useEffect(() => {
    if (record?.payload) {
      setFormData(record.payload as RecordPayload)
    }
  }, [record])

  const allRequests = requestsResponse?.data || []
  // Filter requests for this record
  const requests = allRequests.filter(r => r.record_id === id)
  const activeRequest = requests.find(r => r.status === 'pending')
  const approvedRequest = requests.find(r => r.status === 'approved')

  const isOwner = record?.submitted_by === user?.id
  const hasEditScope = minRoleLevel === 0 || scopes.includes('records:update')
  
  const hasActiveEditWindow = !!approvedRequest
  const canEdit = hasActiveEditWindow && hasEditScope

  const updateMutation = useMutation({
    mutationFn: (data: any) => updateRecord(id!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['records', id] })
      queryClient.invalidateQueries({ queryKey: ['edit-requests'] })
      setIsEditing(false)
      toast.success('RECORD_UPDATED_AND_REFROZEN')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'UPDATE_FAILED')
    }
  })

  const validate = () => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.full_name) {
      newErrors.full_name = 'REQUIRED_FIELD'
    } else if (!/^[a-zA-Z0-9\s]+$/.test(formData.full_name)) {
      newErrors.full_name = 'NO_SPECIAL_CHARACTERS_ALLOWED'
    }

    if (!formData.email) {
      newErrors.email = 'REQUIRED_FIELD'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'INVALID_EMAIL_FORMAT'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleStartEdit = () => {
    setFormData(record?.payload as RecordPayload)
    setIsEditing(true)
  }

  const handleSave = () => {
    if (validate()) {
      updateMutation.mutate({ payload: formData })
    } else {
      toast.error('VALIDATION_FAILED')
    }
  }

  if (isRecordLoading) return <PageWrapper title="Loading..."><div className="animate-pulse font-mono">ENCRYPTING_CHANNEL...</div></PageWrapper>
  if (!record) return <PageWrapper title="Error"><div className="text-danger font-mono">RECORD_NOT_FOUND</div></PageWrapper>

  return (
    <PageWrapper title={`Record: ${record.record_type}`}>
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left: Content (Col 2) */}
        <div className="lg:col-span-2 space-y-6">
          <button 
            onClick={() => navigate('/records')}
            className="flex items-center space-x-2 text-muted hover:text-accent transition-colors font-mono text-xs uppercase"
          >
            <ArrowLeft size={14} />
            <span>Return to Database</span>
          </button>

          {/* Banner Status */}
          {hasActiveEditWindow ? (
            <div className="bg-success/10 border border-success/30 p-6 rounded-lg flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 rounded-full bg-success/20 flex items-center justify-center text-success">
                  <FileEdit size={24} />
                </div>
                <div>
                  <h4 className="font-syne font-extrabold text-success uppercase">Edit Window Authorized</h4>
                  <p className="text-xs font-mono text-muted">The security freeze has been temporarily lifted for this segment.</p>
                </div>
              </div>
            </div>
          ) : record.is_frozen ? (
            <div className="bg-frozen/10 border border-frozen/30 p-6 rounded-lg flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 rounded-full bg-frozen/20 flex items-center justify-center text-frozen">
                  <ShieldCheck size={24} />
                </div>
                <div>
                  <h4 className="font-syne font-extrabold text-frozen uppercase">Frozen Data Protocol Active</h4>
                  <p className="text-xs font-mono text-muted">Modification is strictly disabled until multi-stage approval is granted.</p>
                </div>
              </div>
              {isOwner && !activeRequest && (
                <Button 
                  variant="outline" 
                  className="border-frozen text-frozen hover:bg-frozen/10"
                  onClick={() => setIsEditModalOpen(true)}
                >
                  REQUEST_ACCESS
                </Button>
              )}
              {activeRequest && (
                <Badge variant="warning">PENDING_APPROVAL</Badge>
              )}
            </div>
          ) : null}

          {/* Data Payload Panel */}
          <div className="bg-bg-surface border border-border rounded-lg overflow-hidden">
            <div className="p-4 border-b border-border bg-bg-surface2/50 flex items-center justify-between">
              <div className="flex items-center space-x-2 font-syne font-bold">
                {isEditing ? <ClipboardList size={16} className="text-accent" /> : <Database size={16} className="text-accent" />}
                <span>{isEditing ? 'DATA_ENTRY_FORM' : 'DATA_PAYLOAD'}</span>
              </div>
              {canEdit && !isEditing && (
                <Button size="sm" onClick={handleStartEdit}>INIT_EDITOR</Button>
              )}
              {isEditing && (
                <div className="flex space-x-2">
                  <Button size="sm" variant="ghost" onClick={() => setIsEditing(false)}>
                    <X size={14} className="mr-1" /> CANCEL
                  </Button>
                  <Button size="sm" onClick={handleSave} isLoading={updateMutation.isPending}>
                    <Save size={14} className="mr-1" /> COMMIT_CHANGES
                  </Button>
                </div>
              )}
            </div>
            <div className="p-6">
              {isEditing ? (
                <RecordForm data={formData} onChange={setFormData} errors={errors} />
              ) : (
                <div className="space-y-8">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                    <div>
                      <div className="text-[10px] font-mono text-dim uppercase mb-1">Full Name</div>
                      <div className="text-sm font-mono font-bold text-text border-l-2 border-accent pl-3">
                        {record.payload.full_name || 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] font-mono text-dim uppercase mb-1">Email Address</div>
                      <div className="text-sm font-mono font-bold text-text border-l-2 border-accent pl-3">
                        {record.payload.email || 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] font-mono text-dim uppercase mb-1">Phone Number</div>
                      <div className="text-sm font-mono font-bold text-text border-l-2 border-accent/40 pl-3">
                        {record.payload.phone_number || 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] font-mono text-dim uppercase mb-1">Location</div>
                      <div className="text-sm font-mono font-bold text-text border-l-2 border-accent/40 pl-3">
                        {record.payload.location || 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] font-mono text-dim uppercase mb-1">Effective Date</div>
                      <div className="text-sm font-mono font-bold text-text border-l-2 border-accent/40 pl-3">
                        {record.payload.date || 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] font-mono text-dim uppercase mb-1">Timestamp</div>
                      <div className="text-sm font-mono font-bold text-text border-l-2 border-accent/40 pl-3">
                        {record.payload.time || 'N/A'}
                      </div>
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] font-mono text-dim uppercase mb-1">Detailed Notes</div>
                    <div className="text-sm font-mono text-muted bg-bg-base p-4 rounded border border-border whitespace-pre-wrap leading-relaxed">
                      {record.payload.notes || 'No additional notes provided.'}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right: Metadata & Approvals (Col 1) */}
        <div className="space-y-6">
          <div className="bg-bg-surface border border-border rounded-lg p-6 space-y-6">
            <h4 className="font-syne font-extrabold text-xs uppercase tracking-widest text-muted border-b border-border pb-4">Segment Metadata</h4>
            
            <div className="space-y-4">
              <div className="space-y-1">
                <div className="text-[10px] font-mono text-dim uppercase">Status</div>
                <FrozenBadge isFrozen={record.is_frozen} />
              </div>
              <div className="space-y-1">
                <div className="text-[10px] font-mono text-dim uppercase">Record Type</div>
                <Badge variant="muted">{record.record_type.toUpperCase()}</Badge>
              </div>
              <div className="space-y-1">
                <div className="text-[10px] font-mono text-dim uppercase">Version</div>
                <div className="text-sm font-mono font-bold text-text">v{record.version}</div>
              </div>
              <div className="space-y-1">
                <div className="text-[10px] font-mono text-dim uppercase">Data Custodian</div>
                <div className="text-sm font-mono font-bold text-text">
                  USER_#{String(record.submitted_by).slice(0, 8)} {isOwner && '(YOU)'}
                </div>
              </div>
              <div className="space-y-1">
                <div className="text-[10px] font-mono text-dim uppercase">Timestamp (Init)</div>
                <div className="text-sm font-mono text-text/70">{new Date(record.created_at).toLocaleString()}</div>
              </div>
            </div>
          </div>

          <div className="bg-bg-surface border border-border rounded-lg p-6">
            <div className="flex items-center space-x-2 mb-6 text-muted">
              <History size={16} />
              <h4 className="font-syne font-extrabold text-xs uppercase tracking-widest">Approval History</h4>
            </div>

            <div className="space-y-8">
              {requests.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-[10px] font-mono text-dim uppercase">No active requests</div>
                </div>
              ) : (
                requests.map(req => (
                  <div key={req.id} className="space-y-4 border-t border-border/50 pt-4 first:border-0 first:pt-0">
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-[10px] font-mono font-bold text-accent">REQ-#{String(req.id).slice(0, 8)}</div>
                      <Badge variant={req.status === 'approved' ? 'success' : req.status === 'rejected' ? 'danger' : 'warning'}>
                        {req.status}
                      </Badge>
                    </div>
                    <div className="text-xs italic text-muted mb-4">"{req.reason}"</div>
                    <ApprovalTimeline request={req} />
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      <RequestEditModal 
        isOpen={isEditModalOpen} 
        onClose={() => setIsEditModalOpen(false)} 
        recordId={id!} 
      />
    </PageWrapper>
  )
}

export default RecordDetail
