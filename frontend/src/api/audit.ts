import api from './client'
import { ApiResponse } from '../types'

export interface AuditLog {
  id: string;
  user_id: string | null;
  action: string;
  resource: string | null;
  resource_id: string | null;
  dept_id: string | null;
  details: any;
  ip_address: string | null;
  created_at: string;
  user_email: string;
  dept_name: string;
}

export const getAuditLogs = () => 
  api.get<any, ApiResponse<AuditLog[]>>('/api/v1/audit')
