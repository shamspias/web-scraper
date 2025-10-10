import {defineStore} from 'pinia'
import {ref, computed} from 'vue'
import api from '../services/api'

export const useScraperStore = defineStore('scraper', () => {
    const jobs = ref([])
    const currentJob = ref(null)
    const isApiHealthy = ref(false)
    const isLoading = ref(false)
    const error = ref(null)

    const activeJobs = computed(() =>
        jobs.value.filter(job =>
            job.status === 'pending' || job.status === 'in_progress'
        )
    )

    const completedJobs = computed(() =>
        jobs.value.filter(job => job.status === 'completed')
    )

    const failedJobs = computed(() =>
        jobs.value.filter(job => job.status === 'failed')
    )

    async function checkApiHealth() {
        try {
            const response = await api.checkHealth()
            isApiHealthy.value = response.data.status === 'healthy'
        } catch (err) {
            isApiHealthy.value = false
            console.error('API health check failed:', err)
        }
    }

    async function startScraping(jobData) {
        isLoading.value = true
        error.value = null

        try {
            const response = await api.startScrape(jobData)
            const newJob = {
                ...response.data,
                url: jobData.url,
                createdAt: new Date().toISOString()
            }
            jobs.value.unshift(newJob)

            // Start polling for this job
            pollJobStatus(newJob.job_id)

            return newJob
        } catch (err) {
            error.value = err.response?.data?.detail || 'Failed to start scraping'
            throw err
        } finally {
            isLoading.value = false
        }
    }

    async function getJobStatus(jobId) {
        try {
            const response = await api.getJobStatus(jobId)

            // Update job in list
            const index = jobs.value.findIndex(j => j.job_id === jobId)
            if (index !== -1) {
                jobs.value[index] = {
                    ...jobs.value[index],
                    ...response.data
                }
            }

            return response.data
        } catch (err) {
            console.error('Failed to get job status:', err)
            throw err
        }
    }

    async function pollJobStatus(jobId, interval = 2000) {
        const poll = async () => {
            try {
                const status = await getJobStatus(jobId)

                if (status.status === 'completed' || status.status === 'failed') {
                    return
                }

                setTimeout(poll, interval)
            } catch (err) {
                console.error('Polling error:', err)
            }
        }

        poll()
    }

    async function loadAllJobs() {
        try {
            const response = await api.listJobs()
            // Fetch detailed info for each job
            const jobPromises = response.data.jobs.map(job =>
                getJobStatus(job.job_id)
            )
            const detailedJobs = await Promise.all(jobPromises)
            jobs.value = detailedJobs
        } catch (err) {
            console.error('Failed to load jobs:', err)
        }
    }

    async function deleteJob(jobId) {
        try {
            await api.deleteJob(jobId)
            jobs.value = jobs.value.filter(j => j.job_id !== jobId)
        } catch (err) {
            console.error('Failed to delete job:', err)
            throw err
        }
    }

    async function retryFailedUrls(jobId, urls) {
        try {
            const response = await api.retryFailedUrls(jobId, urls)

            // Start polling for this job
            pollJobStatus(jobId)

            return response.data
        } catch (err) {
            console.error('Failed to retry URLs:', err)
            throw err
        }
    }

    return {
        jobs,
        currentJob,
        isApiHealthy,
        isLoading,
        error,
        activeJobs,
        completedJobs,
        failedJobs,
        checkApiHealth,
        startScraping,
        getJobStatus,
        pollJobStatus,
        loadAllJobs,
        deleteJob,
        retryFailedUrls
    }
})