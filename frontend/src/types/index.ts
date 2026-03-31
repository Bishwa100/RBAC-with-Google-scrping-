export interface Scope {
  id: string;
  resource: string;
  action: string;
  description: string | null;
}

export interface Role {
  id: string;
  name: string;
  level: number;
  dept_id?: string | null;
  description: string | null;
  scopes?: Scope[];
}

export interface Department {
  id: string;
  name: string;
  description: string | null;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  department_id: string | null;
  department: Department | null;
  roles: Role[];
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  minRoleLevel: number;
  deptId: string | null;
  scopes: string[];
  isAuthenticated: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
  detail?: string;
}

// TopicLens Types
export interface SharedContentItem {
  share_id: string;
  result_id: number;
  job_id: string;
  
  // Content details
  topic: string;
  source: string;
  url: string;
  title: string | null;
  content: string | null;
  metadata: Record<string, any> | null;
  
  // Analysis
  sentiment: string | null;
  keywords: string[] | null;
  summary: string | null;
  
  // Sharing metadata
  shared_by_user_id: string;
  shared_by_username: string;
  shared_with_role_id: string;
  shared_with_role_name: string;
  notes: string | null;
  shared_at: string;
  
  // Timestamps
  created_at: string;
}

export interface ShareContentRequest {
  result_id: number;
  job_id: string;
  role_ids: string[];
  notes?: string;
}

export interface ShareContentResponse {
  success: boolean;
  message: string;
  shared_count: number;
  share_ids: string[];
}

export interface MySharedContentResponse {
  items: SharedContentItem[];
  total: number;
}
