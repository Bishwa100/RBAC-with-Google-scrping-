import api from './client'
import { ApiResponse, User } from '../types'

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export const login = (data: any) => 
  api.post<any, ApiResponse<LoginResponse>>('/api/v1/auth/login', data)

export const getMe = () => 
  api.get<any, ApiResponse<User>>('/api/v1/auth/me')

export const logout = () =>
  api.post('/api/v1/auth/logout')
