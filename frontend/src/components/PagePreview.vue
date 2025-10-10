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
            <p class="text-lg font-bold text-gray-900">{{ contentBlocksCount }}</p>
            <p class="text-xs text-gray-500">blocks</p>
          </div>
          <div v-if="page.all_images && page.all_images.length > 0" class="text-center">
            <p class="text-lg font-bold text-purple-600">{{ page.all_images.length }}</p>
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
      <!-- Metadata -->
      <div v-if="page.metadata && Object.keys(page.metadata).length > 0" class="space-y-2">
        <h5 class="font-semibold text-gray-900 text-sm">Metadata</h5>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
          <div v-for="(value, key) in page.metadata" :key="key" class="bg-white p-3 rounded border border-gray-200">
            <p class="text-xs font-medium text-gray-500 uppercase mb-1">{{ key }}</p>
            <p class="text-sm text-gray-900 line-clamp-2">{{ value }}</p>
          </div>
        </div>
      </div>

      <!-- Structured Content with Images at Positions -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <h5 class="font-semibold text-gray-900 text-sm">Structured Content</h5>
          <span class="text-xs text-gray-500">{{ contentBlocksCount }} blocks ({{
              textBlocksCount
            }} text, {{ imageBlocksCount }} images)</span>
        </div>

        <div class="bg-white p-4 rounded border border-gray-200 space-y-3 max-h-96 overflow-y-auto">
          <div v-for="(block, blockIndex) in displayedContent" :key="blockIndex">
            <!-- Text Block -->
            <div v-if="block.type === 'text'" class="text-sm text-gray-700">
              <p class="whitespace-pre-wrap">{{ block.content }}</p>
            </div>

            <!-- Image Block -->
            <div v-else-if="block.type === 'image'" class="bg-blue-50 border-l-4 border-blue-500 p-3 rounded">
              <div class="flex items-start space-x-3">
                <svg class="w-5 h-5 text-blue-600 flex-shrink-0 mt-1" fill="none" stroke="currentColor"
                     viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-medium text-blue-900 mb-1">IMAGE AT THIS POSITION</p>
                  <a :href="block.url" target="_blank"
                     class="text-xs text-blue-600 hover:text-blue-700 hover:underline break-all">
                    {{ block.url }}
                  </a>
                  <p v-if="block.alt" class="text-xs text-gray-600 mt-1">
                    <span class="font-medium">Alt:</span> {{ block.alt }}
                  </p>
                  <p v-if="block.title" class="text-xs text-gray-600">
                    <span class="font-medium">Title:</span> {{ block.title }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <button
              v-if="page.structured_content && page.structured_content.length > maxDisplayBlocks"
              @click="showAllContent = !showAllContent"
              class="w-full mt-2 text-primary-600 hover:text-primary-700 text-sm font-medium py-2 px-4 bg-primary-50 hover:bg-primary-100 rounded transition-colors">
            {{ showAllContent ? 'Show Less' : `Show All ${page.structured_content.length} Blocks` }}
          </button>
        </div>
      </div>

      <!-- All Images List -->
      <div v-if="page.all_images && page.all_images.length > 0">
        <h5 class="font-semibold text-gray-900 text-sm mb-2">All Image URLs ({{ page.all_images.length }})</h5>
        <div class="bg-white p-4 rounded border border-gray-200 max-h-48 overflow-y-auto space-y-2">
          <div v-for="(imageUrl, imgIndex) in page.all_images.slice(0, showAllImages ? page.all_images.length : 10)"
               :key="imgIndex"
               class="flex items-center space-x-2 p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors">
            <span class="text-xs font-medium text-gray-500 bg-white px-2 py-1 rounded">{{ imgIndex + 1 }}</span>
            <a :href="imageUrl" target="_blank"
               class="text-xs text-primary-600 hover:text-primary-700 hover:underline flex-1 truncate">
              {{ imageUrl }}
            </a>
            <button @click="copyToClipboard(imageUrl)" class="text-gray-400 hover:text-gray-600" title="Copy URL">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
              </svg>
            </button>
          </div>

          <button
              v-if="page.all_images.length > 10"
              @click="showAllImages = !showAllImages"
              class="w-full text-center text-primary-600 hover:text-primary-700 text-sm font-medium py-2">
            {{ showAllImages ? 'Show Less' : `Show All ${page.all_images.length} Images` }}
          </button>
        </div>
      </div>

      <!-- Timestamp -->
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
const showAllContent = ref(false)
const showAllImages = ref(false)
const maxDisplayBlocks = 20

const contentBlocksCount = computed(() => {
  return props.page.structured_content?.length || 0
})

const textBlocksCount = computed(() => {
  return props.page.structured_content?.filter(b => b.type === 'text').length || 0
})

const imageBlocksCount = computed(() => {
  return props.page.structured_content?.filter(b => b.type === 'image').length || 0
})

const displayedContent = computed(() => {
  if (!props.page.structured_content) return []
  if (showAllContent.value) return props.page.structured_content
  return props.page.structured_content.slice(0, maxDisplayBlocks)
})

function formatDate(date) {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text)
    alert('URL copied to clipboard!')
  } catch (err) {
    console.error('Failed to copy:', err)
  }
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