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
