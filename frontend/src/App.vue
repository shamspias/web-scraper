<template>
  <div id="app" class="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-gray-50">
    <router-view/>
  </div>
</template>

<script setup>
import {onMounted} from 'vue'
import {useScraperStore} from './stores/scraper'

const scraperStore = useScraperStore()

onMounted(() => {
  scraperStore.checkApiHealth()
})
</script>
