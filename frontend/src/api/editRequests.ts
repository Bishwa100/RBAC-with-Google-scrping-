import api from './client'
import { ApiResponse } from '../types'

export interface ApprovalStep {
  id: string;
  request_id: string;
  approver_id: string | null;
  step_level: number;
  required_min_role_level: number;
  decision: string | null;
  decided_at: string | null;
  comment: string | null;
  created_at: string;
}

export interface EditRequest {
  id: string;
  record_id: string;
  requested_by: string;
  reason: string;
  status: 'pending' | 'approved' | 'rejected' | 'completed';
  approvals_required: number;
  approvals_received: number;
  edit_window_minutes: number;
  edit_window_expires_at: string | null;
  created_at: string;
  resolved_at: string | null;
  steps: ApprovalStep[];
}

export const getEditRequests = (params?: any) => 
  api.get<any, ApiResponse<EditRequest[]>>('/api/v1/edit-requests', { params })

export const getEditRequest = (id: string) =>
  api.get<any, ApiResponse<EditRequest>>(`/api/v1/edit-requests/${id}`)

export const createEditRequest = (data: { record_id: string, reason: string }) => 
  api.post<any, ApiResponse<EditRequest>>('/api/v1/edit-requests', data)

export const approveEditRequest = (id: string, comment: string = '') => 
  api.post<any, ApiResponse<EditRequest>>(`/api/v1/edit-requests/${id}/approve`, { decision: 'approved', comment })

export const rejectEditRequest = (id: string, comment: string = '') => 
  api.post<any, ApiResponse<EditRequest>>(`/api/v1/edit-requests/${id}/reject`, { decision: 'rejected', comment })
