<template>
  <div v-if="failedUrls && failedUrls.length > 0" class="card animate-slide-up">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-bold text-red-900 flex items-center">
        <svg class="w-5 h-5 mr-2 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        Failed URLs ({{ failedUrls.length }})
      </h2>

      <div class="flex items-center space-x-2">
        <button
            v-if="selectedUrls.length > 0"
            @click="retrySelected"
            :disabled="isRetrying"
            class="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
          <svg v-if="!isRetrying" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          <svg v-else class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isRetrying ? 'Retrying...' : `Retry Selected (${selectedUrls.length})` }}
        </button>

        <button
            @click="retryAll"
            :disabled="isRetrying"
            class="flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
          <svg v-if="!isRetrying" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          <svg v-else class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isRetrying ? 'Retrying...' : 'Retry All' }}
        </button>
      </div>
    </div>

    <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded mb-4">
      <div class="flex items-start">
        <svg class="w-5 h-5 text-red-600 mt-0.5 mr-3" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clip-rule="evenodd"/>
        </svg>
        <div>
          <p class="font-medium text-red-800">Some URLs failed to scrape</p>
          <p class="text-sm text-red-700 mt-1">
            Select URLs below and click "Retry Selected", or click "Retry All" to retry all failed URLs at once.
          </p>
        </div>
      </div>
    </div>

    <div class="space-y-2 max-h-96 overflow-y-auto">
      <div
          v-for="(failedUrl, index) in failedUrls"
          :key="index"
          class="flex items-start space-x-3 p-4 bg-white border-2 rounded-lg hover:border-red-300 transition-colors"
          :class="{ 'border-red-400 bg-red-50': selectedUrls.includes(failedUrl.url) }">
        <input
            type="checkbox"
            :id="`failed-url-${index}`"
            :value="failedUrl.url"
            v-model="selectedUrls"
            class="w-5 h-5 text-red-600 border-gray-300 rounded focus:ring-red-500 mt-1"
        />

        <div class="flex-1 min-w-0">
          <div class="flex items-center space-x-2 mb-2">
            <span class="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded">{{ index + 1 }}</span>
            <span v-if="failedUrl.retry_count > 0"
                  class="text-xs font-medium text-orange-600 bg-orange-100 px-2 py-1 rounded">
              Retry {{ failedUrl.retry_count }}
            </span>
          </div>

          <a
              :href="failedUrl.url"
              target="_blank"
              class="text-sm font-medium text-red-600 hover:text-red-700 hover:underline break-all block mb-2">
            {{ failedUrl.url }}
          </a>

          <div class="bg-gray-50 border border-gray-200 rounded p-3">
            <p class="text-xs font-medium text-gray-700 mb-1">Error:</p>
            <p class="text-xs text-gray-600">{{ failedUrl.error }}</p>
          </div>

          <div class="flex items-center space-x-4 mt-2 text-xs text-gray-500">
            <span class="flex items-center">
              <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              Attempted: {{ formatDate(failedUrl.attempted_at) }}
            </span>
          </div>
        </div>

        <button
            @click="retryUrl(failedUrl.url)"
            :disabled="isRetrying"
            class="flex-shrink-0 p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
            title="Retry this URL">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
        </button>
      </div>
    </div>

    <div v-if="selectedUrls.length > 0" class="mt-4 flex items-center justify-between bg-blue-50 p-3 rounded-lg">
      <span class="text-sm font-medium text-blue-900">{{ selectedUrls.length }} URL(s) selected</span>
      <button
          @click="clearSelection"
          class="text-sm text-blue-600 hover:text-blue-700 font-medium">
        Clear Selection
      </button>
    </div>
  </div>
</template>

<script setup>
import {ref} from 'vue'

const props = defineProps({
  failedUrls: {
    type: Array,
    required: true
  },
  jobId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['retry'])

const selectedUrls = ref([])
const isRetrying = ref(false)

function formatDate(date) {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

async function retryUrl(url) {
  isRetrying.value = true
  try {
    await emit('retry', [url])
  } finally {
    isRetrying.value = false
  }
}

async function retrySelected() {
  if (selectedUrls.value.length === 0) return

  isRetrying.value = true
  try {
    await emit('retry', [...selectedUrls.value])
    selectedUrls.value = []
  } finally {
    isRetrying.value = false
  }
}

async function retryAll() {
  const allUrls = props.failedUrls.map(f => f.url)
  isRetrying.value = true
  try {
    await emit('retry', allUrls)
    selectedUrls.value = []
  } finally {
    isRetrying.value = false
  }
}

function clearSelection() {
  selectedUrls.value = []
}
</script>