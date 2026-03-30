import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { getRecords } from '../api/records'
import { getUsers } from '../api/users'
import { getDepartments } from '../api/departments'
import { getEditRequests } from '../api/editRequests'
import PageWrapper from '../components/layout/PageWrapper'
import { 
  Database, 
  Users, 
  FileEdit, 
  Building2, 
  TrendingUp, 
  AlertCircle,
  Clock,
  CheckCircle2
} from 'lucide-react'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell,
  LineChart,
  Line,
  Legend
} from 'recharts'
import clsx from 'clsx'

const Dashboard: React.FC = () => {
  const { data: recordsRes } = useQuery({ queryKey: ['records'], queryFn: () => getRecords() })
  const { data: usersRes } = useQuery({ queryKey: ['users'], queryFn: () => getUsers() })
  const { data: deptsRes } = useQuery({ queryKey: ['departments'], queryFn: () => getDepartments() })
  const { data: requestsRes } = useQuery({ queryKey: ['edit-requests'], queryFn: () => getEditRequests() })

  const records = recordsRes?.data || []
  const users = usersRes?.data || []
  const departments = deptsRes?.data || []
  const requests = requestsRes?.data || []

  const pendingRequests = requests.filter(r => r.status === 'pending')
  
  // Data for Records by Department
  const recordsByDept = departments.map(dept => ({
    name: dept.name,
    count: records.filter(r => r.dept_id === dept.id).length
  }))

  // Data for Request Status
  const requestStatusData = [
    { name: 'Approved', value: requests.filter(r => r.status === 'approved').length, color: '#10b981' },
    { name: 'Pending', value: requests.filter(r => r.status === 'pending').length, color: '#f59e0b' },
    { name: 'Rejected', value: requests.filter(r => r.status === 'rejected').length, color: '#ef4444' },
    { name: 'Expired', value: requests.filter(r => r.status === 'expired').length, color: '#6b7280' },
  ].filter(d => d.value > 0)

  const stats = [
    { 
      label: 'Total Records', 
      value: records.length, 
      icon: Database, 
      color: 'text-accent',
      bg: 'bg-accent/10'
    },
    { 
      label: 'Active Personnel', 
      value: users.length, 
      icon: Users, 
      color: 'text-role-2',
      bg: 'bg-role-2/10'
    },
    { 
      label: 'Pending Approvals', 
      value: pendingRequests.length, 
      icon: FileEdit, 
      color: 'text-role-1',
      bg: 'bg-role-1/10'
    },
    { 
      label: 'Operational Sectors', 
      value: departments.length, 
      icon: Building2, 
      color: 'text-role-0',
      bg: 'bg-role-0/10'
    },
  ]

  return (
    <PageWrapper title="System Overview">
      <div className="space-y-8 pb-12">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h3 className="text-3xl font-syne font-extrabold text-text uppercase tracking-tight">Root Intelligence</h3>
            <p className="text-muted font-mono text-sm">Real-time surveillance of system nodes and operational flux.</p>
          </div>
          <div className="flex items-center space-x-2 text-[10px] font-mono text-accent bg-accent/5 border border-accent/20 px-3 py-1 rounded-full uppercase tracking-widest">
            <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
            <span>Link_Established // Live_Data_Feed</span>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat, i) => (
            <div key={i} className="bg-bg-surface border border-border p-6 rounded-lg group hover:border-accent/30 transition-all duration-300">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-[10px] font-mono text-dim uppercase mb-1">{stat.label}</p>
                  <h4 className="text-3xl font-syne font-extrabold text-text tracking-tighter">{stat.value}</h4>
                </div>
                <div className={clsx("p-2 rounded-md", stat.bg, stat.color)}>
                  <stat.icon size={20} />
                </div>
              </div>
              <div className="mt-4 flex items-center text-[10px] font-mono text-success">
                <TrendingUp size={10} className="mr-1" />
                <span>+0.0% SIGNAL_STRENGTH</span>
              </div>
            </div>
          ))}
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Records by Sector */}
          <div className="bg-bg-surface border border-border rounded-lg p-6">
            <div className="flex items-center space-x-2 mb-8">
              <Database className="text-accent" size={18} />
              <h5 className="font-syne font-extrabold text-xs uppercase tracking-widest text-text">Sector Distribution</h5>
            </div>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={recordsByDept}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
                  <XAxis 
                    dataKey="name" 
                    stroke="#525252" 
                    fontSize={10} 
                    tickLine={false} 
                    axisLine={false}
                    tick={{ fill: '#737373', fontWeight: 'bold' }}
                  />
                  <YAxis 
                    stroke="#525252" 
                    fontSize={10} 
                    tickLine={false} 
                    axisLine={false}
                    tick={{ fill: '#737373' }}
                  />
                  <Tooltip 
                    cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                    contentStyle={{ 
                      backgroundColor: '#171717', 
                      borderColor: '#262626', 
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontFamily: 'DM Mono'
                    }}
                  />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={40} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Request Status */}
          <div className="bg-bg-surface border border-border rounded-lg p-6">
            <div className="flex items-center space-x-2 mb-8">
              <FileEdit className="text-accent" size={18} />
              <h5 className="font-syne font-extrabold text-xs uppercase tracking-widest text-text">Approval Workflow Status</h5>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="h-[250px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={requestStatusData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {requestStatusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#171717', 
                        borderColor: '#262626', 
                        borderRadius: '4px',
                        fontSize: '12px'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-col justify-center space-y-4">
                {requestStatusData.map((item, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-[10px] font-mono text-muted uppercase font-bold">{item.name}</span>
                    </div>
                    <span className="text-xs font-mono font-bold">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Recent Pending Requests */}
        <div className="bg-bg-surface border border-border rounded-lg overflow-hidden">
          <div className="p-4 border-b border-border bg-bg-surface2/50 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <AlertCircle size={16} className="text-role-1" />
              <h5 className="font-syne font-extrabold text-xs uppercase tracking-widest text-text">Critical Pending Actions</h5>
            </div>
            <span className="text-[10px] font-mono text-dim">{pendingRequests.length} ACTIONABLE_ITEMS</span>
          </div>
          <div className="divide-y divide-border">
            {pendingRequests.slice(0, 5).map((req, i) => (
              <div key={i} className="p-4 flex items-center justify-between hover:bg-bg-base/50 transition-colors">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 rounded bg-role-1/10 flex items-center justify-center text-role-1">
                    <Clock size={18} />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-text uppercase">Request_{req.id.slice(0, 8)}</div>
                    <div className="text-[10px] text-muted font-mono truncate max-w-[200px]">{req.reason}</div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right hidden sm:block">
                    <div className="text-[10px] font-mono text-dim">CLEARANCE_LEVEL_REQUIRED</div>
                    <div className="text-xs font-bold text-role-1">LEVEL_{req.steps.find(s => s.decision === null)?.required_min_role_level || 'N/A'}</div>
                  </div>
                  <div className="px-2 py-1 bg-role-1/10 border border-role-1/20 text-role-1 text-[8px] font-mono font-bold rounded uppercase">
                    Awaiting_Decision
                  </div>
                </div>
              </div>
            ))}
            {pendingRequests.length === 0 && (
              <div className="p-12 text-center">
                <CheckCircle2 size={32} className="mx-auto text-success/30 mb-4" />
                <p className="text-[10px] font-mono text-dim uppercase">All systems nominal // No pending approvals</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </PageWrapper>
  )
}

export default Dashboard
