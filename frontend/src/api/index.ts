// Export unified API client
export { default as api, topiclensAPI } from './client'

// Export all service modules
export * from './auth'
export * from './users'
export * from './roles'
export * from './scopes'
export * from './departments'
export * from './records'
export * from './editRequests'
export * from './audit'

// Export TopicLens types
export type {
  TopicSearchRequest,
  TopicSearchResponse,
  JobStatus,
  ContentAnalyzeRequest,
} from './client'
