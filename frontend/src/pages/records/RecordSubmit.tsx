import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { createRecord } from '../../api/records'
import PageWrapper from '../../components/layout/PageWrapper'
import Button from '../../components/ui/Button'
import RecordForm, { RecordPayload } from '../../components/records/RecordForm'
import { ArrowLeft, Upload, FileJson, ChevronRight, ShieldCheck, ClipboardList } from 'lucide-react'
import { toast } from 'sonner'
import clsx from 'clsx'
import { useConfirm } from '../../components/ui/ConfirmProvider'

const RECORD_TYPES = [
  { value: 'attendance_log', label: 'Attendance Log', desc: 'Daily attendance and check-in records' },
  { value: 'expense_report', label: 'Expense Report', desc: 'Financial claims and reimbursements' },
  { value: 'training_record', label: 'Training Record', desc: 'Training sessions and completion data' },
  { value: 'inventory_entry', label: 'Inventory Entry', desc: 'Asset and resource tracking logs' },
  { value: 'compliance_report', label: 'Compliance Report', desc: 'Regulatory compliance documentation' },
]

const INITIAL_PAYLOAD: RecordPayload = {
  full_name: '',
  email: '',
  phone_number: '',
  date: new Date().toISOString().split('T')[0],
  time: new Date().toTimeString().split(' ')[0].slice(0, 5),
  location: '',
  notes: ''
}

const RecordSubmit: React.FC = () => {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [recordType, setRecordType] = useState('')
  const [formData, setFormData] = useState<RecordPayload>(INITIAL_PAYLOAD)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const mutation = useMutation({
    mutationFn: (data: { record_type: string, payload: any }) => createRecord(data),
    onSuccess: () => {
      toast.success('SEGMENT_COMMITTED_AND_FROZEN')
      navigate('/records')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'SUBMISSION_FAILED')
    }
  })

  const confirmAction = useConfirm()

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

  const handleSelectType = (type: string) => {
    setRecordType(type)
    setStep(2)
  }

  const handleNext = () => {
    if (validate()) {
      setStep(3)
    } else {
      toast.error('VALIDATION_FAILED')
    }
  }

  const handleSubmit = () => {
    ;(async () => {
      const confirmed = await confirmAction(`Are you sure you want to submit and permanently freeze this record? This action cannot be undone.`)
      if (!confirmed) return
      mutation.mutate({ record_type: recordType, payload: formData })
    })()
  }

  return (
    <PageWrapper title="Submit New Record">
      <div className="max-w-3xl mx-auto space-y-8">
        <button 
          onClick={() => navigate('/records')}
          className="flex items-center space-x-2 text-muted hover:text-accent transition-colors font-mono text-xs uppercase"
        >
          <ArrowLeft size={14} />
          <span>Return to Database</span>
        </button>

        {/* Header */}
        <div>
          <h3 className="text-2xl font-syne font-extrabold text-text uppercase tracking-tight">New Data Segment</h3>
          <p className="text-muted font-mono text-sm mt-1">
            Submit a new data entry. Once submitted, the record will be <span className="text-frozen font-bold">FROZEN</span> immediately.
          </p>
        </div>

        {/* Step Indicator */}
        <div className="flex items-center space-x-3">
          {['Select Type', 'Enter Data', 'Confirm'].map((label, i) => (
            <div key={i} className="flex items-center">
              <div className={clsx(
                "w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs border-2 transition-all",
                step > i + 1 ? "border-success text-success bg-success/5" :
                step === i + 1 ? "border-accent text-accent bg-accent/5" :
                "border-border text-muted"
              )}>
                0{i + 1}
              </div>
              <span className={clsx("ml-2 text-xs font-mono uppercase", step === i + 1 ? "text-accent" : "text-dim")}>{label}</span>
              {i < 2 && <ChevronRight size={14} className="mx-2 text-dim" />}
            </div>
          ))}
        </div>

        {/* Step 1: Select Type */}
        {step === 1 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {RECORD_TYPES.map(type => (
              <button
                key={type.value}
                onClick={() => handleSelectType(type.value)}
                className="p-5 bg-bg-surface border border-border rounded-lg hover:border-accent/50 hover:bg-bg-surface2 transition-all text-left group"
              >
                <div className="flex items-center space-x-3 mb-2">
                  <FileJson size={18} className="text-accent group-hover:scale-110 transition-transform" />
                  <span className="font-syne font-bold text-sm uppercase">{type.label}</span>
                </div>
                <p className="text-[11px] font-mono text-muted">{type.desc}</p>
              </button>
            ))}
          </div>
        )}

        {/* Step 2: Enter Data */}
        {step === 2 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-muted uppercase">
                Type: <span className="text-accent font-bold">{recordType.replace(/_/g, ' ')}</span>
              </span>
              <Button variant="secondary" size="sm" onClick={() => setStep(1)}>CHANGE_TYPE</Button>
            </div>

            <div className="bg-bg-surface border border-border rounded-lg overflow-hidden">
              <div className="p-3 border-b border-border bg-bg-surface2/50 flex items-center space-x-2">
                <ClipboardList size={14} className="text-accent" />
                <span className="font-syne font-bold text-xs">DATA_ENTRY_FORM</span>
              </div>
              <div className="p-6">
                <RecordForm data={formData} onChange={setFormData} errors={errors} />
              </div>
            </div>

            <div className="flex space-x-3">
              <Button variant="secondary" className="w-full" onClick={() => setStep(1)}>BACK</Button>
              <Button className="w-full space-x-2" onClick={handleNext}>
                <span>REVIEW_SUBMISSION</span>
                <ChevronRight size={16} />
              </Button>
            </div>
          </div>
        )}

        {/* Step 3: Confirm */}
        {step === 3 && (
          <div className="space-y-6">
            <div className="bg-frozen/5 border border-frozen/20 p-5 rounded-lg flex items-start space-x-4">
              <ShieldCheck size={24} className="text-frozen shrink-0 mt-0.5" />
              <div>
                <p className="font-bold text-frozen text-xs uppercase mb-1">Freeze Protocol Notice</p>
                <p className="font-mono text-xs text-muted leading-relaxed">
                  Upon submission this record will be <strong className="text-frozen">PERMANENTLY FROZEN</strong>. 
                  Any future modifications will require a multi-stage approval workflow involving two levels 
                  of authority above your clearance level.
                </p>
              </div>
            </div>

            <div className="bg-bg-surface border border-border rounded-lg p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-4">
                <div className="text-[10px] font-mono text-dim uppercase">Record Type</div>
                <div className="text-sm font-mono font-bold text-accent">{recordType.replace(/_/g, ' ').toUpperCase()}</div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 pt-2">
                <div>
                  <div className="text-[10px] font-mono text-dim uppercase mb-1">Full Name</div>
                  <div className="text-sm font-mono text-text">{formData.full_name}</div>
                </div>
                <div>
                  <div className="text-[10px] font-mono text-dim uppercase mb-1">Email</div>
                  <div className="text-sm font-mono text-text">{formData.email}</div>
                </div>
                <div>
                  <div className="text-[10px] font-mono text-dim uppercase mb-1">Phone</div>
                  <div className="text-sm font-mono text-text">{formData.phone_number || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-[10px] font-mono text-dim uppercase mb-1">Location</div>
                  <div className="text-sm font-mono text-text">{formData.location || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-[10px] font-mono text-dim uppercase mb-1">Date</div>
                  <div className="text-sm font-mono text-text">{formData.date}</div>
                </div>
                <div>
                  <div className="text-[10px] font-mono text-dim uppercase mb-1">Time</div>
                  <div className="text-sm font-mono text-text">{formData.time}</div>
                </div>
              </div>
              
              <div className="pt-2">
                <div className="text-[10px] font-mono text-dim uppercase mb-1">Notes</div>
                <div className="text-sm font-mono text-muted whitespace-pre-wrap">{formData.notes || 'No additional notes provided.'}</div>
              </div>
            </div>

            <div className="flex space-x-3">
              <Button variant="secondary" className="w-full" onClick={() => setStep(2)}>BACK</Button>
              <Button 
                className="w-full space-x-2" 
                onClick={handleSubmit}
                isLoading={mutation.isPending}
              >
                <Upload size={16} />
                <span>SUBMIT_AND_FREEZE</span>
              </Button>
            </div>
          </div>
        )}
      </div>
    </PageWrapper>
  )
}

export default RecordSubmit
