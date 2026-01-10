import { ref } from 'vue'
import api from '../api.js'

// Global state - persists across component instances
const stats = ref(null)
const loading = ref(false)

export function useStats() {
  const loadStats = async () => {
    // Only load if not already loaded and not currently loading
    if (!stats.value && !loading.value) {
      loading.value = true
      try {
        const response = await api.getStatistics()
        stats.value = response.data
      } catch (err) {
        console.error('Failed to load stats:', err)
      } finally {
        loading.value = false
      }
    }
  }

  return {
    stats,
    loading,
    loadStats
  }
}
