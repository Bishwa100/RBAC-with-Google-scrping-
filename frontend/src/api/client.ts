import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refreshToken = useAuthStore.getState().refreshToken
        if (!refreshToken) throw new Error('No refresh token')

        const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        })

        const { access_token } = response.data.data
        useAuthStore.getState().updateAccessToken(access_token)

        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        useAuthStore.getState().logout()
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

// ============================================================================
// TopicLens API Types and Endpoints (now unified in single backend)
// ============================================================================

export interface TopicSearchRequest {
  topic: string
  sources: string[]
  deep_analysis?: boolean
}

export interface TopicSearchResponse {
  job_id: string
  task_id?: string
  message: string
}

export interface JobStatus {
  id: string
  user_id: string
  topic: string
  sources: string[]
  deep_analysis: boolean
  status: string
  progress: number
  result?: any
  error_message?: string
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface ContentAnalyzeRequest {
  url: string
}

// TopicLens API methods (using same client, different routes)
export const topiclensAPI = {
  // Search endpoint
  search: (data: TopicSearchRequest): Promise<any> => 
    api.post('/api/v1/topiclens/search', data),

  // Get job status
  getJobStatus: (jobId: string): Promise<any> => 
    api.get(`/api/v1/topiclens/status/${jobId}`),

  // Analyze content
  analyzeContent: (data: ContentAnalyzeRequest): Promise<any> => 
    api.post('/api/v1/topiclens/analyze', data),

  // Get available sources
  getAvailableSources: (): Promise<any> => 
    api.get('/api/v1/topiclens/sources'),

  // Get all jobs
  getAllJobs: (limit: number = 50, offset: number = 0): Promise<any> => 
    api.get(`/api/v1/topiclens/jobs?limit=${limit}&offset=${offset}`),

  // Health check
  healthCheck: (): Promise<any> => 
    api.get('/api/v1/topiclens/health'),

  // Content Sharing endpoints
  shareContent: (data: {
    job_id: string
    role_ids: string[]
    source: string
    url: string
    title?: string
    content?: string
    rank?: number
    notes?: string
  }): Promise<any> => 
    api.post('/api/v1/topiclens/share', data),

  getMySharedContent: (limit: number = 50, offset: number = 0): Promise<any> => 
    api.get(`/api/v1/topiclens/my-shared-content?limit=${limit}&offset=${offset}`),

  getAllSharedContent: (limit: number = 100, offset: number = 0, roleId?: string): Promise<any> => {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) })
    if (roleId) params.append('role_id', roleId)
    return api.get(`/api/v1/topiclens/shared?${params.toString()}`)
  },

  revokeShare: (shareId: string): Promise<any> => 
    api.delete(`/api/v1/topiclens/share/${shareId}`),
}

export default api
