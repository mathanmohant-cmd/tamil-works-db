<template>
  <div class="search-results-page">
    <!-- VerseView Overlay -->
    <VerseView
      v-if="showVerseView"
      :verseId="selectedVerseId"
      :searchWord="verseViewSearchWord"
      @close="closeVerseView"
    />

    <!-- Search Controls -->
    <SearchControls v-if="!showVerseView" />

    <!-- Main Content Area -->
    <div v-if="!showVerseView" class="main-container">
      <!-- Loading State -->
      <div v-if="loading" class="loading">
        <p>Searching...</p>
      </div>

      <!-- Error State -->
      <div v-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="error = null">Dismiss</button>
      </div>

      <!-- No Results Message -->
      <div v-if="!loading && !error && searchResults && searchResults.unique_words && searchResults.unique_words.length === 0" class="no-results">
        <p>No results found for "{{ searchQuery }}"</p>
      </div>

      <!-- Search Results -->
      <SearchResults v-if="!loading && searchResults" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSearchState } from '../composables/useSearchState.js'
import { useFilterState } from '../composables/useFilterState.js'
import SearchControls from '../components/search/SearchControls.vue'
import SearchResults from '../components/search/SearchResults.vue'
import VerseView from '../VerseView.vue'
import api from '../api.js'

const router = useRouter()
const route = useRoute()

// Use composables
const {
  searchQuery,
  matchType,
  wordPosition,
  sortBy,
  searchResults,
  loading,
  error,
  expandedWords,
  loadedOccurrences,
  sortingWord,
  showVerseView,
  selectedVerseId,
  verseViewSearchWord,
  closeVerseView
} = useSearchState()

const {
  filterMode,
  selectedWorks,
  restoreFilters,
  loadWorks,
  markFiltersAsSearched
} = useFilterState()

// Track if initialization is complete
const initialized = ref(false)

// Initialize
onMounted(async () => {
  // Redirect to /search if no query parameter exists
  if (!route.query.q || !route.query.q.trim()) {
    router.replace({ name: 'QuickStart' })
    return
  }

  await loadWorks()
  await restoreFilters()

  // Sync filter state from URL
  syncFiltersFromURL()

  initialized.value = true

  // Perform search with URL query
  const newSearchQuery = route.query.q.trim()

  // Check if we already have cached results for this exact query
  const needsSearch = !searchResults.value ||
    searchResults.value.search_term !== newSearchQuery ||
    matchType.value !== route.query.type ||
    wordPosition.value !== route.query.pos

  searchQuery.value = newSearchQuery

  // Only search if we don't have cached results
  if (needsSearch) {
    await performSearch()
  }
})

// Sync filter state from URL query params
const syncFiltersFromURL = () => {
  if (route.query.type) {
    matchType.value = route.query.type
  }
  if (route.query.pos) {
    wordPosition.value = route.query.pos
  }
  if (route.query.sort) {
    sortBy.value = route.query.sort
  }
}

// Watch route query and perform search when it changes
watch(() => route.query, async (newQuery, oldQuery) => {
  if (!initialized.value) return // Wait for initialization

  // Redirect to /search if no query
  if (!newQuery.q || !newQuery.q.trim()) {
    router.replace({ name: 'QuickStart' })
    return
  }

  // Sync filters from URL
  syncFiltersFromURL()

  // Perform search if query or filters changed
  const newSearchQuery = newQuery.q.trim()
  const queryChanged = newSearchQuery !== searchQuery.value
  const typeChanged = oldQuery && newQuery.type !== oldQuery.type
  const posChanged = oldQuery && newQuery.pos !== oldQuery.pos
  const timestampChanged = oldQuery && newQuery._t !== oldQuery._t

  if (queryChanged || typeChanged || posChanged || timestampChanged) {
    searchQuery.value = newSearchQuery
    await performSearch()
  }
}, { deep: true })

// Watch match type changes and update URL (which triggers search via route watcher)
watch(matchType, async (newType) => {
  if (!initialized.value) return
  if (!searchResults.value) return // Only trigger if there's an active search

  // Update URL with new match type
  router.push({
    name: 'SearchResults',
    query: {
      ...route.query,
      type: newType
    }
  })
})

// Watch word position changes and update URL (which triggers search via route watcher)
watch(wordPosition, async (newPosition) => {
  if (!initialized.value) return
  if (!searchResults.value) return // Only trigger if there's an active search

  // Update URL with new word position
  router.push({
    name: 'SearchResults',
    query: {
      ...route.query,
      pos: newPosition
    }
  })
})

// Watch sort order changes and reload expanded words
watch(sortBy, async (newSort) => {
  if (!searchResults.value) return

  // Update URL with new sort order
  router.push({
    name: 'SearchResults',
    query: {
      ...route.query,
      sort: newSort
    }
  })

  // Get list of currently expanded words
  const wordsToReload = Array.from(expandedWords.value)

  if (wordsToReload.length > 0) {
    // Clear loaded occurrences and reload with new sort order
    for (const wordText of wordsToReload) {
      // Mark as sorting (not loading more)
      sortingWord.value = wordText

      // Clear existing occurrences for this word
      if (searchResults.value && searchResults.value.results) {
        searchResults.value.results = searchResults.value.results.filter(
          r => r.word_text !== wordText
        )
      }

      // Reset tracking
      delete loadedOccurrences.value[wordText]

      // Reload with new sort order
      await loadWordOccurrences(wordText)

      // Clear sorting state
      sortingWord.value = null
    }
  }
})

// Perform search
const performSearch = async () => {
  const trimmedQuery = searchQuery.value.trim()
  if (!trimmedQuery) {
    router.replace({ name: 'QuickStart' })
    return
  }

  loading.value = true
  error.value = null
  expandedWords.value = new Set()
  loadedOccurrences.value = {}

  try {
    const params = {
      q: trimmedQuery,
      match_type: matchType.value,
      word_position: wordPosition.value,
      limit: 0, // Initial search: get word counts only
      sort_by: sortBy.value
    }

    if (filterMode.value === 'select' && selectedWorks.value.length > 0) {
      params.work_ids = selectedWorks.value.join(',')
    }

    const response = await api.searchWords(params)
    searchResults.value = response.data

    // Ensure results array exists (even if empty)
    if (!searchResults.value.results) {
      searchResults.value.results = []
    }

    // Mark filters as searched (for change detection)
    markFiltersAsSearched()

    // Scroll to results
    setTimeout(() => {
      const resultsSection = document.querySelector('.results-layout')
      if (resultsSection) {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }, 100)

  } catch (err) {
    console.error('Search error:', err)
    error.value = err.response?.data?.detail || 'Search failed. Please try again.'
  } finally {
    loading.value = false
  }
}

// Load occurrences for a specific word
const loadWordOccurrences = async (wordText) => {
  try {
    const params = {
      q: searchResults.value.search_term,
      match_type: matchType.value,
      word_position: wordPosition.value,
      limit: 100,
      offset: 0,
      sort_by: sortBy.value,
      word_text: wordText
    }

    if (filterMode.value === 'select' && selectedWorks.value.length > 0) {
      params.work_ids = selectedWorks.value.join(',')
    }

    const response = await api.searchWords(params)
    const newResults = response.data.results || []

    // Append to search results
    if (searchResults.value && searchResults.value.results) {
      // Filter out any existing results for this word
      const existingResults = searchResults.value.results.filter(r => r.word_text !== wordText)
      searchResults.value.results = [...existingResults, ...newResults]
    } else {
      searchResults.value.results = newResults
    }

    // Update tracking
    loadedOccurrences.value[wordText] = {
      offset: newResults.length,
      hasMore: newResults.length === 100
    }
  } catch (err) {
    console.error('Failed to load word occurrences:', err)
  }
}
</script>

<style scoped>
.search-results-page {
  position: relative;
}

.main-container {
  max-width: 1000px;
  margin: 0 auto;
}

/* Loading State */
.loading {
  text-align: center;
  padding: 3rem;
  font-size: 1.2rem;
  color: #6c757d;
}

/* Error State */
.error {
  max-width: 600px;
  margin: 2rem auto;
  padding: 1.5rem;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 6px;
  color: #721c24;
  text-align: center;
}

.error button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #721c24;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}

.error button:hover {
  background: #5a161c;
}

/* No Results */
.no-results {
  max-width: 600px;
  margin: 2rem auto;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  font-size: 1.1rem;
  color: #6c757d;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .main-container {
    margin: 0 auto;
  }
}
</style>
