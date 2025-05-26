import axios from 'axios'

const API_BASE_URL = 'http://172.22.206.209:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// Monitoring API endpoints
export const monitoringApi = {
  // System health and status
  getHealth: () => api.get('/health'),
  getSystemStatus: () => api.get('/api/v1/monitoring/status'),
  getSystemMetrics: () => api.get('/api/v1/monitoring/metrics'),
  
  // Scraping sessions
  getScrapingSessions: (params = {}) => api.get('/api/v1/monitoring/sessions', { params }),
  getSessionDetails: (sessionId) => api.get(`/api/v1/monitoring/sessions/${sessionId}`),
  createScrapingSession: (data) => api.post('/api/v1/monitoring/sessions', data),
  updateSessionStatus: (sessionId, status) => 
    api.patch(`/api/v1/monitoring/sessions/${sessionId}`, { status }),
  
  // Site statistics
  getSiteStats: () => api.get('/api/v1/monitoring/sites'),
  getSiteMetrics: (site) => api.get(`/api/v1/monitoring/sites/${site}/metrics`),
  
  // Performance metrics
  getPerformanceMetrics: (timeRange = '1h') => 
    api.get('/api/v1/monitoring/performance', { params: { range: timeRange } }),
  
  // Error tracking
  getErrors: (params = {}) => api.get('/api/v1/monitoring/errors', { params }),
  
  // Multi-site orchestrator
  getOrchestratorStatus: () => api.get('/api/v1/orchestrator/status'),
  startMultiSiteScraping: (config) => api.post('/api/v1/orchestrator/start', config),
  stopMultiSiteScraping: () => api.post('/api/v1/orchestrator/stop'),
}

// Jobs API endpoints
export const jobsApi = {
  getJobs: (params = {}) => api.get('/api/v1/jobs', { params }),
  getJob: (jobId) => api.get(`/api/v1/jobs/${jobId}`),
  createJob: (data) => api.post('/api/v1/jobs', data),
  updateJob: (jobId, data) => api.put(`/api/v1/jobs/${jobId}`, data),
  deleteJob: (jobId) => api.delete(`/api/v1/jobs/${jobId}`),
  getJobStats: () => api.get('/api/v1/jobs/stats'),
}

export default api