import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - inject auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().clearAuth()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login/', credentials),
  register: (userData) => api.post('/auth/register/', userData),
  refreshToken: (refreshToken) => api.post('/auth/refresh/', { refresh: refreshToken }),
  logout: () => api.post('/auth/logout/'),
}

// GitHub Integration API
export const githubAPI = {
  listRepos: () => api.get('/github/repos/'),
  getRepo: (repoId) => api.get(`/github/repos/${repoId}/`),
  connectRepo: (repoData) => api.post('/github/repos/', repoData),
  disconnectRepo: (repoId) => api.delete(`/github/repos/${repoId}/`),
  getWebhookEvents: (repoId) => api.get(`/github/repos/${repoId}/events/`),
}

// AI Engine API
export const aiAPI = {
  generateTests: (codeData) => api.post('/ai/generate/', codeData),
  updateTests: (testData) => api.post('/ai/update/', testData),
  getTestFile: (testId) => api.get(`/ai/tests/${testId}/`),
  listTestFiles: (repoId) => api.get(`/ai/tests/?repo=${repoId}`),
}

// Insights API
export const insightsAPI = {
  getMetrics: (repoId) => api.get(`/insights/metrics/${repoId ? `?repo=${repoId}` : ''}`),
  getTestHealth: (repoId) => api.get(`/insights/test-health/${repoId}/`),
  getTimeline: (repoId) => api.get(`/insights/timeline/${repoId}/`),
  getProductivityStats: () => api.get('/insights/productivity/'),
}

// CI Pipeline API
export const ciAPI = {
  getPipelineStatus: (repoId) => api.get(`/ci/status/${repoId}/`),
  getQualityGate: (repoId) => api.get(`/ci/quality-gate/${repoId}/`),
  triggerPipeline: (repoId) => api.post(`/ci/trigger/${repoId}/`),
}

export default api

// Made with Bob
