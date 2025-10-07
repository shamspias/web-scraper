<template>
  <span :class="badgeClasses" class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold">
    <span :class="dotClasses" class="w-2 h-2 rounded-full"></span>
    <span>{{ statusText }}</span>
  </span>
</template>

<script setup>
import {computed} from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  }
})

const badgeClasses = computed(() => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800 border border-yellow-300',
    in_progress: 'bg-blue-100 text-blue-800 border border-blue-300',
    completed: 'bg-green-100 text-green-800 border border-green-300',
    failed: 'bg-red-100 text-red-800 border border-red-300'
  }
  return classes[props.status] || 'bg-gray-100 text-gray-800 border border-gray-300'
})

const dotClasses = computed(() => {
  const classes = {
    pending: 'bg-yellow-500 animate-pulse',
    in_progress: 'bg-blue-500 animate-pulse',
    completed: 'bg-green-500',
    failed: 'bg-red-500'
  }
  return classes[props.status] || 'bg-gray-500'
})

const statusText = computed(() => {
  const texts = {
    pending: 'Pending',
    in_progress: 'In Progress',
    completed: 'Completed',
    failed: 'Failed'
  }
  return texts[props.status] || props.status
})
</script>
