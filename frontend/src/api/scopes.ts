import api from './client'
import { ApiResponse, Scope } from '../types'

export const getScopes = () => 
  api.get<any, ApiResponse<Scope[]>>('/api/v1/scopes')

export const getScope = (id: string) => 
  api.get<any, ApiResponse<Scope>>(`/api/v1/scopes/${id}`)
