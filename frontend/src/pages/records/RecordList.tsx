import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { getRecords, Record } from '../../api/records'
import PageWrapper from '../../components/layout/PageWrapper'
import DataTable from '../../components/shared/DataTable'
import FrozenBadge from '../../components/records/FrozenBadge'
import Button from '../../components/ui/Button'
import { Plus, Eye } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { format } from 'date-fns'

const RecordList: React.FC = () => {
  const navigate = useNavigate()
  const { data: recordsResponse, isLoading } = useQuery({
    queryKey: ['records'],
    queryFn: () => getRecords(),
  })

  const records = recordsResponse?.data || []

  const columns: ColumnDef<Record>[] = [
    {
      accessorKey: 'id',
      header: 'ID',
      cell: ({ row }) => <span className="text-accent font-bold">#{String(row.original.id).slice(0, 8)}</span>
    },
    {
      accessorKey: 'record_type',
      header: 'Data Segment',
      cell: ({ row }) => (
        <div>
          <div className="font-bold text-text uppercase">{row.original.record_type.replace(/_/g, ' ')}</div>
          <div className="text-[10px] text-muted uppercase tracking-tighter">
            v{row.original.version} · {format(new Date(row.original.created_at), 'yyyyMMdd')}
          </div>
        </div>
      )
    },
    {
      accessorKey: 'is_frozen',
      header: 'Protocol Status',
      cell: ({ row }) => (
        <FrozenBadge 
          isFrozen={row.original.is_frozen} 
        />
      )
    },
    {
      accessorKey: 'created_at',
      header: 'Last Sync',
      cell: ({ row }) => (
        <div className="text-xs">
          {format(new Date(row.original.updated_at || row.original.created_at), 'yyyy-MM-dd HH:mm')}
        </div>
      )
    },
    {
      id: 'actions',
      header: '',
      cell: ({ row }) => (
        <div className="flex justify-end">
          <Button 
            variant="secondary" 
            size="sm" 
            className="space-x-2"
            onClick={() => navigate(`/records/${row.original.id}`)}
          >
            <Eye size={14} />
            <span>ACCESS</span>
          </Button>
        </div>
      )
    }
  ]

  return (
    <PageWrapper title="Records Database">
      <div className="space-y-6">
        <div className="flex justify-between items-end">
          <div>
            <h3 className="text-2xl font-syne font-extrabold text-text uppercase tracking-tight">Mainframe Data</h3>
            <p className="text-muted font-mono text-sm">Centralized repository for all department-specific data segments.</p>
          </div>
          <Button className="space-x-2" onClick={() => navigate('/records/submit')}>
            <Plus size={18} />
            <span>SUBMIT_NEW_SEGMENT</span>
          </Button>
        </div>

        <DataTable 
          columns={columns} 
          data={records} 
          isLoading={isLoading} 
        />
      </div>
    </PageWrapper>
  )
}

export default RecordList
