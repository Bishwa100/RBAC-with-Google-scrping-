import api from './client'
import { ApiResponse } from '../types'

export interface Record {
  id: string;
  submitted_by: string;
  dept_id: string;
  record_type: string;
  payload: any;
  is_frozen: boolean;
  frozen_at: string;
  unfrozen_at: string | null;
  version: number;
  created_at: string;
  updated_at: string | null;
}

export const getRecords = (params?: any) => 
  api.get<any, ApiResponse<Record[]>>('/api/v1/records', { params })

export const getRecord = (id: string) => 
  api.get<any, ApiResponse<Record>>(`/api/v1/records/${id}`)

export const createRecord = (data: { record_type: string, payload: any }) => 
  api.post<any, ApiResponse<Record>>('/api/v1/records', data)

export const updateRecord = (id: string, data: { payload: any }) => 
  api.patch<any, ApiResponse<Record>>(`/api/v1/records/${id}`, data)
