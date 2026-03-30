import React, { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { useNavigate } from 'react-router-dom'
import { getUsers, createUser, extractUserInfo } from '../../api/users'
import { getDepartments } from '../../api/departments'
import { User } from '../../types'
import PageWrapper from '../../components/layout/PageWrapper'
import DataTable from '../../components/shared/DataTable'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import Modal from '../../components/ui/Modal'
import { 
  UserPlus, 
  MoreVertical, 
  ShieldAlert, 
  Key, 
  Upload, 
  FileText, 
  Image as ImageIcon,
  X,
  Phone,
  Mail,
  User as UserIcon,
  Loader2,
  FileSpreadsheet,
  CheckCircle2,
  Info
} from 'lucide-react'
import clsx from 'clsx'
import { useAuthStore } from '../../store/authStore'
import { toast } from 'sonner'

const UserList: React.FC = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { minRoleLevel } = useAuthStore()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [extractedData, setExtractedData] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    phone: '',
    password: 'Pass123!',
    dept_id: '',
    details: {
      designation: '',
      employee_id: '',
      joining_date: ''
    }
  })

  const { data: usersResponse, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => getUsers(),
  })

  const { data: deptsResponse } = useQuery({
    queryKey: ['departments'],
    queryFn: () => getDepartments(),
    enabled: isModalOpen
  })

  const users = usersResponse?.data || []
  const departments = deptsResponse?.data || []

  const createMutation = useMutation({
    mutationFn: (data: any) => createUser(data, selectedFile || undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      setIsModalOpen(false)
      toast.success('OPERATIVE_ENLISTED_SUCCESSFULLY')
      setFormData({ 
        email: '', 
        full_name: '', 
        phone: '', 
        password: 'Pass123!', 
        dept_id: '',
        details: { designation: '', employee_id: '', joining_date: '' }
      })
      setSelectedFile(null)
      setExtractedData(null)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'ENLISTMENT_FAILED')
    }
  })

  const extractMutation = useMutation({
    mutationFn: (file: File) => extractUserInfo(file),
    onSuccess: (res) => {
      const data = res.data
      setExtractedData(data)
      
      // Auto-fill logic with dynamic mapping
      const newFormData = { 
        ...formData,
        details: { ...formData.details } 
      }
      
      // Direct mappings
      if (data.full_name || data.name || data.customer_name) 
        newFormData.full_name = data.full_name || data.name || data.customer_name
        
      if (data.email || data.email_address) 
        newFormData.email = data.email || data.email_address
        
      if (data.phone || data.mobile || data.contact || data.phone_number) 
        newFormData.phone = data.phone || data.mobile || data.contact || data.phone_number
      
      // Details mappings
      if (data.designation || data.role || data.job_title || data.position) 
        newFormData.details.designation = data.designation || data.role || data.job_title || data.position
      
      if (data.employee_id || data.id_number || data.staff_id || data.registration_number) 
        newFormData.details.employee_id = data.employee_id || data.id_number || data.staff_id || data.registration_number
        
      if (data.joining_date || data.hired_date || data.start_date || data.date_of_joining) {
        let dateVal = data.joining_date || data.hired_date || data.start_date || data.date_of_joining
        // Basic date format check (YYYY-MM-DD)
        if (typeof dateVal === 'string' && dateVal.match(/^\d{4}-\d{2}-\d{2}/)) {
          newFormData.details.joining_date = dateVal.substring(0, 10)
        }
      }
      
      setFormData(newFormData)
      toast.success('AI_EXTRACTION_COMPLETE_FIELDS_POPULATED')
    },
    onError: () => {
      toast.error('AI_EXTRACTION_FAILED_SERVICE_UNAVAILABLE')
    }
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    setSelectedFile(file)
    if (file) {
      extractMutation.mutate(file)
    }
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setSelectedFile(null)
    setExtractedData(null)
    setFormData({ 
      email: '', 
      full_name: '', 
      phone: '', 
      password: 'Pass123!', 
      dept_id: '',
      details: { designation: '', employee_id: '', joining_date: '' }
    })
  }

  const columns: ColumnDef<User>[] = [
    {
      accessorKey: 'full_name',
      header: 'Operator',
      cell: ({ row }) => (
        <div className="flex items-center space-x-3">
          <div className={clsx(
            "w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs",
            `bg-role-${Math.min(...row.original.roles.map(r => r.level), 4)}`
          )}>
            {row.original.full_name.charAt(0)}
          </div>
          <div>
            <div className="font-bold text-text">{row.original.full_name}</div>
            <div className="text-[10px] text-muted">{row.original.email}</div>
          </div>
        </div>
      )
    },
    {
      accessorKey: 'department',
      header: 'Sector',
      cell: ({ row }) => (
        <Badge variant="muted">
          {row.original.department?.name || 'UNASSIGNED'}
        </Badge>
      )
    },
    {
      accessorKey: 'roles',
      header: 'Clearance',
      cell: ({ row }) => (
        <div className="flex flex-wrap gap-1">
          {row.original.roles.map(role => (
            <div 
              key={role.id}
              className={clsx(
                "text-[10px] font-mono font-bold px-1.5 py-0.5 rounded border",
                `bg-role-${role.level}/10 text-role-${role.level} border-role-${role.level}/20`
              )}
            >
              {role.name}
            </div>
          ))}
        </div>
      )
    },
    {
      accessorKey: 'is_active',
      header: 'Status',
      cell: ({ row }) => (
        <Badge variant={row.original.is_active ? 'success' : 'danger'}>
          {row.original.is_active ? 'ACTIVE' : 'SUSPENDED'}
        </Badge>
      )
    },
    {
      id: 'actions',
      header: '',
      cell: ({ row }) => (
        <div className="flex justify-end space-x-2">
          {minRoleLevel <= 2 && (
            <Button 
              variant="ghost" 
              size="sm" 
              className="font-mono text-[10px] space-x-1 hover:text-accent"
              onClick={() => navigate(`/users/${row.original.id}`)}
            >
              <Key size={12} />
              <span>EDIT_CLEARANCE</span>
            </Button>
          )}
          <Button variant="ghost" size="icon">
            <MoreVertical size={16} />
          </Button>
        </div>
      )
    }
  ]

  return (
    <PageWrapper title="User Management">
      <div className="space-y-6">
        <div className="flex justify-between items-end">
          <div>
            <h3 className="text-2xl font-syne font-extrabold text-text uppercase tracking-tight">Personnel Database</h3>
            <p className="text-muted font-mono text-sm">Authorized access to operative records and clearance levels.</p>
          </div>
          
          <div className="flex space-x-3">
            {minRoleLevel <= 2 && (
              <Button className="space-x-2" onClick={() => setIsModalOpen(true)}>
                <UserPlus size={18} />
                <span>ENLIST_OPERATIVE</span>
              </Button>
            )}
          </div>
        </div>

        <DataTable 
          columns={columns} 
          data={users} 
          isLoading={isLoading} 
        />

        <Modal 
          isOpen={isModalOpen} 
          onClose={handleModalClose} 
          title="Operative Enlistment Protocol"
          size="lg"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <div className="space-y-1">
                <label className="text-[10px] font-mono text-dim uppercase flex items-center">
                  <UserIcon size={10} className="mr-1" /> Full Designation (Name)
                </label>
                <input 
                  type="text"
                  className="w-full bg-bg-base border border-border focus:border-accent rounded px-4 py-2 text-sm focus:outline-none font-mono"
                  value={formData.full_name}
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  placeholder="e.g. JOHN_DOE"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-mono text-dim uppercase flex items-center">
                  <Mail size={10} className="mr-1" /> Communication Node (Email)
                </label>
                <input 
                  type="email"
                  className="w-full bg-bg-base border border-border focus:border-accent rounded px-4 py-2 text-sm focus:outline-none font-mono"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  placeholder="operative@node.local"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-mono text-dim uppercase flex items-center">
                  <Phone size={10} className="mr-1" /> Contact Line (Phone)
                </label>
                <input 
                  type="text"
                  className="w-full bg-bg-base border border-border focus:border-accent rounded px-4 py-2 text-sm focus:outline-none font-mono"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  placeholder="+X XXX XXX XXXX"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-mono text-dim uppercase">Sector Assignment</label>
                <select 
                  className="w-full bg-bg-base border border-border focus:border-accent rounded px-4 py-2 text-sm focus:outline-none font-mono"
                  value={formData.dept_id}
                  onChange={(e) => setFormData({...formData, dept_id: e.target.value})}
                >
                  <option value="">GLOBAL_PROTOCOL (No Sector)</option>
                  {departments.map(d => (
                    <option key={d.id} value={d.id}>{d.name.toUpperCase()}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="space-y-4">
              <div className="bg-accent/5 p-4 rounded-lg border border-accent/20 space-y-3">
                <div className="flex items-center space-x-2 text-accent mb-1">
                  <FileText size={14} />
                  <span className="text-[10px] font-bold uppercase tracking-wider">Detailed Identification</span>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-[10px] font-mono text-dim uppercase">Designation</label>
                    <input 
                      type="text"
                      className="w-full bg-bg-base border border-border focus:border-accent rounded px-3 py-1.5 text-xs focus:outline-none font-mono"
                      value={formData.details.designation}
                      onChange={(e) => setFormData({
                        ...formData, 
                        details: { ...formData.details, designation: e.target.value }
                      })}
                      placeholder="e.g. AGENT"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-mono text-dim uppercase">Employee ID</label>
                    <input 
                      type="text"
                      className="w-full bg-bg-base border border-border focus:border-accent rounded px-3 py-1.5 text-xs focus:outline-none font-mono"
                      value={formData.details.employee_id}
                      onChange={(e) => setFormData({
                        ...formData, 
                        details: { ...formData.details, employee_id: e.target.value }
                      })}
                      placeholder="ID-XXXX"
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-mono text-dim uppercase">Joining Date</label>
                  <input 
                    type="date"
                    className="w-full bg-bg-base border border-border focus:border-accent rounded px-3 py-1.5 text-xs focus:outline-none font-mono"
                    value={formData.details.joining_date}
                    onChange={(e) => setFormData({
                      ...formData, 
                      details: { ...formData.details, joining_date: e.target.value }
                    })}
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-mono text-dim uppercase">Upload Operative Details</label>
                <div 
                  className={clsx(
                    "border-2 border-dashed border-border rounded-lg p-8 flex flex-col items-center justify-center transition-all cursor-pointer hover:border-accent/50 min-h-[200px]",
                    selectedFile && "bg-accent/5 border-accent/50"
                  )}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input 
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    onChange={handleFileChange}
                    accept=".xlsx,.xls,.csv,.pdf,.png,.jpg,.jpeg"
                  />
                  {extractMutation.isPending ? (
                    <div className="text-center">
                      <Loader2 className="mx-auto text-accent mb-4 animate-spin" size={32} />
                      <div className="text-xs font-bold text-text mb-1 uppercase tracking-tight">Analyzing Data...</div>
                      <div className="text-[10px] text-muted uppercase">Extracting operative details</div>
                    </div>
                  ) : selectedFile ? (
                    <div className="text-center relative w-full">
                      <button 
                        className="absolute -top-4 -right-4 p-1 bg-bg-surface border border-border rounded-full text-dim hover:text-danger transition-colors"
                        onClick={(e) => {
                          e.stopPropagation()
                          setSelectedFile(null)
                          setExtractedData(null)
                        }}
                      >
                        <X size={14} />
                      </button>
                      <div className="mb-2 p-3 bg-accent/10 rounded-full inline-block text-accent">
                        {selectedFile.name.endsWith('.pdf') ? <FileText size={24} /> : 
                         selectedFile.name.match(/\.(xlsx|xls|csv)$/) ? <FileSpreadsheet size={24} /> : 
                         <ImageIcon size={24} />}
                      </div>
                      <div className="text-xs font-bold text-text truncate max-w-[200px] mx-auto">{selectedFile.name}</div>
                      <div className="text-[10px] text-muted">{(selectedFile.size / 1024).toFixed(1)} KB</div>
                      {extractMutation.isSuccess && (
                        <div className="mt-2 flex items-center justify-center text-[10px] text-success font-bold uppercase space-x-1">
                          <CheckCircle2 size={10} />
                          <span>AI_EXTRACTION_SUCCESSFUL</span>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-center">
                      <Upload className="mx-auto text-dim mb-4" size={32} />
                      <div className="text-xs font-bold text-muted mb-1 uppercase tracking-tight">Inject Operative Data</div>
                      <div className="text-[10px] text-dim uppercase">Excel, PDF, or Identity Images</div>
                    </div>
                  )}
                </div>
              </div>

              {extractedData && (
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-muted">
                    <Info size={12} />
                    <span className="text-[10px] font-mono uppercase">Extraction Summary</span>
                  </div>
                  <div className="max-h-[150px] overflow-y-auto border border-border rounded bg-bg-surface2/30">
                    <table className="w-full text-[10px] font-mono">
                      <thead className="bg-bg-surface sticky top-0">
                        <tr className="border-b border-border">
                          <th className="text-left p-1 text-dim uppercase">Key</th>
                          <th className="text-left p-1 text-dim uppercase">Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(extractedData).filter(([k]) => !k.startsWith('_')).map(([key, value]) => (
                          <tr key={key} className="border-b border-border/50 last:border-0">
                            <td className="p-1 text-accent font-bold">{key.replace(/_/g, ' ')}</td>
                            <td className="p-1 text-text truncate max-w-[120px]">{String(value)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              <div className="bg-bg-surface2/50 p-4 rounded border border-border">
                <div className="flex items-center space-x-2 mb-2 text-accent">
                  <ShieldAlert size={14} />
                  <span className="text-[10px] font-bold uppercase">Security Protocol</span>
                </div>
                <p className="text-[10px] text-muted leading-relaxed font-mono">
                  All uploaded documents are analyzed for authenticity. Identity verification is mandatory for operative enlistment.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-border flex space-x-3">
            <Button variant="ghost" className="w-full" onClick={handleModalClose}>ABORT_ENLISTMENT</Button>
            <Button 
              className="w-full" 
              onClick={() => createMutation.mutate(formData)}
              isLoading={createMutation.isPending}
              disabled={!formData.email || !formData.full_name}
            >
              FINALIZE_ENLISTMENT
            </Button>
          </div>
        </Modal>
      </div>
    </PageWrapper>
  )
}

export default UserList