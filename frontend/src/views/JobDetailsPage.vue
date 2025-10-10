<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <button
              @click="goBack"
              class="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
            </svg>
            Back to Dashboard
          </button>

          <div v-if="job" class="flex items-center space-x-4">
            <StatusBadge :status="job.status"/>
          </div>
        </div>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="loading" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="flex items-center justify-center">
        <svg class="animate-spin h-12 w-12 text-primary-600" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    </div>

    <!-- Job Details -->
    <main v-else-if="job" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <!-- Job Info Card -->
      <div class="card animate-slide-up">
        <div class="flex items-start justify-between mb-6">
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-gray-900 mb-2">Scraping Job Details</h1>
            <div class="flex items-center space-x-4 text-sm text-gray-600">
              <span class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/>
                </svg>
                {{ job.url }}
              </span>
              <span class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                {{ formatDate(job.createdAt) }}
              </span>
            </div>
          </div>

          <button
              v-if="job.status === 'completed' || job.status === 'failed'"
              @click="refreshJob"
              class="btn-secondary"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            Refresh
          </button>
        </div>

        <!-- Progress Section -->
        <div v-if="job.status === 'in_progress' || job.status === 'pending'" class="space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-gray-700">{{ job.message || 'Processing...' }}</span>
            <span class="text-sm text-gray-500">{{ job.status }}</span>
          </div>

          <div class="relative">
            <div class="overflow-hidden h-3 text-xs flex rounded-full bg-gray-200">
              <div
                  class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-gradient-to-r from-primary-500 to-primary-600 transition-all duration-500 animate-pulse"
                  :style="{ width: progressPercentage + '%' }"
              ></div>
            </div>
            <div class="flex justify-between items-center mt-2">
              <span class="text-xs text-gray-600">{{ progressPercentage }}% Complete</span>
              <span class="text-xs text-gray-600">
                {{ job.total_pages_scraped || 0 }} pages scraped
              </span>
            </div>
          </div>

          <div class="flex items-center space-x-2 text-sm text-gray-600 bg-blue-50 p-4 rounded-lg">
            <svg class="w-5 h-5 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Scraping in progress... This page will auto-refresh</span>
          </div>
        </div>

        <!-- Completion Stats -->
        <div v-else-if="job.status === 'completed'" class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="bg-gradient-to-br from-green-50 to-emerald-50 p-4 rounded-lg border border-green-200">
            <p class="text-sm font-medium text-green-700">Total Pages</p>
            <p class="text-2xl font-bold text-green-900 mt-1">{{ job.total_pages_scraped }}</p>
          </div>

          <div class="bg-gradient-to-br from-blue-50 to-cyan-50 p-4 rounded-lg border border-blue-200">
            <p class="text-sm font-medium text-blue-700">URLs Discovered</p>
            <p class="text-2xl font-bold text-blue-900 mt-1">{{ job.sitemap?.total_urls || 0 }}</p>
          </div>

          <div class="bg-gradient-to-br from-purple-50 to-pink-50 p-4 rounded-lg border border-purple-200">
            <p class="text-sm font-medium text-purple-700">Images</p>
            <p class="text-2xl font-bold text-purple-900 mt-1">{{ totalImages }}</p>
          </div>

          <div class="bg-gradient-to-br from-red-50 to-pink-50 p-4 rounded-lg border border-red-200">
            <p class="text-sm font-medium text-red-700">Failed URLs</p>
            <p class="text-2xl font-bold text-red-900 mt-1">{{ job.failed_urls?.length || 0 }}</p>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="job.status === 'failed'" class="bg-red-50 border-l-4 border-red-500 p-4 rounded">
          <div class="flex items-center">
            <svg class="w-6 h-6 text-red-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clip-rule="evenodd"/>
            </svg>
            <div>
              <p class="font-medium text-red-800">Scraping Failed</p>
              <p class="text-sm text-red-700 mt-1">{{ job.message }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Failed URLs Section -->
      <FailedUrlsSection
          v-if="job.failed_urls && job.failed_urls.length > 0"
          :failed-urls="job.failed_urls"
          :job-id="job.job_id"
          @retry="handleRetry"
      />

      <!-- Output Directory Info -->
      <div v-if="job.output_directory && job.status === 'completed'" class="card animate-slide-up">
        <h2 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
          <svg class="w-5 h-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
          </svg>
          Output Directory
        </h2>
        <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
          <code class="text-sm text-gray-800 break-all">{{ job.output_directory }}</code>
        </div>
        <p class="text-xs text-gray-500 mt-2">
          All scraped data has been saved to this directory on the server
        </p>
      </div>

      <!-- Sitemap -->
      <div v-if="job.sitemap && job.status === 'completed'" class="card animate-slide-up">
        <h2 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
          <svg class="w-5 h-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
          </svg>
          Discovered URLs ({{ job.sitemap.total_urls }})
        </h2>

        <div class="max-h-96 overflow-y-auto space-y-2">
          <div
              v-for="(url, index) in job.sitemap.urls"
              :key="index"
              class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <span class="text-xs font-medium text-gray-500 bg-white px-2 py-1 rounded">{{ index + 1 }}</span>
            <a
                :href="url"
                target="_blank"
                class="text-sm text-primary-600 hover:text-primary-700 hover:underline flex-1 truncate"
            >
              {{ url }}
            </a>
            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- Scraped Pages -->
      <div v-if="job.pages && job.pages.length > 0" class="card animate-slide-up">
        <h2 class="text-lg font-bold text-gray-900 mb-4 flex items-center">
          <svg class="w-5 h-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          Scraped Pages ({{ job.pages.length }})
        </h2>

        <div class="space-y-4">
          <PagePreview
              v-for="(page, index) in job.pages.slice(0, showAllPages ? job.pages.length : 5)"
              :key="index"
              :page="page"
              :index="index"
          />
        </div>

        <button
            v-if="job.pages.length > 5"
            @click="showAllPages = !showAllPages"
            class="mt-4 w-full btn-secondary"
        >
          {{ showAllPages ? 'Show Less' : `Show All ${job.pages.length} Pages` }}
        </button>
      </div>

      <!-- General Errors -->
      <div v-if="job.errors && job.errors.length > 0" class="card animate-slide-up">
        <h2 class="text-lg font-bold text-orange-900 mb-4 flex items-center">
          <svg class="w-5 h-5 mr-2 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          General Errors ({{ job.errors.length }})
        </h2>

        <div class="space-y-2 max-h-64 overflow-y-auto">
          <div
              v-for="(error, index) in job.errors"
              :key="index"
              class="bg-orange-50 border-l-4 border-orange-400 p-3 rounded text-sm text-orange-800"
          >
            {{ error }}
          </div>
        </div>
      </div>
    </main>

    <!-- Error State -->
    <div v-else class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="text-center">
        <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <p class="text-gray-600 font-medium">Job not found</p>
        <button @click="goBack" class="mt-4 btn-primary">
          Go Back
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, computed, onMounted, onUnmounted} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useScraperStore} from '../stores/scraper'
import StatusBadge from '../components/StatusBadge.vue'
import PagePreview from '../components/PagePreview.vue'
import FailedUrlsSection from '../components/FailedUrlsSection.vue'

const route = useRoute()
const router = useRouter()
const scraperStore = useScraperStore()

const job = ref(null)
const loading = ref(true)
const showAllPages = ref(false)
let pollInterval = null

const progressPercentage = computed(() => {
  if (!job.value) return 0
  if (job.value.status === 'completed') return 100
  if (job.value.status === 'failed') return 0

  const totalPages = job.value.total_pages_scraped || 0
  const totalUrls = job.value.sitemap?.total_urls || 100

  return Math.min(Math.round((totalPages / totalUrls) * 100), 95)
})

const totalImages = computed(() => {
  if (!job.value?.pages) return 0
  return job.value.pages.reduce((sum, page) => sum + (page.all_images?.length || 0), 0)
})

onMounted(async () => {
  await loadJob()

  // Start polling if job is active
  if (job.value && (job.value.status === 'pending' || job.value.status === 'in_progress')) {
    startPolling()
  }
})

onUnmounted(() => {
  stopPolling()
})

async function loadJob() {
  loading.value = true
  try {
    const jobId = route.params.id
    const data = await scraperStore.getJobStatus(jobId)
    job.value = data
  } catch (error) {
    console.error('Failed to load job:', error)
  } finally {
    loading.value = false
  }
}

async function refreshJob() {
  await loadJob()
}

async function handleRetry(urls) {
  try {
    await scraperStore.retryFailedUrls(job.value.job_id, urls)

    // Start polling
    startPolling()
  } catch (error) {
    console.error('Failed to retry URLs:', error)
    alert('Failed to retry URLs. Please check console for details.')
  }
}

function startPolling() {
  pollInterval = setInterval(async () => {
    await loadJob()

    // Stop polling if job is complete
    if (job.value && (job.value.status === 'completed' || job.value.status === 'failed')) {
      stopPolling()
    }
  }, 3000)
}

function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}

function goBack() {
  router.push({name: 'Home'})
}

function formatDate(date) {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}
</script>