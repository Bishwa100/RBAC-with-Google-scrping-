import api from './client'
import { ApiResponse, Role } from '../types'

export const getRoles = () => 
  api.get<any, ApiResponse<Role[]>>('/api/v1/roles')

export const getRole = (id: string) => 
  api.get<any, ApiResponse<Role>>(`/api/v1/roles/${id}`)
