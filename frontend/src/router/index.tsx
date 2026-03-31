import { createBrowserRouter, Navigate } from 'react-router-dom'
import Login from '../pages/Login'
import ProtectedRoute from '../components/rbac/ProtectedRoute'
import PageWrapper from '../components/layout/PageWrapper'
import React from 'react'

import UserList from '../pages/users/UserList'
import UserDetail from '../pages/users/UserDetail'
import RoleManagement from '../pages/roles/RoleManagement'
import ScopeManagement from '../pages/scopes/ScopeManagement'
import DepartmentManagement from '../pages/departments/DepartmentManagement'
import RecordList from '../pages/records/RecordList'
import RecordDetail from '../pages/records/RecordDetail'
import RecordSubmit from '../pages/records/RecordSubmit'
import EditRequestListPage from '../pages/edit-requests/EditRequestList'
import Dashboard from '../pages/Dashboard'
import ActivityLogPage from '../pages/ActivityLog'
import TopicSearchPage from '../pages/TopicSearchPage'
import SharedContentPage from '../pages/SharedContentPage'

// Placeholder components
const Placeholder = ({ title }: { title: string }) => (
  <PageWrapper title={title}>
    <div className="p-8 border border-dashed border-border rounded-lg flex flex-col items-center justify-center min-h-[400px]">
      <div className="text-4xl font-syne font-extrabold text-dim mb-4 opacity-20">PENDING_IMPLEMENTATION</div>
      <p className="font-mono text-muted">Segment: {title.toUpperCase()}</p>
    </div>
  </PageWrapper>
)

const DeptDashboard = () => <Placeholder title="Department Dashboard" />
const MyProfile = () => <Placeholder title="My Profile" />

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <Navigate to="/records" replace />
      </ProtectedRoute>
    ),
  },
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute minLevel={0}>
        <Dashboard />
      </ProtectedRoute>
    ),
  },
  {
    path: '/dept-dashboard',
    element: (
      <ProtectedRoute minLevel={1}>
        <DeptDashboard />
      </ProtectedRoute>
    ),
  },
  {
    path: '/users',
    element: (
      <ProtectedRoute minLevel={2}>
        <UserList />
      </ProtectedRoute>
    ),
  },
  {
    path: '/users/:id',
    element: (
      <ProtectedRoute minLevel={2}>
        <UserDetail />
      </ProtectedRoute>
    ),
  },
  {
    path: '/roles',
    element: (
      <ProtectedRoute minLevel={0}>
        <RoleManagement />
      </ProtectedRoute>
    ),
  },
  {
    path: '/scopes',
    element: (
      <ProtectedRoute minLevel={2}>
        <ScopeManagement />
      </ProtectedRoute>
    ),
  },
  {
    path: '/departments',
    element: (
      <ProtectedRoute minLevel={0}>
        <DepartmentManagement />
      </ProtectedRoute>
    ),
  },
  {
    path: '/records',
    element: (
      <ProtectedRoute minLevel={4}>
        <RecordList />
      </ProtectedRoute>
    ),
  },
  {
    path: '/records/submit',
    element: (
      <ProtectedRoute minLevel={4}>
        <RecordSubmit />
      </ProtectedRoute>
    ),
  },
  {
    path: '/records/:id',
    element: (
      <ProtectedRoute minLevel={4}>
        <RecordDetail />
      </ProtectedRoute>
    ),
  },
  {
    path: '/edit-requests',
    element: (
      <ProtectedRoute minLevel={4}>
        <EditRequestListPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/activity',
    element: (
      <ProtectedRoute minLevel={2}>
        <ActivityLogPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/profile',
    element: (
      <ProtectedRoute minLevel={4}>
        <MyProfile />
      </ProtectedRoute>
    ),
  },
  {
    path: '/topiclens',
    element: (
      <ProtectedRoute minLevel={0}>
        <TopicSearchPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/shared-content',
    element: (
      <ProtectedRoute minLevel={4}>
        <SharedContentPage />
      </ProtectedRoute>
    ),
  },
])
