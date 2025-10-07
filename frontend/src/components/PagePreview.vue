<template>
  <div class="border-2 border-gray-200 rounded-lg hover:border-primary-300 transition-colors">
    <button @click="expanded = !expanded"
            class="w-full text-left p-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
      <div class="flex items-center space-x-3 flex-1 min-w-0">
        <div class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
          <span class="text-sm font-bold text-primary-700">{{ index + 1 }}</span>
        </div>

        <div class="flex-1 min-w-0">
          <h4 class="font-semibold text-gray-900 truncate mb-1">{{ page.title || 'Untitled Page' }}</h4>
          <p class="text-sm text-gray-600 truncate">{{ page.url }}</p>
        </div>

        <div class="flex items-center space-x-4 flex-shrink-0">
          <div class="text-center">
            <p class="text-lg font-bold text-gray-900">{{ wordCount }}</p>
            <p class="text-xs text-gray-500">words</p>
          </div>
          <div v-if="page.images && page.images.length > 0" class="text-center">
            <p class="text-lg font-bold text-purple-600">{{ page.images.length }}</p>
            <p class="text-xs text-gray-500">images</p>
          </div>
        </div>
      </div>

      <svg class="w-5 h-5 text-gray-400 transition-transform ml-2" :class="{ 'transform rotate-180': expanded }"
           fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
      </svg>
    </button>

    <div v-if="expanded" class="border-t border-gray-200 p-4 bg-gray-50 space-y-4">
      <div v-if="page.metadata && Object.keys(page.metadata).length > 0" class="space-y-2">
        <h5 class="font-semibold text-gray-900 text-sm">Metadata</h5>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
          <div v-for="(value, key) in page.metadata" :key="key" class="bg-white p-3 rounded border border-gray-200">
            <p class="text-xs font-medium text-gray-500 uppercase mb-1">{{ key }}</p>
            <p class="text-sm text-gray-900 line-clamp-2">{{ value }}</p>
          </div>
        </div>
      </div>

      <div>
        <h5 class="font-semibold text-gray-900 text-sm mb-2">Text Content</h5>
        <div class="bg-white p-4 rounded border border-gray-200 max-h-64 overflow-y-auto">
          <p class="text-sm text-gray-700 whitespace-pre-line">{{ textPreview }}</p>
          <button v-if="page.clean_text && page.clean_text.length > 500" @click="showFullText = !showFullText"
                  class="mt-2 text-primary-600 hover:text-primary-700 text-sm font-medium">
            {{ showFullText ? 'Show Less' : 'Show More' }}
          </button>
        </div>
      </div>

      <div v-if="page.images && page.images.length > 0">
        <h5 class="font-semibold text-gray-900 text-sm mb-2">Images ({{ page.images.length }})</h5>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div v-for="(image, imgIndex) in page.images.slice(0, 8)" :key="imgIndex"
               class="bg-white p-2 rounded border border-gray-200 hover:border-primary-300 transition-colors">
            <div class="aspect-square bg-gray-100 rounded mb-2 flex items-center justify-center overflow-hidden">
              <img v-if="image.url" :src="image.url" :alt="image.alt_text || 'Image'" class="w-full h-full object-cover"
                   @error="handleImageError"/>
              <svg v-else class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
            </div>
            <p class="text-xs text-gray-600 truncate" :title="image.alt_text">{{ image.alt_text || 'No alt text' }}</p>
            <p v-if="image.downloaded_path" class="text-xs text-green-600 mt-1 flex items-center">
              <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
              Downloaded
            </p>
          </div>
        </div>
        <p v-if="page.images.length > 8" class="text-sm text-gray-500 mt-2 text-center">+ {{ page.images.length - 8 }}
          more images</p>
      </div>

      <div class="text-xs text-gray-500 flex items-center">
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        Scraped: {{ formatDate(page.scraped_at) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, computed} from 'vue'

const props = defineProps({
  page: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  }
})

const expanded = ref(false)
const showFullText = ref(false)

const wordCount = computed(() => {
  if (!props.page.clean_text) return 0
  return props.page.clean_text.split(/\s+/).length
})

const textPreview = computed(() => {
  if (!props.page.clean_text) return 'No text content'
  if (showFullText.value) return props.page.clean_text
  return props.page.clean_text.slice(0, 500) + (props.page.clean_text.length > 500 ? '...' : '')
})

function handleImageError(event) {
  event.target.style.display = 'none'
}

function formatDate(date) {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
