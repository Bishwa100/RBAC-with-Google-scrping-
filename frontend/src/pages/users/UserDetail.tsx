import React, { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getUser, getUserScopes, assignRole, removeRole, assignScope, removeScope, updateUser, getUserStats } from '../../api/users'
import { getRoles } from '../../api/roles'
import { getScopes } from '../../api/scopes'
import PageWrapper from '../../components/layout/PageWrapper'
import Button from '../../components/ui/Button'
import Badge from '../../components/ui/Badge'
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
} from 'recharts'
import { 
  ArrowLeft, 
  Shield, 
  User as UserIcon, 
  Mail, 
  Building2, 
  ShieldCheck, 
  Plus, 
  Trash2,
  Lock,
  Unlock,
  Key,
  TrendingUp,
  Database,
  FileEdit,
  Activity
} from 'lucide-react'
import { toast } from 'sonner'
import clsx from 'clsx'
import { useAuthStore } from '../../store/authStore'
import { useConfirm } from '../../components/ui/ConfirmProvider'

const UserDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { minRoleLevel } = useAuthStore()

  const { data: userResponse, isLoading: isUserLoading } = useQuery({
    queryKey: ['users', id],
    queryFn: () => getUser(id!),
    enabled: !!id,
  })

  const { data: statsResponse } = useQuery({
    queryKey: ['users', id, 'stats'],
    queryFn: () => getUserStats(id!),
    enabled: !!id,
  })
  
  const stats = statsResponse?.data

  const { data: userScopesResponse } = useQuery({
    queryKey: ['users', id, 'scopes'],
    queryFn: () => getUserScopes(id!),
    enabled: !!id,
  })

  const { data: rolesResponse } = useQuery({
    queryKey: ['roles'],
    queryFn: () => getRoles(),
    enabled: minRoleLevel <= 2,
  })

  const { data: allScopesResponse } = useQuery({
    queryKey: ['scopes'],
    queryFn: () => getScopes(),
    enabled: minRoleLevel <= 2,
  })

  const user = userResponse?.data

  const extractArray = (maybeArrayOrObj: any) => {
    if (!maybeArrayOrObj) return []
    if (Array.isArray(maybeArrayOrObj)) return maybeArrayOrObj
    if (Array.isArray(maybeArrayOrObj.data)) return maybeArrayOrObj.data
    if (Array.isArray(maybeArrayOrObj.items)) return maybeArrayOrObj.items
    if (Array.isArray(maybeArrayOrObj.results)) return maybeArrayOrObj.results
    if (typeof maybeArrayOrObj === 'object') return Object.values(maybeArrayOrObj)
    return []
  }

  const userScopes = extractArray(userScopesResponse)
  const allRoles = extractArray(rolesResponse)
  const allScopes = extractArray(allScopesResponse)

  const toggleStatusMutation = useMutation({
    mutationFn: (active: boolean) => updateUser(id!, { is_active: active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users', id] })
      toast.success('OPERATIVE_STATUS_UPDATED')
    }
  })

  const addRoleMutation = useMutation({
    mutationFn: (roleId: string) => assignRole(id!, roleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users', id] })
      toast.success('CLEARANCE_LEVEL_GRANTED')
    }
  })

  const delRoleMutation = useMutation({
    mutationFn: (roleId: string) => removeRole(id!, roleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users', id] })
      toast.success('CLEARANCE_LEVEL_REVOKED')
    }
  })

  const addScopeMutation = useMutation({
    mutationFn: (scopeId: string) => assignScope(id!, scopeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users', id, 'scopes'] })
      toast.success('SCOPE_ACCESS_GRANTED')
    }
  })

  const delScopeMutation = useMutation({
    mutationFn: (scopeId: string) => removeScope(id!, scopeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users', id, 'scopes'] })
      toast.success('SCOPE_ACCESS_REVOKED')
    }
  })

  const confirmAction = useConfirm()

  if (isUserLoading) return <PageWrapper title="Loading..."><div className="animate-pulse font-mono">ENCRYPTING_CHANNEL...</div></PageWrapper>
  if (!user) return <PageWrapper title="Error"><div className="text-danger font-mono">OPERATIVE_NOT_FOUND</div></PageWrapper>

  const availableRoles = allRoles.filter(r => !user.roles.some(ur => ur.id === r.id))
  const availableScopes = allScopes.filter(s => !userScopes.some(us => us.id === s.id))

  const requestStatusData = stats ? [
    { name: 'Approved', value: stats.approved_requests, color: '#10b981' },
    { name: 'Pending', value: stats.pending_requests, color: '#f59e0b' },
    { name: 'Rejected', value: stats.rejected_requests, color: '#ef4444' },
    { name: 'Completed', value: stats.completed_requests, color: '#3b82f6' },
  ].filter(d => d.value > 0) : []

  return (
    <PageWrapper title={`Operative: ${user.full_name}`}>
      <div className="space-y-8">
        <button 
          onClick={() => navigate('/users')}
          className="flex items-center space-x-2 text-muted hover:text-accent transition-colors font-mono text-xs uppercase"
        >
          <ArrowLeft size={14} />
          <span>Personnel Database</span>
        </button>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Operative Info */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-bg-surface border border-border rounded-lg p-6 space-y-6">
              <div className="flex flex-col items-center space-y-4 pb-6 border-b border-border">
                <div className={clsx(
                  "w-20 h-20 rounded-full flex items-center justify-center font-bold text-3xl border-4",
                  `bg-role-${Math.min(...user.roles.map(r => r.level), 4)}/10 border-role-${Math.min(...user.roles.map(r => r.level), 4)}/30 text-role-${Math.min(...user.roles.map(r => r.level), 4)}`
                )}>
                  {user.full_name.charAt(0)}
                </div>
                <div className="text-center">
                  <h4 className="text-xl font-syne font-extrabold text-text uppercase tracking-tight">{user.full_name}</h4>
                  <Badge variant={user.is_active ? 'success' : 'danger'}>
                    {user.is_active ? 'ACTIVE_DUTY' : 'SUSPENDED'}
                  </Badge>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center space-x-3 text-muted">
                  <Mail size={14} />
                  <span className="font-mono text-xs uppercase">{user.email}</span>
                </div>
                <div className="flex items-center space-x-3 text-muted">
                  <Building2 size={14} />
                  <span className="font-mono text-xs uppercase">{user.department?.name || 'NO_SECTOR_ASSIGNED'}</span>
                </div>
                <div className="flex items-center space-x-3 text-muted">
                  <Shield size={14} />
                  <span className="font-mono text-xs uppercase">ID: {user.id.slice(0, 18)}...</span>
                </div>
              </div>

              <div className="pt-4">
                <Button 
                  variant={user.is_active ? 'outline' : 'default'} 
                  className={clsx("w-full space-x-2", user.is_active && "border-danger text-danger hover:bg-danger/10")}
                  onClick={async () => {
                    const ok = await confirmAction(user.is_active ? 'Suspend this operative? This will disable their access.' : 'Reinstate this operative?')
                    if (!ok) return
                    toggleStatusMutation.mutate(!user.is_active)
                  }}
                  isLoading={toggleStatusMutation.isPending}
                >
                  {user.is_active ? (
                    <>
                      <Lock size={16} />
                      <span>SUSPEND_OPERATIVE</span>
                    </>
                  ) : (
                    <>
                      <Unlock size={16} />
                      <span>REINSTATE_OPERATIVE</span>
                    </>
                  )}
                </Button>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-bg-surface border border-border rounded-lg p-6 space-y-6">
              <h4 className="font-syne font-extrabold text-xs uppercase tracking-widest text-muted border-b border-border pb-4 flex items-center">
                <TrendingUp size={14} className="mr-2" /> DATA_INTELLIGENCE
              </h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <div className="text-[10px] font-mono text-dim uppercase">Submissions</div>
                  <div className="text-xl font-syne font-extrabold text-text tracking-tighter">{stats?.total_records || 0}</div>
                </div>
                <div className="space-y-1">
                  <div className="text-[10px] font-mono text-dim uppercase">Requests</div>
                  <div className="text-xl font-syne font-extrabold text-text tracking-tighter">{stats?.total_requests || 0}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Clearance & Scopes & Analysis */}
          <div className="lg:col-span-2 space-y-6">
            {/* Data Analysis Section */}
            <div className="bg-bg-surface border border-border rounded-lg overflow-hidden">
               <div className="p-4 border-b border-border bg-bg-surface2/50 flex items-center justify-between">
                <div className="flex items-center space-x-2 font-syne font-bold">
                  <Activity size={16} className="text-accent" />
                  <span className="text-xs uppercase">Operative Data Analysis</span>
                </div>
              </div>
              <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Activity Over Time */}
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Database className="text-muted" size={14} />
                    <h5 className="font-syne font-extrabold text-[10px] uppercase tracking-widest text-muted">Submission Flux</h5>
                  </div>
                  <div className="h-[200px] w-full">
                    {stats?.activity_over_time && stats.activity_over_time.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={stats.activity_over_time}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
                          <XAxis 
                            dataKey="date" 
                            stroke="#525252" 
                            fontSize={8} 
                            tickLine={false} 
                            axisLine={false}
                          />
                          <YAxis 
                            stroke="#525252" 
                            fontSize={8} 
                            tickLine={false} 
                            axisLine={false}
                          />
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: '#171717', 
                              borderColor: '#262626', 
                              fontSize: '10px',
                              fontFamily: 'DM Mono'
                            }}
                          />
                          <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4, fill: '#3b82f6' }} />
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-full flex items-center justify-center border border-dashed border-border rounded">
                        <span className="text-[8px] font-mono text-dim uppercase">Insufficient_Activity_Data</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Request Status Distribution */}
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <FileEdit className="text-muted" size={14} />
                    <h5 className="font-syne font-extrabold text-[10px] uppercase tracking-widest text-muted">Request Outcomes</h5>
                  </div>
                  <div className="h-[200px] w-full flex items-center justify-center">
                    {requestStatusData.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={requestStatusData}
                            cx="50%"
                            cy="50%"
                            innerRadius={40}
                            outerRadius={60}
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
                              fontSize: '10px'
                            }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-full w-full flex items-center justify-center border border-dashed border-border rounded">
                        <span className="text-[8px] font-mono text-dim uppercase">No_Request_Metrics</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Roles/Clearance */}
            <div className="bg-bg-surface border border-border rounded-lg overflow-hidden">
              <div className="p-4 border-b border-border bg-bg-surface2/50 flex items-center justify-between">
                <div className="flex items-center space-x-2 font-syne font-bold">
                  <ShieldCheck size={16} className="text-accent" />
                  <span className="text-xs uppercase">Clearance Levels</span>
                </div>
              </div>
              <div className="p-6 space-y-4">
                <div className="flex flex-wrap gap-2">
                  {user.roles.map(role => (
                    <div 
                      key={role.id}
                      className={clsx(
                        "flex items-center space-x-2 px-3 py-1.5 rounded border font-mono font-bold text-[10px]",
                        `bg-role-${role.level}/10 text-role-${role.level} border-role-${role.level}/20`
                      )}
                    >
                      <span>{role.name.toUpperCase()} (Lvl {role.level})</span>
                      {user.roles.length > 1 && (
                        <button 
                          onClick={async () => {
                            const ok = await confirmAction('Revoke this clearance level from the operative?')
                            if (!ok) return
                            delRoleMutation.mutate(role.id)
                          }}
                          className="hover:text-danger transition-colors"
                        >
                          <Trash2 size={12} />
                        </button>
                      )}
                    </div>
                  ))}
                </div>

                {minRoleLevel <= 2 && availableRoles.length > 0 && (
                  <div className="mt-6 pt-6 border-t border-border/50">
                    <label className="text-[10px] font-mono text-dim uppercase block mb-3">Grant New Clearance</label>
                    <div className="flex gap-2 flex-wrap">
                      {availableRoles.map(role => (
                        <Button 
                          key={role.id}
                          size="sm" 
                          variant="ghost" 
                          className="text-[10px] font-mono border border-border hover:border-accent"
                          onClick={() => addRoleMutation.mutate(role.id)}
                          isLoading={addRoleMutation.isPending && addRoleMutation.variables === role.id}
                        >
                          <Plus size={12} className="mr-1" /> {role.name}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Scopes */}
            <div className="bg-bg-surface border border-border rounded-lg overflow-hidden">
              <div className="p-4 border-b border-border bg-bg-surface2/50 flex items-center justify-between">
                <div className="flex items-center space-x-2 font-syne font-bold">
                  <Key size={16} className="text-accent" />
                  <span className="text-xs uppercase">Direct Scopes & Permissions</span>
                </div>
              </div>
              <div className="p-6 space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {userScopes.map(scope => (
                    <div 
                      key={scope.id}
                      className="flex items-center justify-between p-3 bg-bg-base border border-border rounded group"
                    >
                      <div className="font-mono">
                        <div className="text-[10px] font-bold text-accent">{scope.resource.toUpperCase()}</div>
                        <div className="text-xs text-text">{scope.action.toUpperCase()}</div>
                      </div>
                      <button 
                        onClick={async () => {
                          const ok = await confirmAction('Revoke this scope from the operative?')
                          if (!ok) return
                          delScopeMutation.mutate(scope.id)
                        }}
                        className="text-dim hover:text-danger opacity-0 group-hover:opacity-100 transition-all"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  ))}
                  {userScopes.length === 0 && (
                    <div className="col-span-full py-8 text-center border border-dashed border-border rounded">
                      <p className="text-[10px] font-mono text-dim uppercase">No direct scopes assigned</p>
                    </div>
                  )}
                </div>

                {minRoleLevel <= 2 && availableScopes.length > 0 && (
                  <div className="mt-6 pt-6 border-t border-border/50">
                    <label className="text-[10px] font-mono text-dim uppercase block mb-3">Inject Access Scope</label>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {availableScopes.map(scope => (
                        <button 
                          key={scope.id}
                          onClick={() => addScopeMutation.mutate(scope.id)}
                          className="p-2 border border-border rounded text-left hover:border-accent/50 hover:bg-accent/5 transition-all group"
                        >
                          <div className="text-[8px] font-mono text-dim group-hover:text-accent">{scope.resource.toUpperCase()}</div>
                          <div className="text-[10px] font-mono font-bold text-muted group-hover:text-text">{scope.action.toUpperCase()}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </PageWrapper>
  )
}

export default UserDetail
