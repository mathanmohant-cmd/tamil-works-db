<template>
  <div class="search-page">
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
      <!-- Welcome Message -->
      <div v-if="!loading && !searchResults && showWelcome" class="welcome">
        <h2>Search words across Thamizh literature</h2>
        <p class="welcome-subtitle"><router-link class="acknowledgement" :to="{ name: 'Home' }">Thanks to Prof P. Pandiyaraja</router-link></p>
        <div class="try-examples">
          <h3>Try Searching: Click These Words</h3>
          <div class="example-buttons">
            <button @click="tryExampleSearch('அறம்')" class="example-btn">அறம்</button>
            <button @click="tryExampleSearch('தமிழ்நாடு')" class="example-btn">தமிழ்நாடு</button>
            <button @click="tryExampleSearch('எஃகு')" class="example-btn">எஃகு</button>
            <button @click="tryExampleSearch('தமித்து')" class="example-btn">தமித்து</button>
            <button @click="tryExampleSearch('ஈனில்')" class="example-btn">ஈனில்</button>
          </div>
        </div>

        <div class="quick-start">
          <h3>🚀 Quick Start</h3>
          <ul class="tips-list">
            <li><strong>Type a Thamizh word</strong> in the search box above</li>
            <li><strong>Choose match type:</strong> Partial (finds similar words) or Exact (precise match)</li>
            <li><strong>Set position:</strong> Beginning, End, or Anywhere in the word</li>
            <li><strong>Filter by works</strong> (optional) to search specific texts</li>
          </ul>
          <p>Understanding what a concordance is and the <strong>word segmentation principles</strong> will help you use this tool more effectively.</p>
          <p class="learn-more"><router-link class="acknowledgement" :to="{ name: 'About' }">Learn more about this tool</router-link></p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading">
        <p>Searching...</p>
      </div>

      <!-- Error State -->
      <div v-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="error = null">Dismiss</button>
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
  showWelcome,
  restoreFilters,
  loadWorks
} = useFilterState()

// Track if initialization is complete
const initialized = ref(false)

// Initialize
onMounted(async () => {
  await loadWorks()
  await restoreFilters()
  initialized.value = true

  // Perform search if query exists after initialization
  if (route.query.q && route.query.q.trim()) {
    searchQuery.value = route.query.q.trim()
    showWelcome.value = false
    await performSearch()
  }
})

// Watch route query and perform search when it changes
watch(() => route.query, async (newQuery) => {
  if (!initialized.value) return // Wait for initialization

  if (newQuery.q && newQuery.q.trim()) {
    searchQuery.value = newQuery.q.trim()
    showWelcome.value = false
    await performSearch()
  } else if (route.name === 'Search') {
    // Clear results if no query on Search page
    searchResults.value = null
    showWelcome.value = true
  }
}, { deep: true })

// Watch match type changes and trigger new search
watch(matchType, async () => {
  if (!initialized.value) return
  if (!searchResults.value) return // Only trigger if there's an active search
  await performSearch()
})

// Watch word position changes and trigger new search
watch(wordPosition, async () => {
  if (!initialized.value) return
  if (!searchResults.value) return // Only trigger if there's an active search
  await performSearch()
})

// Watch sort order changes and reload expanded words
watch(sortBy, async () => {
  if (!searchResults.value) return

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
    searchResults.value = null
    showWelcome.value = true
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

// Try example search
const tryExampleSearch = (word) => {
  // Reset search filters to defaults
  matchType.value = 'exact'
  wordPosition.value = 'beginning'

  // Clear work filters
  filterMode.value = 'all'
  selectedWorks.value = []

  // Navigate to search with query
  router.push({
    name: 'Search',
    query: { q: word }
  })
}
</script>

<style scoped>
.search-page {
  position: relative;
}

.main-container {
  max-width: 1000px;
  margin: 0 auto;
}

/* Welcome Message */
.welcome {
  max-width: 800px;
  margin: 1rem auto;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.welcome h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
  color: #2c3e50;
  text-align: center;
}

.welcome-subtitle {
  text-align: center;
  font-size: 1.1rem;
  color: #6c757d;
  margin-bottom: .5rem;
  font-style: italic;
}

.quick-start {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 6px;
}

.quick-start h3 {
  margin: 0 0 1rem 0;
  font-size: 1.3rem;
  color: #2c3e50;
}

.tips-list {
  margin: 0 0 1rem 1.5rem;
  padding: 0;
}

.tips-list li {
  margin-bottom: 0.75rem;
  line-height: 1.6;
  color: #495057;
}

.learn-more {
  margin: 1rem 0 0 0;
  text-align: center;
}

.principles-link {
  color: #4a90e2;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.05rem;
}

.principles-link:hover {
  text-decoration: underline;
}

.try-examples {
  text-align: center;
  margin-bottom: 2rem;
}

.try-examples h3 {
  margin: 0 0 1rem 0;
  font-size: .9rem;
  color: #2c3e50;
}

.example-buttons {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.example-btn {
  padding: 0.6rem 1.2rem;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: 600;
  transition: all 0.2s;
}

.example-btn:hover {
  background: #357abd;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(74, 144, 226, 0.3);
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

.acknowledgement {
  color: #0f4c81;
  text-decoration: none;
  border-bottom: 1px dotted var(--life-pulse);
  font-weight: 400;
}

.acknowledgement:hover {
  border-bottom: 1px dotted var(--life-pulse);
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .main-container {
  margin: 0 auto;
  }

  .welcome {
    padding: .25rem;
    margin: 0 0rem;
  }

  .welcome h2 {
    font-size: 1.0rem;
    margin: 0 0rem;
  }

  .welcome-subtitle {
    font-size: 1rem;
  }

  .quick-start {
    padding: .5rem;
  }

  .quick-start h3 {
    font-size: .9rem;
  }

  .tips-list {
    margin-left: 1rem;
  }

  .tips-list li {
    font-size: 0.95rem;
  }

  .example-buttons {
    gap: 0.5rem;
  }

  .example-btn {
    padding: 0.5rem 1rem;
    font-size: 1rem;
  }

  .try-examples {
  padding: .5rem;
}
}
</style>
