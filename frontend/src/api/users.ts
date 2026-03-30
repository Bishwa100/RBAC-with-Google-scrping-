import api from './client'
import { ApiResponse, User } from '../types'

export const getUsers = (params?: any) => 
  api.get<any, ApiResponse<User[]>>('/api/v1/users', { params })

export const getUser = (id: string) => 
  api.get<any, ApiResponse<User>>(`/api/v1/users/${id}`)

export const getUserStats = (id: string) =>
  api.get<any, ApiResponse<any>>(`/api/v1/users/stats/${id}`)

export const createUser = (data: any, file?: File) => {
  const formData = new FormData()
  Object.keys(data).forEach(key => {
    if (data[key] !== undefined && data[key] !== null) {
      if (key === 'details') {
        formData.append('details_json', JSON.stringify(data[key]))
      } else {
        formData.append(key, data[key])
      }
    }
  })
  if (file) {
    formData.append('file', file)
  }
  return api.post<any, ApiResponse<User>>('/api/v1/users', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const extractUserInfo = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post<any, ApiResponse<any>>('/api/v1/users/extract', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const analyzeUserFile = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post<any, ApiResponse<any>>('/api/v1/users/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const updateUser = (id: string, data: any) => 
  api.patch<any, ApiResponse<User>>(`/api/v1/users/${id}`, data)

export const deleteUser = (id: string) => 
  api.delete(`/api/v1/users/${id}`)

export const uploadUsers = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post<any, ApiResponse<any>>('/api/v1/users/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const assignRole = (userId: string, roleId: string) =>
  api.post(`/api/v1/users/${userId}/roles?role_id=${roleId}`)

export const removeRole = (userId: string, roleId: string) =>
  api.delete(`/api/v1/users/${userId}/roles/${roleId}`)

export const getUserScopes = (userId: string) =>
  api.get<any, ApiResponse<any[]>>(`/api/v1/users/${userId}/scopes`)

export const assignScope = (userId: string, scopeId: string) =>
  api.post(`/api/v1/users/${userId}/scopes?scope_id=${scopeId}`)

export const removeScope = (userId: string, scopeId: string) =>
  api.delete(`/api/v1/users/${userId}/scopes/${scopeId}`)
