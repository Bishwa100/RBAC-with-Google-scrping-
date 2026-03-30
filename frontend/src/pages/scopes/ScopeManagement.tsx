import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getScopes } from '../../api/scopes'
import api from '../../api/client'
import PageWrapper from '../../components/layout/PageWrapper'
import Button from '../../components/ui/Button'
import DataTable from '../../components/shared/DataTable'
import { ColumnDef } from '@tanstack/react-table'
import { Scope, ApiResponse } from '../../types'
import { 
  Key, 
  Plus, 
  Trash2, 
  Tag,
  Activity,
  FileText
} from 'lucide-react'
import { toast } from 'sonner'

const ScopeManagement: React.FC = () => {
  const queryClient = useQueryClient()
  const [isCreating, setIsCreating] = useState(false)
  const [formData, setFormData] = useState({
    resource: '',
    action: '',
    description: ''
  })

  const { data: scopesResponse, isLoading: isScopesLoading } = useQuery({
    queryKey: ['scopes'],
    queryFn: () => getScopes(),
  })

  const scopes = scopesResponse?.data || []

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post<any, ApiResponse<Scope>>('/api/v1/scopes', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scopes'] })
      setIsCreating(false)
      setFormData({ resource: '', action: '', description: '' })
      toast.success('SCOPE_PROTOCOL_ESTABLISHED')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'ESTABLISHMENT_FAILED')
    }
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/api/v1/scopes/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scopes'] })
      toast.success('SCOPE_DECOMMISSIONED')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'DECOMMISSION_FAILED')
    }
  })

  const columns: ColumnDef<Scope>[] = [
    {
      accessorKey: 'resource',
      header: 'Resource',
      cell: ({ row }) => (
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded bg-accent/10 border border-accent/20 flex items-center justify-center text-accent">
            <Tag size={16} />
          </div>
          <div className="font-mono font-bold text-text uppercase tracking-tight">{row.original.resource}</div>
        </div>
      )
    },
    {
      accessorKey: 'action',
      header: 'Action',
      cell: ({ row }) => (
        <div className="flex items-center space-x-2">
          <Activity size={14} className="text-muted" />
          <div className="font-mono text-xs font-bold text-accent uppercase">{row.original.action}</div>
        </div>
      )
    },
    {
      accessorKey: 'description',
      header: 'Protocol Description',
      cell: ({ row }) => (
        <span className="text-xs text-muted italic line-clamp-1 max-w-xs">
          {row.original.description || 'No protocol description defined.'}
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
            onClick={() => {
              if (window.confirm('IRREVERSIBLE_ACTION: Decommissioning a scope will revoke access for all associated operatives. Proceed?')) {
                deleteMutation.mutate(row.original.id as any)
              }
            }}
          >
            <Trash2 size={16} />
          </Button>
        </div>
      )
    }
  ]

  return (
    <PageWrapper title="Scope Management">
      <div className="space-y-8">
        <div className="flex justify-between items-end">
          <div>
            <h3 className="text-2xl font-syne font-extrabold text-text uppercase tracking-tight">Access Scopes</h3>
            <p className="text-muted font-mono text-sm">Define and manage granular access permissions for system resources.</p>
          </div>
          {!isCreating && (
            <Button className="space-x-2" onClick={() => setIsCreating(true)}>
              <Plus size={18} />
              <span>ESTABLISH_NEW_SCOPE</span>
            </Button>
          )}
        </div>

        {isCreating && (
          <div className="bg-bg-surface border border-accent/30 rounded-lg p-6 space-y-6 animate-in fade-in slide-in-from-top-4">
            <div className="flex items-center space-x-2 border-b border-border pb-4 mb-4">
              <Key className="text-accent" size={20} />
              <h4 className="font-syne font-extrabold text-xs uppercase tracking-widest text-accent">Scope Definition Protocol</h4>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1">
                <label className="text-[10px] font-mono text-dim uppercase flex items-center">
                  <Tag size={10} className="mr-1" /> Resource Name
                </label>
                <input
                  type="text"
                  value={formData.resource}
                  onChange={(e) => setFormData({ ...formData, resource: e.target.value.toLowerCase() })}
                  placeholder="e.g. records"
                  className="w-full bg-bg-base border border-border focus:border-accent rounded px-4 py-2 font-mono text-sm focus:outline-none transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-mono text-dim uppercase flex items-center">
                  <Activity size={10} className="mr-1" /> Action
                </label>
                <input
                  type="text"
                  value={formData.action}
                  onChange={(e) => setFormData({ ...formData, action: e.target.value.toLowerCase() })}
                  placeholder="e.g. approve"
                  className="w-full bg-bg-base border border-border focus:border-accent rounded px-4 py-2 font-mono text-sm focus:outline-none transition-all"
                />
              </div>

              <div className="space-y-1 md:col-span-2">
                <label className="text-[10px] font-mono text-dim uppercase flex items-center">
                  <FileText size={10} className="mr-1" /> Protocol Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Define scope responsibilities and access constraints..."
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
                disabled={!formData.resource || !formData.action}
              >
                CONFIRM_SCOPE_ESTABLISHMENT
              </Button>
            </div>
          </div>
        )}

        <DataTable 
          columns={columns} 
          data={scopes} 
          isLoading={isScopesLoading} 
        />
      </div>
    </PageWrapper>
  )
}

export default ScopeManagement
