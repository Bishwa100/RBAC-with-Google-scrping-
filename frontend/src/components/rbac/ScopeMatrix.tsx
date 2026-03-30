import React from 'react'
import { Scope } from '../../types'
import clsx from 'clsx'
import { Check, X, Shield } from 'lucide-react'

interface ScopeMatrixProps {
  userScopes: string[]; // formatted as "resource:action"
  allScopes: Scope[];
  onToggle?: (scopeId: string, active: boolean) => void;
  canEdit?: boolean;
}

const ScopeMatrix: React.FC<ScopeMatrixProps> = ({ 
  userScopes, 
  allScopes, 
  onToggle, 
  canEdit = false 
}) => {
  const resources = Array.from(new Set(allScopes.map(s => s.resource)))
  const actions = Array.from(new Set(allScopes.map(s => s.action)))

  const hasScope = (resource: string, action: string) => {
    return userScopes.includes(`${resource}:${action}`)
  }

  const getScopeId = (resource: string, action: string) => {
    return allScopes.find(s => s.resource === resource && s.action === action)?.id
  }

  return (
    <div className="border border-border rounded-lg bg-bg-surface overflow-hidden">
      <div className="p-4 border-b border-border bg-bg-surface2/50 flex items-center justify-between">
        <h4 className="font-syne font-bold flex items-center space-x-2">
          <Shield size={16} className="text-accent" />
          <span>SCOPE_MATRIX</span>
        </h4>
        {!canEdit && <div className="text-[10px] font-mono text-muted uppercase">Read-Only Mode</div>}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-border">
              <th className="px-4 py-3 text-[10px] font-mono font-bold text-muted uppercase tracking-widest bg-bg-surface2/30">Resource \ Action</th>
              {actions.map(action => (
                <th key={action} className="px-4 py-3 text-[10px] font-mono font-bold text-muted uppercase tracking-widest text-center">
                  {action}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border/50">
            {resources.map(resource => (
              <tr key={resource} className="hover:bg-bg-surface2/20 transition-colors">
                <td className="px-4 py-3 font-mono text-xs font-bold text-text/70 bg-bg-surface2/10">{resource}</td>
                {actions.map(action => {
                  const active = hasScope(resource, action)
                  const scopeId = getScopeId(resource, action)
                  
                  return (
                    <td key={action} className="px-4 py-3 text-center">
                      <button
                        disabled={!canEdit || !scopeId}
                        onClick={() => scopeId && onToggle?.(scopeId, active)}
                        className={clsx(
                          "w-6 h-6 rounded flex items-center justify-center transition-all mx-auto",
                          active 
                            ? "bg-success text-white shadow-[0_0_10px_rgba(79,209,142,0.3)]" 
                            : "bg-bg-surface3 text-dim border border-border/50 hover:border-accent/50",
                          canEdit && "cursor-pointer active:scale-90"
                        )}
                      >
                        {active ? <Check size={14} strokeWidth={3} /> : <X size={12} />}
                      </button>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default ScopeMatrix
