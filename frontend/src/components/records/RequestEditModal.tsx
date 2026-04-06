import React, { useState } from 'react'
import Modal from '../ui/Modal'
import Button from '../ui/Button'
import { createEditRequest } from '../../api/editRequests'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { ShieldAlert, Info, ChevronRight, FileText } from 'lucide-react'
import { useConfirm } from '../ui/ConfirmProvider'

interface RequestEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  recordId: string;
}

const RequestEditModal: React.FC<RequestEditModalProps> = ({ isOpen, onClose, recordId }) => {
  const [step, setStep] = useState(1)
  const [reason, setReason] = useState('')
  const queryClient = useQueryClient()
  const confirmAction = useConfirm()

  const mutation = useMutation({
    mutationFn: (data: { record_id: string, reason: string }) => createEditRequest(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['records', recordId] })
      queryClient.invalidateQueries({ queryKey: ['edit-requests'] })
      toast.success('REQUEST_BROADCASTED')
      setStep(3)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'BROADCAST_FAILED')
    }
  })

  const handleSubmit = () => {
    if (reason.length < 10) {
      toast.error('REASON_TOO_SHORT_MIN_10_CHARS')
      return
    }
    ;(async () => {
      const confirmed = await confirmAction('Broadcast this edit request to the approval pipeline?')
      if (!confirmed) return
      mutation.mutate({ record_id: recordId, reason })
    })()
  }

  const handleClose = () => {
    setStep(1)
    setReason('')
    onClose()
  }

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Access Request Protocol">
      <div className="space-y-6">
        {/* Step Indicator */}
        <div className="flex items-center space-x-2 mb-8">
          {[1, 2, 3].map(i => (
            <div key={i} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs border-2 transition-colors ${
                step === i ? "border-accent text-accent bg-accent/5" : 
                step > i ? "border-success text-success bg-success/5" : "border-border text-muted"
              }`}>
                0{i}
              </div>
              {i < 3 && <div className={`w-8 h-0.5 mx-1 ${step > i ? "bg-success" : "bg-border"}`} />}
            </div>
          ))}
        </div>

        {step === 1 && (
          <div className="space-y-4 animate-in slide-in-from-right-4 duration-300">
            <div className="flex items-start space-x-4 p-4 bg-warning/5 border border-warning/20 rounded-lg text-warning">
              <ShieldAlert className="shrink-0 mt-1" size={20} />
              <div className="space-y-1">
                <div className="font-bold uppercase text-xs">Security Protocol Warning</div>
                <div className="text-xs font-mono leading-relaxed">
                  This record is under FROZEN status. Requesting an edit window requires multi-stage authorization from departmental supervisors.
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-mono font-bold uppercase text-muted tracking-widest">Justification for Access</label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Specify the reason for overriding data freeze..."
                className="w-full h-32 bg-bg-surface2 border border-border rounded-md p-4 font-mono text-sm focus:outline-none focus:border-accent transition-colors resize-none"
              />
              <div className="text-[10px] text-dim text-right font-mono">CHARS: {reason.length}</div>
            </div>

            <Button className="w-full space-x-2" onClick={() => setStep(2)}>
              <span>PROCEED_TO_VALIDATION</span>
              <ChevronRight size={16} />
            </Button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
            <div className="p-4 border border-border rounded-lg bg-bg-surface2">
              <div className="flex items-center space-x-3 mb-4 text-accent">
                <Info size={18} />
                <span className="font-syne font-bold uppercase text-xs">Approval Flow Mapping</span>
              </div>
              <ul className="space-y-3 font-mono text-[11px] text-muted">
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-accent rounded-full" />
                  <span>TIER 01: L+1 AUTHORITY (ONE LEVEL ABOVE YOU)</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-accent rounded-full" />
                  <span>TIER 02: L+2 AUTHORITY (TWO LEVELS ABOVE YOU)</span>
                </li>
              </ul>
            </div>

            <div className="p-4 border border-dashed border-border rounded-lg space-y-2">
              <div className="text-[10px] font-mono text-dim uppercase">Reason Preview</div>
              <div className="text-xs italic text-text/80">"{reason}"</div>
            </div>

            <div className="flex space-x-3">
              <Button variant="secondary" className="w-full" onClick={() => setStep(1)}>BACK</Button>
              <Button 
                className="w-full" 
                onClick={handleSubmit}
                isLoading={mutation.isPending}
              >
                INITIALIZE_REQUEST
              </Button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-6 py-4 text-center animate-in zoom-in-95 duration-500">
            <div className="w-16 h-16 rounded-full bg-success/10 border-2 border-success flex items-center justify-center mx-auto mb-4">
              <FileText className="text-success" size={32} />
            </div>
            <h4 className="text-xl font-syne font-extrabold text-success">REQUEST_INITIALIZED</h4>
            <p className="font-mono text-muted text-xs px-4">
              Your edit request has been broadcasted to the approval pipeline. You will be notified once both tiers approve.
            </p>
            <Button className="w-full mt-4" onClick={handleClose}>CLOSE_TERMINAL</Button>
          </div>
        )}
      </div>
    </Modal>
  )
}

export default RequestEditModal
