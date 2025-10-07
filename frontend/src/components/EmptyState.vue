<template>
  <div class="text-center py-12">
    <slot name="icon">
      <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
      </svg>
    </slot>

    <h3 class="text-lg font-medium text-gray-900 mb-2">
      <slot name="title">No data available</slot>
    </h3>

    <p class="text-gray-600 mb-6">
      <slot name="description">Get started by creating your first item</slot>
    </p>

    <slot name="action"></slot>
  </div>
</template>