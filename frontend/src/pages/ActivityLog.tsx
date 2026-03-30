import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { getAuditLogs } from '../api/audit'
import PageWrapper from '../components/layout/PageWrapper'
import DataTable from '../components/shared/DataTable'
import { ColumnDef } from '@tanstack/react-table'
import { AuditLog } from '../api/audit'
import Badge from '../components/ui/Badge'
import { 
  Activity, 
  User, 
  Terminal, 
  Globe, 
  Clock,
  ShieldAlert
} from 'lucide-react'
import { format } from 'date-fns'
import clsx from 'clsx'

const ActivityLogPage: React.FC = () => {
  const { data: logsResponse, isLoading } = useQuery({
    queryKey: ['audit-logs'],
    queryFn: () => getAuditLogs(),
  })

  const logs = logsResponse?.data || []

  const columns: ColumnDef<AuditLog>[] = [
    {
      accessorKey: 'created_at',
      header: 'Timestamp',
      cell: ({ row }) => (
        <div className="flex items-center space-x-2 font-mono text-[10px] text-muted">
          <Clock size={12} />
          <span>{format(new Date(row.original.created_at), 'yyyy-MM-dd HH:mm:ss')}</span>
        </div>
      )
    },
    {
      accessorKey: 'user_email',
      header: 'Operator',
      cell: ({ row }) => (
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 rounded-full bg-bg-surface2 flex items-center justify-center text-muted">
            <User size={12} />
          </div>
          <span className="font-mono text-[10px] font-bold text-text uppercase tracking-tight">
            {row.original.user_email}
          </span>
        </div>
      )
    },
    {
      accessorKey: 'action',
      header: 'System Action',
      cell: ({ row }) => {
        const action = row.original.action.toUpperCase()
        const isCritical = action.includes('DELETE') || action.includes('REVOKE') || action.includes('DECOMMISSION')
        return (
          <div className="flex items-center space-x-2">
             <div className={clsx(
               "px-2 py-0.5 rounded text-[10px] font-mono font-bold border",
               isCritical ? "bg-danger/10 text-danger border-danger/20" : "bg-accent/10 text-accent border-accent/20"
             )}>
               {action}
             </div>
          </div>
        )
      }
    },
    {
      accessorKey: 'resource',
      header: 'Resource',
      cell: ({ row }) => (
        <div className="flex items-center space-x-1 font-mono text-[10px]">
          <span className="text-muted">{row.original.resource || 'SYSTEM'}</span>
          {row.original.resource_id && (
            <span className="text-dim">::{row.original.resource_id.slice(0, 8)}</span>
          )}
        </div>
      )
    },
    {
      accessorKey: 'dept_name',
      header: 'Sector Context',
      cell: ({ row }) => (
        <Badge variant="muted" className="text-[10px]">
          {row.original.dept_name}
        </Badge>
      )
    },
    {
      accessorKey: 'ip_address',
      header: 'Source IP',
      cell: ({ row }) => (
        <div className="flex items-center space-x-1 font-mono text-[10px] text-dim">
          <Globe size={10} />
          <span>{row.original.ip_address || '0.0.0.0'}</span>
        </div>
      )
    }
  ]

  return (
    <PageWrapper title="Audit Trails">
      <div className="space-y-6">
        <div className="flex justify-between items-end">
          <div>
            <h3 className="text-2xl font-syne font-extrabold text-text uppercase tracking-tight">Surveillance Logs</h3>
            <p className="text-muted font-mono text-sm">Immutable ledger of system actions and operator interventions.</p>
          </div>
          <div className="flex items-center space-x-2 text-[10px] font-mono text-danger bg-danger/5 border border-danger/20 px-3 py-1 rounded uppercase tracking-widest">
            <ShieldAlert size={12} className="animate-pulse" />
            <span>Active_Monitoring_Engaged</span>
          </div>
        </div>

        <div className="bg-bg-surface border border-border rounded-lg overflow-hidden">
          <div className="p-4 border-b border-border bg-bg-surface2/30 flex items-center space-x-2">
            <Terminal size={16} className="text-accent" />
            <span className="text-[10px] font-mono font-bold uppercase tracking-widest">System_Event_Stream</span>
          </div>
          <DataTable 
            columns={columns} 
            data={logs} 
            isLoading={isLoading} 
          />
        </div>
      </div>
    </PageWrapper>
  )
}

export default ActivityLogPage
