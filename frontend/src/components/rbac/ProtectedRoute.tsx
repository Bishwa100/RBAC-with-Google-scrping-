import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

interface ProtectedRouteProps {
  children: React.ReactNode;
  minLevel?: number;
  requiredScope?: string;
  fallback?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  minLevel, 
  requiredScope,
  fallback = '/records'
}) => {
  const { isAuthenticated, minRoleLevel, scopes } = useAuthStore()
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // minLevel 0 is highest authority, 4 is lowest.
  // So minRoleLevel <= minLevel means user has enough authority.
  if (minLevel !== undefined && minRoleLevel > minLevel) {
    return <Navigate to={fallback} replace />
  }

  if (requiredScope && !scopes.includes(requiredScope) && minRoleLevel !== 0) {
    return <Navigate to={fallback} replace />
  }

  return <>{children}</>
}

export default ProtectedRoute
