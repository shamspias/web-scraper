<template>
  <div
      class="bg-white border-2 border-gray-200 rounded-xl p-5 hover:border-primary-400 hover:shadow-lg transition-all duration-300 cursor-pointer"
      @click="$emit('view-details', job.job_id)">
    <div class="flex items-start justify-between mb-4">
      <div class="flex-1 min-w-0">
        <div class="flex items-center space-x-3 mb-2">
          <StatusBadge :status="job.status"/>
          <span class="text-xs text-gray-500">{{ formatDate(job.createdAt) }}</span>
        </div>

        <h3 class="text-lg font-semibold text-gray-900 truncate mb-1">
          {{ getDomainFromUrl(job.url) }}
        </h3>

        <a :href="job.url" target="_blank"
           class="text-sm text-primary-600 hover:text-primary-700 hover:underline truncate block" @click.stop>
          {{ job.url }}
        </a>
      </div>

      <div class="flex items-center space-x-2 ml-4">
        <button @click.stop="$emit('delete', job.job_id)"
                class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Delete job">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
      </div>
    </div>

    <div v-if="job.status === 'in_progress' || job.status === 'pending'" class="mb-4">
      <div class="flex items-center justify-between text-xs text-gray-600 mb-1">
        <span>{{ job.message || 'Processing...' }}</span>
        <span>{{ progressPercentage }}%</span>
      </div>
      <div class="overflow-hidden h-2 text-xs flex rounded-full bg-gray-200">
        <div
            class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-gradient-to-r from-primary-500 to-primary-600 transition-all duration-500"
            :style="{ width: progressPercentage + '%' }"></div>
      </div>
    </div>

    <div v-else-if="job.status === 'completed'" class="grid grid-cols-3 gap-4">
      <div class="text-center">
        <p class="text-2xl font-bold text-primary-600">{{ job.total_pages_scraped || 0 }}</p>
        <p class="text-xs text-gray-600">Pages</p>
      </div>
      <div class="text-center">
        <p class="text-2xl font-bold text-green-600">{{ job.sitemap?.total_urls || 0 }}</p>
        <p class="text-xs text-gray-600">URLs</p>
      </div>
      <div class="text-center">
        <p class="text-2xl font-bold text-purple-600">{{ totalImages }}</p>
        <p class="text-xs text-gray-600">Images</p>
      </div>
    </div>

    <div v-else-if="job.status === 'failed'" class="bg-red-50 p-3 rounded-lg">
      <p class="text-sm text-red-800">{{ job.message || 'Scraping failed' }}</p>
    </div>

    <div class="mt-4 pt-4 border-t border-gray-200">
      <button @click.stop="$emit('view-details', job.job_id)"
              class="w-full flex items-center justify-center space-x-2 py-2 px-4 bg-gray-100 hover:bg-primary-50 text-gray-700 hover:text-primary-700 rounded-lg transition-colors font-medium">
        <span>View Details</span>
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import {computed} from 'vue'
import StatusBadge from './StatusBadge.vue'

const props = defineProps({
  job: {
    type: Object,
    required: true
  }
})

defineEmits(['view-details', 'delete'])

const progressPercentage = computed(() => {
  if (props.job.status === 'completed') return 100
  if (props.job.status === 'failed') return 0
  const totalPages = props.job.total_pages_scraped || 0
  const totalUrls = props.job.sitemap?.total_urls || 100
  return Math.min(Math.round((totalPages / totalUrls) * 100), 95)
})

const totalImages = computed(() => {
  if (!props.job.pages) return 0
  return props.job.pages.reduce((sum, page) => sum + (page.images?.length || 0), 0)
})

function getDomainFromUrl(url) {
  try {
    const urlObj = new URL(url)
    return urlObj.hostname.replace('www.', '')
  } catch {
    return url
  }
}

function formatDate(date) {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}
</script>

