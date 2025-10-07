<template>
  <div class="min-h-screen">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div
                class="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/>
              </svg>
            </div>
            <div>
              <h1 class="text-2xl font-bold text-gray-900">Web Scraper</h1>
              <p class="text-sm text-gray-500">Professional data extraction tool</p>
            </div>
          </div>

          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-2">
              <div
                  :class="['w-2 h-2 rounded-full', scraperStore.isApiHealthy ? 'bg-green-500 animate-pulse' : 'bg-red-500']"></div>
              <span class="text-sm font-medium" :class="scraperStore.isApiHealthy ? 'text-green-600' : 'text-red-600'">
                {{ scraperStore.isApiHealthy ? 'API Online' : 'API Offline' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- New Scraping Form -->
      <div class="card mb-8 animate-slide-up">
        <h2 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <svg class="w-6 h-6 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Start New Scraping Job
        </h2>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Website URL *
            </label>
            <input
                v-model="formData.url"
                type="url"
                required
                placeholder="https://example.com"
                class="input-field"
                :disabled="scraperStore.isLoading"
            />
            <p class="mt-2 text-xs text-gray-500">
              ⚠️ Only scrape websites you own or have permission to access
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Max Crawl Depth
              </label>
              <input
                  v-model.number="formData.max_depth"
                  type="number"
                  min="1"
                  max="10"
                  class="input-field"
                  :disabled="scraperStore.isLoading"
              />
              <p class="mt-1 text-xs text-gray-500">How many levels deep to crawl (1-10)</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Authorization Token *
              </label>
              <input
                  v-model="formData.authorization_token"
                  type="text"
                  required
                  minlength="10"
                  placeholder="your-authorization-token"
                  class="input-field"
                  :disabled="scraperStore.isLoading"
              />
            </div>
          </div>

          <div class="flex items-center">
            <input
                v-model="formData.include_images"
                type="checkbox"
                id="include-images"
                class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                :disabled="scraperStore.isLoading"
            />
            <label for="include-images" class="ml-2 text-sm text-gray-700">
              Download images
            </label>
          </div>

          <div v-if="scraperStore.error" class="bg-red-50 border-l-4 border-red-500 p-4 rounded">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clip-rule="evenodd"/>
              </svg>
              <p class="text-sm text-red-700">{{ scraperStore.error }}</p>
            </div>
          </div>

          <div class="flex items-center justify-between">
            <button
                type="submit"
                class="btn-primary flex items-center"
                :disabled="scraperStore.isLoading || !scraperStore.isApiHealthy"
            >
              <svg v-if="!scraperStore.isLoading" class="w-5 h-5 mr-2" fill="none" stroke="currentColor"
                   viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
              <svg v-else class="animate-spin w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ scraperStore.isLoading ? 'Starting...' : 'Start Scraping' }}
            </button>

            <button
                type="button"
                @click="loadJobs"
                class="btn-secondary flex items-center"
                :disabled="scraperStore.isLoading"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              Refresh Jobs
            </button>
          </div>
        </form>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Total Jobs</p>
              <p class="text-3xl font-bold text-gray-900 mt-1">{{ scraperStore.jobs.length }}</p>
            </div>
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Active</p>
              <p class="text-3xl font-bold text-yellow-600 mt-1">{{ scraperStore.activeJobs.length }}</p>
            </div>
            <div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-yellow-600 animate-spin-slow" fill="none" stroke="currentColor"
                   viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Completed</p>
              <p class="text-3xl font-bold text-green-600 mt-1">{{ scraperStore.completedJobs.length }}</p>
            </div>
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Failed</p>
              <p class="text-3xl font-bold text-red-600 mt-1">{{ scraperStore.failedJobs.length }}</p>
            </div>
            <div class="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Jobs List -->
      <div class="card">
        <h2 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <svg class="w-6 h-6 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
          </svg>
          Recent Jobs
        </h2>

        <div v-if="scraperStore.jobs.length === 0" class="text-center py-12">
          <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
          </svg>
          <p class="text-gray-600 font-medium">No jobs yet</p>
          <p class="text-gray-500 text-sm mt-1">Start your first scraping job above</p>
        </div>

        <div v-else class="space-y-4">
          <JobCard
              v-for="job in scraperStore.jobs"
              :key="job.job_id"
              :job="job"
              @view-details="viewJobDetails"
              @delete="handleDeleteJob"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import {ref, onMounted} from 'vue'
import {useRouter} from 'vue-router'
import {useScraperStore} from '../stores/scraper'
import JobCard from '../components/JobCard.vue'

const router = useRouter()
const scraperStore = useScraperStore()

const formData = ref({
  url: '',
  max_depth: 3,
  include_images: true,
  authorization_token: ''
})

onMounted(() => {
  loadJobs()
})

async function handleSubmit() {
  try {
    const job = await scraperStore.startScraping(formData.value)

    // Reset form
    formData.value = {
      url: '',
      max_depth: 3,
      include_images: true,
      authorization_token: ''
    }

    // Navigate to job details
    router.push({name: 'JobDetails', params: {id: job.job_id}})
  } catch (error) {
    console.error('Failed to start scraping:', error)
  }
}

async function loadJobs() {
  await scraperStore.loadAllJobs()
}

function viewJobDetails(jobId) {
  router.push({name: 'JobDetails', params: {id: jobId}})
}

async function handleDeleteJob(jobId) {
  if (confirm('Are you sure you want to delete this job?')) {
    try {
      await scraperStore.deleteJob(jobId)
    } catch (error) {
      console.error('Failed to delete job:', error)
    }
  }
}
</script>