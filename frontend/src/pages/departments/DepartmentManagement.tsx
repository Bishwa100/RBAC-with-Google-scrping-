import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getDepartments } from '../../api/departments'
import api from '../../api/client'
import PageWrapper from '../../components/layout/PageWrapper'
import Button from '../../components/ui/Button'
import DataTable from '../../components/shared/DataTable'
import Badge from '../../components/ui/Badge'
import { ColumnDef } from '@tanstack/react-table'
import { Department, ApiResponse } from '../../types'
import { 
  Building2, 
  Plus, 
  Trash2, 
  Hash,
  FileText
} from 'lucide-react'
import { toast } from 'sonner'
import { useConfirm } from '../../components/ui/ConfirmProvider'

const DepartmentManagement: React.FC = () => {
  const queryClient = useQueryClient()
  const [isCreating, setIsCreating] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    description: ''
  })

  const { data: deptsResponse, isLoading: isDeptsLoading } = useQuery({
    queryKey: ['departments'],
    queryFn: () => getDepartments(),
  })

  const departments = deptsResponse?.data || []

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post<any, ApiResponse<Department>>('/api/v1/departments', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] })
      setIsCreating(false)
      setFormData({ name: '', code: '', description: '' })
      toast.success('SECTOR_ESTABLISHED')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'ESTABLISHMENT_FAILED')
    }
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/api/v1/departments/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] })
      toast.success('SECTOR_DECOMMISSIONED')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'DECOMMISSION_FAILED')
    }
  })

  const confirmAction = useConfirm()

  const columns: ColumnDef<Department>[] = [
    {
      accessorKey: 'name',
      header: 'Sector Name',
      cell: ({ row }) => (
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded bg-accent/10 border border-accent/20 flex items-center justify-center text-accent">
            <Building2 size={16} />
          </div>
          <div className="font-bold text-text uppercase tracking-tight">{row.original.name}</div>
        </div>
      )
    },
    {
      accessorKey: 'code',
      header: 'System Code',
      cell: ({ row }) => (
        <Badge variant="muted" className="font-mono">
          {(row.original as any).code || 'NO_CODE'}
        </Badge>
      )
    },
    {
      accessorKey: 'description',
      header: 'Operational mandate',
      cell: ({ row }) => (
        <span className="text-xs text-muted italic line-clamp-1 max-w-xs">
          {row.original.description || 'No operational mandate defined.'}
        </span>
      )
    },
    {
      id: 'actions',
      header: '',
      cell: ({ row }) => (
        <div className="flex justify-end">
          <Button 
            variant="ghost" 
            size="icon"
            className="text-muted hover:text-danger"
            onClick={async () => {
              const ok = await confirmAction('IRREVERSIBLE_ACTION: Decommissioning a sector will impact all associated personnel and clearances. Proceed?')
              if (!ok) return
              deleteMutation.mutate(row.original.id as any)
            }}
          >
            <Trash2 size={16} />
          </Button>
        </div>
      )
    }
  ]

  return (
    <PageWrapper title="Department Management">
      <div className="space-y-8">
        <div className="flex justify-between items-end">
          <div>
            <h3 className="text-2xl font-syne font-extrabold text-text uppercase tracking-tight">Sector Infrastructure</h3>
            <p className="text-muted font-mono text-sm">Configure and manage operational sectors and organizational units.</p>
          </div>
          {!isCreating && (
            <Button className="space-x-2" onClick={() => setIsCreating(true)}>
              <Plus size={18} />
              <span>ESTABLISH_NEW_SECTOR</span>
            </Button>
          )}
        </div>

        {isCreating && (
          <div className="bg-bg-surface border border-accent/30 rounded-lg p-6 space-y-6 animate-in fade-in slide-in-from-top-4">
            <div className="flex items-center space-x-2 border-b border-border pb-4 mb-4">
              <Building2 className="text-accent" size={20} />
              <h4 className="font-syne font-extrabold text-xs uppercase tracking-widest text-accent">Sector Definition Protocol</h4>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1">
                <label className="text-[10px] font-mono text-dim uppercase flex items-center">
                  <Building2 size={10} className="mr-1" /> Sector Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. INTELLIGENCE_UNIT"
                  className="w-full bg-bg-base border border-border focus:border-accent rounded px-4 py-2 font-mono text-sm focus:outline-none transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-mono text-dim uppercase flex items-center">
                  <Hash size={10} className="mr-1" /> System Code
                </label>
                <input
                  type="text"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                  placeholder="e.g. IU-01"
                  className="w-full bg-bg-base border border-border focus:border-accent rounded px-4 py-2 font-mono text-sm focus:outline-none transition-all"
                />
              </div>

              <div className="space-y-1 md:col-span-2">
                <label className="text-[10px] font-mono text-dim uppercase flex items-center">
                  <FileText size={10} className="mr-1" /> Operational Mandate
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Define sector responsibilities and strategic objectives..."
                  className="w-full h-24 bg-bg-base border border-border focus:border-accent rounded px-4 py-2 font-mono text-sm focus:outline-none transition-all resize-none"
                />
              </div>
            </div>

            <div className="flex space-x-3 pt-4 border-t border-border">
              <Button variant="ghost" className="w-full" onClick={() => setIsCreating(false)}>CANCEL_ESTABLISHMENT</Button>
              <Button 
                className="w-full" 
                onClick={() => createMutation.mutate(formData)}
                isLoading={createMutation.isPending}
                disabled={!formData.name || !formData.code}
              >
                CONFIRM_SECTOR_ESTABLISHMENT
              </Button>
            </div>
          </div>
        )}

        <DataTable 
          columns={columns} 
          data={departments} 
          isLoading={isDeptsLoading} 
        />
      </div>
    </PageWrapper>
  )
}

export default DepartmentManagement
