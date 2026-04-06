import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getRoles } from '../../api/roles'
import { getDepartments } from '../../api/departments'
import api from '../../api/client'
import PageWrapper from '../../components/layout/PageWrapper'
import Button from '../../components/ui/Button'
import DataTable from '../../components/shared/DataTable'
import Badge from '../../components/ui/Badge'
import { ColumnDef } from '@tanstack/react-table'
import { Role, Department, ApiResponse } from '../../types'
import { 
  Shield, 
  Plus, 
  Trash2, 
  AlertTriangle,
  Layers,
  Building2,
  FileText
} from 'lucide-react'
import { toast } from 'sonner'
import clsx from 'clsx'
import { useConfirm } from '../../components/ui/ConfirmProvider'

const RoleManagement: React.FC = () => {
  const queryClient = useQueryClient()
  const confirmAction = useConfirm()
  const [isCreating, setIsCreating] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    level: 4,
    dept_id: '',
    description: ''
  })

  const { data: rolesResponse, isLoading: isRolesLoading } = useQuery({
    queryKey: ['roles'],
    queryFn: () => getRoles(),
  })

  const { data: deptsResponse } = useQuery({
    queryKey: ['departments'],
    queryFn: () => getDepartments(),
  })

  const roles = rolesResponse?.data || []
  const departments = deptsResponse?.data || []

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post<any, ApiResponse<Role>>('/api/v1/roles', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] })
      setIsCreating(false)
      setFormData({ name: '', level: 4, dept_id: '', description: '' })
      toast.success('CLEARANCE_STRATUM_ENACTED')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'ENACTMENT_FAILED')
    }
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/api/v1/roles/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] })
      toast.success('CLEARANCE_STRATUM_DECOMMISSIONED')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'DECOMMISSION_FAILED')
    }
  })

  const columns: ColumnDef<Role>[] = [
    {
      accessorKey: 'name',
      header: 'Designation',
      cell: ({ row }) => (
        <div className="flex items-center space-x-3">
          <div className={clsx(
            "w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs border",
            `bg-role-${row.original.level}/10 border-role-${row.original.level}/30 text-role-${row.original.level}`
          )}>
            <Shield size={14} />
          </div>
          <div>
            <div className="font-bold text-text uppercase tracking-tight">{row.original.name}</div>
            <div className="text-[10px] text-muted font-mono">LVL_{row.original.level}</div>
          </div>
        </div>
      )
    },
    {
      accessorKey: 'dept_id',
      header: 'Department Context',
      cell: ({ row }) => {
        const dept = departments.find(d => d.id === (row.original as any).dept_id)
        return (
          <Badge variant="muted">
            {dept?.name || 'GLOBAL_PROTOCOL'}
          </Badge>
        )
      }
    },
    {
      accessorKey: 'description',
      header: 'Operational Scope',
      cell: ({ row }) => (
        <span className="text-xs text-muted italic line-clamp-1 max-w-xs">
          {row.original.description || 'No operational description provided.'}
        </span>
      )
    },
    {
      id: 'actions',
      header: '',
      cell: ({ row }) => (
        <div className="flex justify-end">
          {row.original.level !== 0 && (
            <Button 
              variant="ghost" 
              size="icon"
              className="text-muted hover:text-danger"
              onClick={async () => {
                const ok = await confirmAction('IRREVERSIBLE_ACTION: Are you sure you want to delete this clearance stratum?')
                if (!ok) return
                deleteMutation.mutate(row.original.id as any)
              }}
            >
              <Trash2 size={16} />
            </Button>
          )}
        </div>
      )
    }
  ]

  return (
    <PageWrapper title="Role Management">
      <div className="space-y-8">
        <div className="flex justify-between items-end">
          <div>
            <h3 className="text-2xl font-syne font-extrabold text-text uppercase tracking-tight">Clearance Stratification</h3>
            <p className="text-muted font-mono text-sm">Define and manage operational hierarchy and permission layers.</p>
          </div>
          {!isCreating && (
            <Button className="space-x-2" onClick={() => setIsCreating(true)}>
              <Plus size={18} />
              <span>ENACT_NEW_STRATUM</span>
            </Button>
          )}
        </div>

        {isCreating && (
          <div className="bg-bg-surface border border-accent/30 rounded-lg p-6 space-y-6 animate-in fade-in slide-in-from-top-4">
            <div className="flex items-center space-x-2 border-b border-border pb-4 mb-4">
              <Shield className="text-accent" size={20} />
              <h4 className="font-syne font-extrabold text-xs uppercase tracking-widest text-accent">Clearance Stratum Definition</h4>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1">
                <label className="text-[10px] font-mono text-dim uppercase flex items-center">
                  <FileText size={10} className="mr-1" /> Designation Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. SENIOR_ANALYST"
                  className="w-full bg-bg-base border border-border focus:border-accent rounded px-4 py-2 font-mono text-sm focus:outline-none transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-mono text-dim uppercase flex items-center">
                  <Layers size={10} className="mr-1" /> Clearance Level (0-4)
                </label>
                <select
                  value={formData.level}
                  onChange={(e) => setFormData({ ...formData, level: parseInt(e.target.value) })}
                  className="w-full bg-bg-base border border-border focus:border-accent rounded px-4 py-2 font-mono text-sm focus:outline-none transition-all"
                >
                  {[0, 1, 2, 3, 4].map(lvl => (
                    <option key={lvl} value={lvl}>LEVEL_{lvl} {lvl === 0 ? '(ROOT)' : lvl === 1 ? '(MANAGER)' : lvl === 4 ? '(WORKER)' : ''}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-mono text-dim uppercase flex items-center">
                  <Building2 size={10} className="mr-1" /> Department Context
                </label>
                <select
                  value={formData.dept_id}
                  onChange={(e) => setFormData({ ...formData, dept_id: e.target.value })}
                  className="w-full bg-bg-base border border-border focus:border-accent rounded px-4 py-2 font-mono text-sm focus:outline-none transition-all"
                >
                  <option value="">GLOBAL_PROTOCOL (No Department)</option>
                  {departments.map(dept => (
                    <option key={dept.id} value={dept.id}>{dept.name}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-1 md:col-span-2">
                <label className="text-[10px] font-mono text-dim uppercase flex items-center">
                  <AlertTriangle size={10} className="mr-1" /> Stratum Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Define operational responsibilities and scope constraints..."
                  className="w-full h-24 bg-bg-base border border-border focus:border-accent rounded px-4 py-2 font-mono text-sm focus:outline-none transition-all resize-none"
                />
              </div>
            </div>

            <div className="flex space-x-3 pt-4 border-t border-border">
              <Button variant="ghost" className="w-full" onClick={() => setIsCreating(false)}>CANCEL_ENACTMENT</Button>
              <Button 
                className="w-full" 
                onClick={() => createMutation.mutate(formData)}
                isLoading={createMutation.isPending}
                disabled={!formData.name}
              >
                CONFIRM_STRATUM_ENACTMENT
              </Button>
            </div>
          </div>
        )}

        <DataTable 
          columns={columns} 
          data={roles} 
          isLoading={isRolesLoading} 
        />
      </div>
    </PageWrapper>
  )
}

export default RoleManagement
