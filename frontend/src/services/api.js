import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    },
    timeout: 30000
})

// Request interceptor
apiClient.interceptors.request.use(
    config => {
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

// Response interceptor
apiClient.interceptors.response.use(
    response => response,
    error => {
        console.error('API Error:', error.response?.data || error.message)
        return Promise.reject(error)
    }
)

export default {
    checkHealth() {
        return apiClient.get('/health')
    },

    startScrape(data) {
        return apiClient.post('/scrape', data)
    },

    getJobStatus(jobId) {
        return apiClient.get(`/scrape/${jobId}`)
    },

    deleteJob(jobId) {
        return apiClient.delete(`/scrape/${jobId}`)
    },

    listJobs() {
        return apiClient.get('/jobs')
    }
}