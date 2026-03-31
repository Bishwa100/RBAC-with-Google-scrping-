import React from 'react'
import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Database, 
  FileEdit, 
  Users, 
  Shield, 
  Key, 
  Building2, 
  LogOut,
  User,
  History,
  Search,
  Share2
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import clsx from 'clsx'

const Sidebar: React.FC = () => {
  const { user, minRoleLevel, logout } = useAuthStore()

  // Check if user is root/admin
  const isRootUser = user?.roles?.some(
    role => role.name.toLowerCase() === 'root' || 
            role.name.toLowerCase() === 'admin' || 
            role.level === 0
  ) || minRoleLevel === 0

  const navItems = [
    { 
      label: 'Dashboard', 
      to: '/dashboard', 
      icon: LayoutDashboard, 
      minLevel: 1 
    },
    { 
      label: 'Records', 
      to: '/records', 
      icon: Database, 
      minLevel: 4 
    },
    { 
      label: 'Edit Requests', 
      to: '/edit-requests', 
      icon: FileEdit, 
      minLevel: 4 
    },
    { 
      label: 'Users', 
      to: '/users', 
      icon: Users, 
      minLevel: 2 
    },
    { 
      label: 'Roles', 
      to: '/roles', 
      icon: Shield, 
      minLevel: 0 
    },
    { 
      label: 'Scopes', 
      to: '/scopes', 
      icon: Key, 
      minLevel: 2 
    },
    { 
      label: 'Departments', 
      to: '/departments', 
      icon: Building2, 
      minLevel: 0 
    },
    { 
      label: 'Activity Log', 
      to: '/activity', 
      icon: History, 
      minLevel: 2 
    },
  ]

  // TopicLens navigation items
  const topiclensItems = [
    ...(isRootUser ? [{
      label: 'TopicLens Search',
      to: '/topiclens',
      icon: Search,
      minLevel: 0
    }] : []),
    {
      label: 'Shared Content',
      to: '/shared-content',
      icon: Share2,
      minLevel: 4
    }
  ]

  const filteredNavItems = navItems.filter(item => minRoleLevel <= item.minLevel)

  return (
    <aside className="w-64 bg-bg-surface border-r border-border flex flex-col h-screen">
      <div className="p-6 border-b border-border">
        <h1 className="text-xl font-syne font-extrabold text-accent">RBAC CONTROL</h1>
        <div className="text-[10px] font-mono text-muted mt-1 uppercase tracking-widest">
          Mission Control v1.0
        </div>
      </div>

      <div className="p-4 border-b border-border flex items-center space-x-3">
        <div className={clsx(
          "w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg",
          `bg-role-${minRoleLevel}`
        )}>
          {user?.full_name?.charAt(0) || 'U'}
        </div>
        <div className="min-w-0">
          <div className="text-sm font-bold truncate">{user?.full_name}</div>
          <div className={clsx(
            "text-[10px] font-mono font-bold px-1.5 py-0.5 rounded inline-block",
            `bg-role-${minRoleLevel}/10 text-role-${minRoleLevel}`
          )}>
            LEVEL {minRoleLevel}
          </div>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto p-4 space-y-2">
        {filteredNavItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => clsx(
              "flex items-center space-x-3 px-3 py-2 rounded-md transition-colors font-syne font-bold",
              isActive 
                ? "bg-accent/10 text-accent" 
                : "text-muted hover:bg-bg-surface2 hover:text-text"
            )}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </NavLink>
        ))}

        {/* TopicLens Section Divider */}
        {topiclensItems.length > 0 && (
          <>
            <div className="pt-4 pb-2">
              <div className="text-[10px] font-mono text-muted uppercase tracking-widest px-3">
                TopicLens
              </div>
            </div>
            {topiclensItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => clsx(
                  "flex items-center space-x-3 px-3 py-2 rounded-md transition-colors font-syne font-bold",
                  isActive 
                    ? "bg-accent/10 text-accent" 
                    : "text-muted hover:bg-bg-surface2 hover:text-text"
                )}
              >
                <item.icon size={20} />
                <span>{item.label}</span>
              </NavLink>
            ))}
          </>
        )}
      </nav>

      <div className="p-4 border-t border-border space-y-2">
        <NavLink
          to="/profile"
          className={({ isActive }) => clsx(
            "flex items-center space-x-3 px-3 py-2 rounded-md transition-colors font-syne font-bold",
            isActive 
              ? "bg-accent/10 text-accent" 
              : "text-muted hover:bg-bg-surface2 hover:text-text"
          )}
        >
          <User size={20} />
          <span>My Profile</span>
        </NavLink>
        <button
          onClick={logout}
          className="w-full flex items-center space-x-3 px-3 py-2 rounded-md transition-colors font-syne font-bold text-danger hover:bg-danger/10"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
