<template>
  <div class="header-wrapper">
    <header class="app-header">
      <div class="header-content">
        <!-- Top Row: Title -->
        <div class="header-top-row">
          <div class="header-titles">
            <h1>தமிழ் இலக்கிய சொல் தேடல்</h1>
            <h3>Search Across Tamil Literature</h3>
          </div>
        </div>

        <!-- Database Summary -->
        <div class="database-summary">
          <span v-if="stats">{{ stats.total_works }} இலக்கிய நூல்கள் | {{ stats.distinct_words.toLocaleString() }} சொற்கள்</span>
          <span v-else>Loading statistics...</span>
          <span class="data-source-note">Data Source: <a href="http://tamilconcordance.in" target="_blank" rel="noopener noreferrer" class="concordance-link">http://tamilconcordance.in</a></span>
        </div>

        <!-- Compact Search Box -->
        <div class="header-search">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search for a word... (e.g., அறம்)"
            @keyup.enter="handleSearch"
            class="search-input"
          />
          <button
            v-if="searchQuery.trim()"
            @click="clearSearchInput"
            class="clear-button"
            title="Clear search"
          >
            ✕
          </button>
          <button @click="handleSearch" class="search-button" :disabled="!searchQuery.trim()">
            Search
          </button>
        </div>

      </div>

      <!-- Bottom Row: Navigation Tabs -->
      <div class="header-bottom-row">
        <nav class="header-nav-tabs">
          <router-link :to="{ name: 'Home' }" class="nav-tab">Acknowledgment</router-link>
          <router-link :to="{ name: 'Search' }" class="nav-tab">Search</router-link>
          <router-link v-if="isWorksBrowserVisible" :to="{ name: 'WorksList' }" class="nav-tab">Browse Works</router-link>
          <router-link :to="{ name: 'About' }" class="nav-tab">About & Help</router-link>
          <router-link :to="{ name: 'Journey' }" class="nav-tab">The Story Behind</router-link>
        </nav>
      </div>
    </header>

    <!-- Filter Options Toggle (only shown on Search page, in content area) -->
    <div v-if="isSearchPage" class="filter-toggle-wrapper">
      <button
        @click="toggleFilterOptions"
        class="filter-toggle-button"
      >
        <span>Search Options</span>
        <span class="toggle-icon">{{ filterOptionsExpanded ? '▼' : '▲' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSearchState } from '../composables/useSearchState.js'
import { useStats } from '../composables/useStats.js'

const router = useRouter()
const route = useRoute()
const searchQuery = ref('')
const filterOptionsExpanded = ref(false) // Default to closed

// Get clearSearch method from composable
const { clearSearch } = useSearchState()

// Get stats from composable (persistent across navigation)
const { stats, loadStats } = useStats()

// Check if Works Browser should be visible (only for localhost or 192.168.1.198)
const isWorksBrowserVisible = computed(() => {
  const hostname = window.location.hostname
  return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '192.168.1.198'
})

// Check if on Search page
const isSearchPage = computed(() => route.name === 'Search')

onMounted(() => {
  loadStats()
})

// Sync search box with URL query param
watch(() => route.query.q, (newQuery) => {
  if (newQuery) {
    searchQuery.value = newQuery
  } else if (route.name !== 'Search') {
    // Clear search box when navigating away from Search page
    searchQuery.value = ''
  }
}, { immediate: true })

function handleSearch() {
  if (searchQuery.value.trim()) {
    const newSearchTerm = searchQuery.value.trim()
    const currentSearchTerm = route.query.q

    // Only clear search results if the search term has changed
    if (newSearchTerm !== currentSearchTerm) {
      clearSearch()
    }

    // Close filter options when search is clicked
    filterOptionsExpanded.value = false
    window.dispatchEvent(new CustomEvent('toggle-filter-options', {
      detail: { expanded: false }
    }))

    router.push({
      name: 'Search',
      query: { q: newSearchTerm }
    })
  }
}

function clearSearchInput() {
  searchQuery.value = ''
}

function toggleFilterOptions() {
  filterOptionsExpanded.value = !filterOptionsExpanded.value

  // Scroll to top when expanding filter options
  if (filterOptionsExpanded.value) {
    // Target the .app-content scrollable container
    const appContent = document.querySelector('.app-content')
    if (appContent) {
      appContent.scrollTo({
        top: 0,
        behavior: 'smooth'
      })
    }
  }

  // Emit event to SearchControls to control visibility
  window.dispatchEvent(new CustomEvent('toggle-filter-options', {
    detail: { expanded: filterOptionsExpanded.value }
  }))
}
</script>

<style scoped>
.header-wrapper {
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 100;
  background: white;
}

.app-header {
  background: linear-gradient(135deg, #4a5f8c 0%, #2d4168 100%);
  border-bottom: 3px solid #1a2942;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
  margin: 0;
}

.header-content {
  padding: 0.5rem 2rem 0 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.header-top-row {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0;
  padding: 0;
}

.header-titles {
  text-align: center;
}

.header-bottom-row {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0;
  margin: 0;
}

.header-nav-tabs {
  display: flex;
  gap: 0;
  flex-wrap: wrap;
  justify-content: center;
}

.nav-tab {
  padding: 0.5rem 0.75rem;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease;
  white-space: nowrap;
  position: relative;
}

.nav-tab:hover {
  color: white;
  border-bottom-color: rgba(255, 255, 255, 0.5);
}

.nav-tab.router-link-active {
  color: white;
  border-bottom-color: white;
  font-weight: 600;
}

.app-header h1 {
  margin: 0;
  font-size: 1.2rem;
  color: white;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.app-header h2 {
  margin: 0.3rem 0 0 0;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 400;
}

.header-search {
  display: flex;
  gap: 0.5rem;
  max-width: 500px;
  margin: 0.5rem auto 0 auto;
  position: relative;
}

.search-input {
  flex: 1;
  padding: 0.6rem 2.5rem 0.6rem 1rem;
  font-size: 0.95rem;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #4a90e2;
}

.clear-button {
  position: absolute;
  right: 5.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: #6c757d;
  font-size: 1.3rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
  z-index: 10;
  line-height: 1;
}

.clear-button:hover {
  color: #dc3545;
}

.search-button {
  padding: 0.6rem 1.2rem;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.search-button:hover:not(:disabled) {
  background-color: #357abd;
}

.search-button:disabled {
  background-color: #adb5bd;
  cursor: not-allowed;
}

.database-summary {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0rem;
  font-size: 0.9rem;
  color: white;
  font-weight: 600;
  margin: 0.25rem 0;
}

.database-summary span {
  display: block;
}

.data-source-note {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.concordance-link {
  color: rgba(255, 255, 255, 0.95);
  text-decoration: none;
  font-weight: 500;
  border-bottom: 1px solid rgba(255, 255, 255, 0.4);
}

.concordance-link:hover {
  color: white;
  border-bottom-color: white;
}

/* Filter Toggle Wrapper (in content area) */
.filter-toggle-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 0 2rem;
  max-width: 1400px;
  margin: 0 auto;
  background: white;
}

.filter-toggle-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  border: 2px solid #4a90e2;
  border-top: none;
  border-radius: 0 0 6px 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  color: #4a90e2;
  transition: all 0.2s;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.filter-toggle-button:hover {
  background: #f8f9fa;
  color: #357abd;
  border-color: #357abd;
}

.toggle-icon {
  font-size: 0.7rem;
  font-weight: 700;
}

@media (max-width: 768px) {
  .header-content {
    padding: 0;
  }

  .filter-toggle-wrapper {
    padding: 0 1rem;
  }

  .header-top-row {
    gap: 1rem;
  }

  .app-header h1 {
    font-size: 1.0rem;
  }

  .app-header h2 {
    font-size: 0.85rem;
  }

  .header-search {
    margin-top: 0.5rem;
  }

  .search-input {
    padding: 0.5rem 0.8rem;
    font-size: 0.9rem;
  }

  .search-button {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }

  .database-summary {
    font-size: 0.7rem;
  }

  .data-source-note {
    font-size: 0.65rem;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 0.5rem 0.75rem 0 0.75rem;
  }

  .filter-toggle-wrapper {
    padding: 0 0.75rem;
  }

  .header-top-row {
    flex-direction: column;
    align-items: center;
    gap: 0.0rem;
  }

  .header-titles {
    text-align: center;
  }

  .app-header h1 {
    font-size: 0.8rem;
  }

  .app-header h2 {
    font-size: 0.75rem;
  }

  .header-search {
    width: 75%;
    max-width: 75%;
    margin-top: 0.5rem;
  }

  .search-input {
    font-size: 0.85rem;
    padding: 0.5rem 0.7rem;
  }

  .search-button {
    font-size: 0.85rem;
    padding: 0.5rem 0.8rem;
  }

  .database-summary {
    font-size: 0.75rem;
  }

  .data-source-note {
    font-size: 0.75rem;
  }
}
</style>
