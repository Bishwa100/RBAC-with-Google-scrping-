import api from './client'
import { ApiResponse, Department } from '../types'

export const getDepartments = () => 
  api.get<any, ApiResponse<Department[]>>('/api/v1/departments')

export const getDepartment = (id: string) => 
  api.get<any, ApiResponse<Department>>(`/api/v1/departments/${id}`)
