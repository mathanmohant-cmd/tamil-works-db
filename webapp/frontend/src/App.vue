<template>
  <div id="app">
    <!-- Header -->
    <header class="app-header">
      <h1>தமிழ் இலக்கிய சொல் தேடல் | Tamil Literary Words Search</h1>

      <!-- Database Summary -->
      <div class="database-summary" v-if="stats">
        <span>{{ stats.total_works }} Works | {{ stats.total_verses.toLocaleString() }} Verses | {{ stats.distinct_words.toLocaleString() }} Distinct Words | {{ stats.total_words.toLocaleString() }} Usage</span>
      </div>
      <div class="header-bottom">
        <div class="search-section">
          <div class="search-row">
            <div class="search-box">
              <div class="autocomplete-wrapper">
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Enter Tamil word... (e.g., அறம்)"
                  @keyup.enter="performSearch"
                  @input="handleAutocompleteInput"
                  @focus="showAutocomplete = true"
                  @blur="hideAutocomplete"
                  class="search-input"
                  autocomplete="off"
                />
                <ul v-if="showAutocomplete && autocompleteResults.length > 0" class="autocomplete-list">
                  <li
                    v-for="word in autocompleteResults"
                    :key="word.word_text"
                    @mousedown.prevent="selectAutocomplete(word.word_text)"
                    class="autocomplete-item"
                  >
                    {{ word.word_text }}
                  </li>
                </ul>
              </div>
              <button @click="performSearch" class="search-button" :disabled="loading || !searchQuery.trim()">
                {{ loading ? 'Searching...' : 'Search' }}
              </button>
              <button
                v-if="searchResults || searchQuery"
                @click="clearSearch"
                class="clear-button"
                title="Clear search"
              >
                Clear
              </button>
            </div>
          </div>
          <!-- Work Filter Radio Buttons -->
          <div class="work-filter-options">
            <div class="filter-group-inline">
              <span class="filter-label">Search in:</span>
              <label>
                <input type="radio" v-model="filterMode" value="all" @change="handleFilterModeChange" />
                All works
              </label>
              <label>
                <input type="radio" v-model="filterMode" value="select" @change="handleFilterModeChange" />
                Select from {{ works.length }} works
              </label>
            </div>
            <button v-if="filterMode === 'select'" @click="toggleFilters" class="filter-selection-button">
              {{ worksFilterButtonText }}
            </button>
          </div>
          <!-- Match Type & Word Position -->
          <div class="match-type-options">
            <div class="filter-group-inline">
              <span class="filter-label">Match:</span>
              <label>
                <input type="radio" v-model="matchType" value="partial" />
                Partial
              </label>
              <label>
                <input type="radio" v-model="matchType" value="exact" />
                Exact
              </label>
            </div>
            <div class="filter-group-inline">
              <span class="filter-label">Position:</span>
              <label>
                <input type="radio" v-model="wordPosition" value="beginning" />
                Beginning
              </label>
              <label>
                <input type="radio" v-model="wordPosition" value="end" />
                End
              </label>
              <label>
                <input type="radio" v-model="wordPosition" value="anywhere" />
                Anywhere
              </label>
            </div>
          </div>
          <!-- Navigation -->
          <nav class="main-nav">
            <button @click="currentPage = 'home'" :class="{active: currentPage === 'home'}">Home</button>
            <button @click="currentPage = 'search'" :class="{active: currentPage === 'search'}">Search</button>
            <button @click="currentPage = 'inspiration'" :class="{active: currentPage === 'inspiration'}">Our Inspiration</button>
            <button @click="currentPage = 'about'" :class="{active: currentPage === 'about'}">About Us</button>
          </nav>
        </div>
      </div>
    </header>

    <!-- Home Page -->
    <Home v-if="currentPage === 'home'" />

    <!-- Our Inspiration Page -->
    <OurInspiration v-if="currentPage === 'inspiration'" />

    <!-- About Page -->
    <About v-if="currentPage === 'about'" />

    <!-- Verse View (shown on search page) -->
    <VerseView
      v-if="currentPage === 'search' && showVerseView"
      :verseId="selectedVerseId"
      :searchWord="verseViewSearchWord"
      @close="closeVerseView"
    />

    <!-- Search Page -->
    <div v-if="currentPage === 'search' && !showVerseView" class="search-page">
    <!-- Collapsible Filters -->
    <div class="filters-panel" v-show="filtersExpanded">
      <div class="filter-group" v-if="works.length">
        <div class="filter-header">
          <label><strong>Filter by Work:</strong></label>
          <div class="filter-header-actions">
            <button @click="clearFilters" class="clear-filter-button" title="Uncheck all works">
              Clear Filter
            </button>
            <label class="remember-checkbox">
              <input type="checkbox" v-model="rememberSelection" />
              Remember for session
            </label>
            <button @click="closeFilters" class="done-button">Done</button>
          </div>
        </div>
        <div class="checkbox-group">
          <label>
            <input type="checkbox" v-model="selectAllWorks" @change="toggleAllWorks" />
            <strong>All Works</strong>
          </label>
          <label v-for="work in works" :key="work.work_id">
            <input type="checkbox" :value="work.work_id" v-model="selectedWorks" />
            {{ work.work_name_tamil }} ({{ work.work_name }})
          </label>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-container">
      <!-- Welcome Message -->
      <div v-if="!searchResults && !loading && currentPage === 'search'" class="welcome">
        <h2>Welcome to Tamil Literary Words Search</h2>
        <p>Enter a Tamil word in the search box to begin.</p>
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

      <!-- Single-Panel Collapsible Results Layout -->
      <div v-if="searchResults && !loading" class="results-layout">
        <div class="single-panel">
          <!-- Search Summary -->
          <div class="results-header">
            <div class="search-summary-panel">
              <div class="searched-word-display">Searched word: <strong>{{ searchResults.search_term }}</strong></div>
              <div>{{ searchSummary }}</div>
            </div>
            <div class="export-buttons-group">
              <button @click="showWordsExportMenu = true" class="export-button-combined" title="Export list of found words">
                📥 Export Words
              </button>
            </div>
          </div>

          <!-- Word List with Expandable Details -->
          <div class="word-list-container">
            <div
              v-for="(word, index) in uniqueWords"
              :key="word.text"
              class="word-item-expandable"
              :class="{ expanded: expandedWords.has(word.text) }"
            >
              <!-- Word Header Row -->
              <div class="word-header-row">
                <div class="word-info">
                  <span class="word-number">{{ index + 1 }}.</span>
                  <span class="word-text">{{ word.text }}</span>
                  <span class="word-count-badge">{{ word.count }}</span>
                </div>
                <div class="word-actions">
                  <a
                    :href="`https://dsal.uchicago.edu/cgi-bin/app/tamil-lex_query.py?qs=${encodeURIComponent(word.text)}&searchhws=yes&matchtype=default`"
                    target="_blank"
                    class="action-icon dictionary-icon"
                    @click.stop
                    title="Look up in Tamil Lexicon"
                  >
                    📖
                  </a>
                  <button
                    @click="toggleWordExpansion(word.text)"
                    class="expand-collapse-button"
                    :class="{ expanded: expandedWords.has(word.text) }"
                    :title="expandedWords.has(word.text) ? 'Collapse' : 'Expand'"
                  >
                    <span class="expand-icon">{{ expandedWords.has(word.text) ? '▼' : '▶' }}</span>
                  </button>
                </div>
              </div>

              <!-- Expandable Occurrences Section -->
              <div v-if="expandedWords.has(word.text)" class="word-expanded-content">
                <!-- Selected Word Summary: Works, Verses, Usage -->
                <div class="expanded-summary">
                  <div class="summary-counts">
                    <span class="summary-item">{{ getWorkCounts(word.text).length }} Work{{ getWorkCounts(word.text).length !== 1 ? 's' : '' }}</span>
                    <span class="summary-divider">|</span>
                    <span class="summary-item">{{ word.verse_count }} Verse{{ word.verse_count !== 1 ? 's' : '' }}</span>
                    <span class="summary-divider">|</span>
                    <span class="summary-item">{{ word.count }} Usage</span>
                  </div>
                  <div class="export-buttons-group">
                    <button
                      @click="showLinesExportMenu(word.text)"
                      class="export-button-combined"
                      title="Export all lines for this word"
                    >
                      📥 Export Lines
                    </button>
                  </div>
                </div>

                <!-- Loading State -->
                <div v-if="loadingWord === word.text" class="loading-occurrences">
                  Loading occurrences...
                </div>

                <!-- Occurrences List -->
                <div v-else class="occurrences-list">
                  <div
                    v-for="(result, occIndex) in getSortedWordOccurrences(word.text)"
                    :key="result.word_id"
                    class="occurrence-item"
                  >
                    <div class="occurrence-number">{{ occIndex + 1 }}</div>
                    <div class="occurrence-content">
                      <div class="occurrence-metadata">
                        <span class="work-name">{{ result.work_name_tamil }}</span>
                        <template v-if="cleanHierarchyPath(result.hierarchy_path_tamil || result.hierarchy_path)">
                          <span class="separator"> • </span>
                          <span>{{ cleanHierarchyPath(result.hierarchy_path_tamil || result.hierarchy_path) }}</span>
                        </template>
                        <span class="separator"> • </span>
                        <span>{{ formatVerseAndLine(result, false) }}</span>
                        <a href="#" @click.prevent="openVerseView(result.verse_id, word.text)" class="verse-link" title="View full verse">🔗</a>
                      </div>
                      <div class="occurrence-line" v-html="highlightWord(result.line_text, word.text)"></div>
                    </div>
                  </div>

                  <!-- Load More Button if needed -->
                  <div v-if="hasMoreOccurrences(word.text)" class="load-more-container">
                    <button
                      @click="loadMoreOccurrences(word.text)"
                      class="load-more-button"
                      :disabled="loadingWord === word.text"
                    >
                      {{ loadingWord === word.text ? 'Loading...' : 'Load More' }}
                    </button>
                  </div>
                </div>

                <!-- Collapse Button at Bottom -->
                <div class="collapse-footer">
                  <button @click="toggleWordExpansion(word.text)" class="collapse-button">
                    ▲ Collapse
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
    <!-- End Search Page -->

    <!-- Export Words Menu -->
    <div v-if="showWordsExportMenu" class="export-modal" @click="showWordsExportMenu = false">
      <div class="export-modal-content" @click.stop>
        <h3>Export Found Words</h3>
        <button @click="exportWords('csv')" class="export-modal-option">
          📊 Export as CSV
        </button>
        <button @click="showWordsExportMenu = false" class="export-modal-cancel">
          Cancel
        </button>
      </div>
    </div>

    <!-- Export Lines Menu -->
    <div v-if="currentExportWordText" class="export-modal" @click="currentExportWordText = null">
      <div class="export-modal-content" @click.stop>
        <h3>Export Lines for "{{ currentExportWordText }}"</h3>
        <button @click="exportWordLines('csv', currentExportWordText)" class="export-modal-option">
          📊 Export as CSV
        </button>
        <button @click="currentExportWordText = null" class="export-modal-cancel">
          Cancel
        </button>
      </div>
    </div>

  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import api from './api.js'
import Home from './Home.vue'
import OurInspiration from './OurInspiration.vue'
import About from './About.vue'
import VerseView from './VerseView.vue'

export default {
  name: 'App',
  components: {
    Home,
    OurInspiration,
    About,
    VerseView
  },
  setup() {
    // Page navigation
    const currentPage = ref('home')

    // State
    const searchQuery = ref('')
    const matchType = ref('partial')
    const wordPosition = ref('beginning')  // beginning, end, anywhere
    const filterMode = ref('all')  // 'all' or 'select'
    const selectedWorks = ref([])
    const selectAllWorks = ref(true)
    const rememberSelection = ref(false)
    const works = ref([])
    const searchResults = ref(null)
    const selectedWord = ref(null)
    const selectedWordText = ref(null)
    const loading = ref(false)
    const error = ref(null)
    const stats = ref(null)
    const offset = ref(0)
    const filtersExpanded = ref(false)
    const autocompleteResults = ref([])
    const showAutocomplete = ref(false)
    let autocompleteTimeout = null
    const expandedWords = ref(new Set())
    const loadingWord = ref(null)
    const loadedOccurrences = ref({}) // Track loaded occurrences per word with offset
    const initialSearchSummary = ref(null) // Store initial search summary

    // Verse view state
    const showVerseView = ref(false)
    const selectedVerseId = ref(null)
    const verseViewSearchWord = ref('')

    // Export menu state
    const showWordsExportMenu = ref(false)
    const currentExportWordText = ref(null)

    // Load initial data
    onMounted(async () => {
      try {
        // Load works
        const worksResponse = await api.getWorks()
        works.value = worksResponse.data

        // Check for saved selection in session storage
        const savedSelection = sessionStorage.getItem('selectedWorks')
        const savedMode = sessionStorage.getItem('filterMode')
        const savedRemember = sessionStorage.getItem('rememberSelection')

        if (savedRemember === 'true' && savedSelection) {
          selectedWorks.value = JSON.parse(savedSelection)
          filterMode.value = savedMode || 'all'
          rememberSelection.value = true
        } else {
          selectedWorks.value = works.value.map(w => w.work_id)
          filterMode.value = 'all'
        }

        // Load stats
        const statsResponse = await api.getStatistics()
        stats.value = statsResponse.data
      } catch (err) {
        error.value = 'Failed to load initial data: ' + err.message
      }
    })

    // Watch for selectAllWorks changes
    watch(selectAllWorks, (newVal) => {
      if (newVal) {
        selectedWorks.value = works.value.map(w => w.work_id)
      }
    })

    watch(selectedWorks, (newVal) => {
      selectAllWorks.value = newVal.length === works.value.length
      // Clear search results when filter changes if we have active search
      if (searchResults.value && searchQuery.value) {
        // Auto-search with new filter selection
        performSearch()
      }
    })

    // Note: We no longer auto-clear on empty searchQuery since we have a dedicated Clear button

    // Methods
    const toggleAllWorks = () => {
      if (selectAllWorks.value) {
        selectedWorks.value = works.value.map(w => w.work_id)
      } else {
        selectedWorks.value = []
      }
    }

    const clearSearch = () => {
      // Clear all search state
      searchResults.value = null
      searchQuery.value = ''
      error.value = null
      expandedWords.value = new Set()
      loadedOccurrences.value = {}
      selectedWord.value = null
      selectedWordText.value = null
      initialSearchSummary.value = null
    }

    const performSearch = async () => {
      // Trim the search query to remove leading/trailing spaces
      const trimmedQuery = searchQuery.value.trim()

      if (!trimmedQuery) {
        error.value = 'Please enter a search term'
        return
      }

      // Switch to search page to show results
      currentPage.value = 'search'

      loading.value = true
      error.value = null
      offset.value = 0
      expandedWords.value = new Set() // Reset expanded words on new search
      loadedOccurrences.value = {} // Reset loaded occurrences

      try {
        // If no works are selected, show empty results
        if (selectedWorks.value.length === 0) {
          searchResults.value = {
            results: [],
            unique_words: [],
            total_count: 0,
            limit: 100,
            offset: 0,
            search_term: trimmedQuery,
            match_type: matchType.value,
            word_position: wordPosition.value
          }
          initialSearchSummary.value = null
          loading.value = false
          return
        }

        const params = {
          q: trimmedQuery,
          match_type: matchType.value,
          word_position: wordPosition.value,
          limit: 0, // Don't load any results initially, just get unique_words
          offset: 0
        }

        if (selectedWorks.value.length > 0 && selectedWorks.value.length < works.value.length) {
          params.work_ids = selectedWorks.value.join(',')
        }

        const response = await api.searchWords(params)
        searchResults.value = {
          ...response.data,
          results: [] // Start with empty results
        }

        // Don't store summary - let it update on each search
        initialSearchSummary.value = null

        selectedWord.value = null
        selectedWordText.value = null
      } catch (err) {
        error.value = 'Search failed: ' + err.message
        searchResults.value = null
        initialSearchSummary.value = null
      } finally {
        loading.value = false
      }
    }

    const loadMore = async () => {
      if (loading.value) return

      loading.value = true
      offset.value += 100

      try {
        const params = {
          q: searchQuery.value.trim(),
          match_type: matchType.value,
          word_position: wordPosition.value,
          limit: 100,
          offset: offset.value
        }

        if (selectedWorks.value.length > 0 && selectedWorks.value.length < works.value.length) {
          params.work_ids = selectedWorks.value.join(',')
        }

        const response = await api.searchWords(params)

        // Preserve unique_words and total_count from initial search
        // Only append new results to the results array
        searchResults.value.results.push(...response.data.results)
        // Don't update unique_words or total_count as they should remain constant
      } catch (err) {
        error.value = 'Failed to load more results: ' + err.message
      } finally {
        loading.value = false
      }
    }

    const selectWord = (word) => {
      selectedWord.value = word
    }

    const selectWordFromList = async (wordText) => {
      selectedWordText.value = wordText
      selectedWord.value = null  // Clear individual line selection

      // Check if we need to load more results for this word
      if (!searchResults.value || !searchResults.value.results) return

      const currentWordResults = searchResults.value.results.filter(
        result => result.word_text === wordText
      )

      // Get the count from unique_words
      const wordInfo = searchResults.value.unique_words?.find(w => w.word_text === wordText)
      const totalCount = wordInfo?.count || currentWordResults.length

      // If we already have all occurrences loaded, just scroll to top
      if (currentWordResults.length >= totalCount) {
        scrollToLinesPanel()
        return
      }

      // Load all occurrences of this specific word from backend
      loading.value = true
      error.value = null
      try {
        const params = {
          q: wordText,
          match_type: 'exact',
          limit: 500,
          offset: 0
        }

        if (selectedWorks.value.length > 0 && selectedWorks.value.length < works.value.length) {
          params.work_ids = selectedWorks.value.join(',')
        }

        const response = await api.searchWords(params)

        // Merge new results with existing results, preserving unique_words
        const existingResults = searchResults.value.results.filter(
          r => r.word_text !== wordText
        )

        searchResults.value = {
          ...searchResults.value,
          results: [...existingResults, ...response.data.results],
          total_count: searchResults.value.total_count
          // Keep original unique_words and search_term
        }

        scrollToLinesPanel()
      } catch (err) {
        error.value = 'Failed to load word occurrences: ' + err.message
      } finally {
        loading.value = false
      }
    }

    const scrollToLinesPanel = () => {
      // Scroll to top of lines panel
      setTimeout(() => {
        const linesPanel = document.querySelector('.results-section')
        if (linesPanel) {
          linesPanel.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      }, 100)
    }

    // Computed: Get unique words with counts from backend (already sorted)
    const uniqueWords = computed(() => {
      if (!searchResults.value) return []

      // ALWAYS use backend's unique_words if available (includes complete counts and work breakdown)
      if (searchResults.value.unique_words && Array.isArray(searchResults.value.unique_words) && searchResults.value.unique_words.length > 0) {
        console.log('Using backend unique_words:', searchResults.value.unique_words.length, 'words')
        return searchResults.value.unique_words.map(word => ({
          text: word.word_text,
          count: word.count, // Usage count (total occurrences)
          verse_count: word.verse_count || 0, // Verse count
          work_breakdown: word.work_breakdown || [] // Include work breakdown from backend
        }))
      }

      // Fallback: compute from results if unique_words not available (NOT RECOMMENDED - counts will be wrong!)
      console.warn('Fallback: Computing word counts from paginated results - counts may be incomplete!')
      if (!searchResults.value.results) return []

      const wordMap = {}
      searchResults.value.results.forEach(result => {
        const text = result.word_text
        if (wordMap[text]) {
          wordMap[text].count++
        } else {
          wordMap[text] = { text, count: 1, verse_count: 0, work_breakdown: [] }
        }
      })

      return Object.values(wordMap).sort((a, b) => a.text.localeCompare(b.text, 'ta'))
    })

    // Computed: Filter results by selected word
    const filteredResults = computed(() => {
      if (!searchResults.value || !searchResults.value.results) return []

      if (!selectedWordText.value) {
        return searchResults.value.results
      }

      return searchResults.value.results.filter(
        result => result.word_text === selectedWordText.value
      )
    })

    // Computed: Check if custom filter is active
    const hasCustomFilter = computed(() => {
      return selectedWorks.value.length > 0 && selectedWorks.value.length < works.value.length
    })

    // Computed: Works indicator text for filter button
    const worksFilterButtonText = computed(() => {
      if (filterMode.value === 'all' || selectedWorks.value.length === works.value.length) {
        return 'All works'
      }
      return `${selectedWorks.value.length}/${works.value.length} works selected - Change selection`
    })

    // Computed: Get filter button text
    const getFilterButtonText = computed(() => {
      if (filtersExpanded.value) {
        return '▼ Hide filters'
      }
      return '▶ Show filters'
    })

    // Computed: Found Words Summary (format: X Works | Y Verses | Z Distinct Words | W Usage)
    const searchSummary = computed(() => {
      if (!searchResults.value || !searchResults.value.unique_words) return ''

      const distinctWords = searchResults.value.unique_words.length
      const totalUsage = searchResults.value.total_count || 0

      // Count works and verses from unique_words
      const worksSet = new Set()
      let totalVerses = 0

      searchResults.value.unique_words.forEach(word => {
        // Add verse count
        totalVerses += word.verse_count || 0

        // Count works from work_breakdown
        if (word.work_breakdown) {
          word.work_breakdown.forEach(wb => {
            worksSet.add(wb.work_name)
          })
        }
      })

      const worksCount = worksSet.size

      return `${worksCount} Work${worksCount !== 1 ? 's' : ''} | ${totalVerses.toLocaleString()} Verse${totalVerses !== 1 ? 's' : ''} | ${distinctWords} Distinct Word${distinctWords !== 1 ? 's' : ''} | ${totalUsage.toLocaleString()} Usage`
    })

    // Method: Toggle filters
    const toggleFilters = () => {
      filtersExpanded.value = !filtersExpanded.value
    }

    // Method: Close filters
    const closeFilters = () => {
      filtersExpanded.value = false

      // Save to session storage if remember is checked
      if (rememberSelection.value) {
        sessionStorage.setItem('selectedWorks', JSON.stringify(selectedWorks.value))
        sessionStorage.setItem('filterMode', filterMode.value)
        sessionStorage.setItem('rememberSelection', 'true')
      } else {
        sessionStorage.removeItem('selectedWorks')
        sessionStorage.removeItem('filterMode')
        sessionStorage.removeItem('rememberSelection')
      }
    }

    const clearFilters = () => {
      selectedWorks.value = []
      selectAllWorks.value = false
    }

    // Method: Handle filter mode change
    const handleFilterModeChange = () => {
      if (filterMode.value === 'all') {
        selectedWorks.value = works.value.map(w => w.work_id)
        selectAllWorks.value = true
      } else {
        // Switch to select mode - uncheck all by default
        selectedWorks.value = []
        selectAllWorks.value = false
        // Switch to search page and open filters panel for selection
        currentPage.value = 'search'
        filtersExpanded.value = true
      }
    }

    // Method: Highlight word in line text
    const highlightWord = (lineText, wordToHighlight) => {
      if (!lineText || !wordToHighlight) return lineText

      // Escape HTML special characters in the line text
      const escapeHtml = (text) => {
        const div = document.createElement('div')
        div.textContent = text
        return div.innerHTML
      }

      const escapedLineText = escapeHtml(lineText)

      // Find and wrap the word in a highlight span
      const regex = new RegExp(`(${wordToHighlight})`, 'g')
      return escapedLineText.replace(regex, '<span class="word-highlight">$1</span>')
    }

    // Method: Export words to CSV
    const exportWords = (format) => {
      showWordsExportMenu.value = false
      if (!uniqueWords.value || uniqueWords.value.length === 0) return

      if (format === 'csv') {
        exportWordsToCSV()
      }
    }

    // Method: Show lines export menu
    const showLinesExportMenu = (wordText) => {
      currentExportWordText.value = wordText
    }

    // Method: Export words to CSV
    const exportWordsToCSV = () => {
      if (!uniqueWords.value || uniqueWords.value.length === 0) return

      // Get search details
      const searchTerm = searchResults.value.search_term || searchQuery.value.trim()
      const totalWords = uniqueWords.value.length
      const totalUsage = searchResults.value.total_count || 0

      // Count works and verses
      const worksSet = new Set()
      let totalVerses = 0
      searchResults.value.unique_words.forEach(word => {
        totalVerses += word.verse_count || 0
        if (word.work_breakdown) {
          word.work_breakdown.forEach(wb => worksSet.add(wb.work_name))
        }
      })

      // Create CSV content
      const headers = ['Word', 'Usage Count']
      const rows = uniqueWords.value.map(word => [word.text, word.count])

      const csvContent = [
        '"Data Source: tamilconcordence.in"',
        '"Compiled by: Prof. Dr. P. Pandiyaraja"',
        '',
        `"Search Term: ${searchTerm}"`,
        `"Match Type: ${matchType.value}"`,
        `"Word Position: ${wordPosition.value}"`,
        `"Total Works Found: ${worksSet.size}"`,
        `"Total Verses Found: ${totalVerses}"`,
        `"Distinct Words Found: ${totalWords}"`,
        `"Total Usage Count: ${totalUsage}"`,
        '',
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
      ].join('\n')

      // Create and download file
      const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `tamil_words_${searchTerm}_${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }


    // Method: Export lines to CSV
    const exportLinesToCSV = () => {
      if (!filteredResults.value || filteredResults.value.length === 0) return

      // Create CSV content with work/hierarchy in one column and line in another
      const headers = ['Work & Location', 'Line']
      const rows = filteredResults.value.map(result => {
        const location = `${result.work_name_tamil}: ${result.hierarchy_path_tamil || result.hierarchy_path} | Verse ${result.verse_number}, Line ${result.line_number}`
        return [location, result.line_text]
      })

      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
      ].join('\n')

      // Create and download file
      const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `tamil_lines_${selectedWordText.value}_${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }

    // Method: Handle autocomplete input
    const handleAutocompleteInput = async () => {
      const query = searchQuery.value.trim()

      if (query.length < 1) {
        autocompleteResults.value = []
        return
      }

      // Debounce autocomplete requests
      if (autocompleteTimeout) {
        clearTimeout(autocompleteTimeout)
      }

      autocompleteTimeout = setTimeout(async () => {
        try {
          const params = {
            q: query,
            match_type: 'partial',
            word_position: 'beginning',
            limit: 10,
            offset: 0
          }

          const response = await api.searchWords(params)

          // Get unique words for autocomplete
          if (response.data.unique_words && Array.isArray(response.data.unique_words)) {
            autocompleteResults.value = response.data.unique_words.slice(0, 10)
          } else {
            autocompleteResults.value = []
          }
        } catch (err) {
          autocompleteResults.value = []
        }
      }, 300)
    }

    // Method: Select autocomplete item
    const selectAutocomplete = (word) => {
      searchQuery.value = word
      autocompleteResults.value = []
      showAutocomplete.value = false
      performSearch()
    }

    // Method: Hide autocomplete
    const hideAutocomplete = () => {
      setTimeout(() => {
        showAutocomplete.value = false
      }, 200)
    }

    // Method: Toggle word expansion
    const toggleWordExpansion = async (wordText) => {
      if (expandedWords.value.has(wordText)) {
        // Collapse
        const newSet = new Set(expandedWords.value)
        newSet.delete(wordText)
        expandedWords.value = newSet
      } else {
        // Expand - load first batch if not already loaded
        const newSet = new Set(expandedWords.value)
        newSet.add(wordText)
        expandedWords.value = newSet

        // Initialize tracking for this word if not exists
        if (!loadedOccurrences.value[wordText]) {
          loadedOccurrences.value[wordText] = {
            offset: 0,
            hasMore: true
          }
        }

        // Check if we have any occurrences loaded for this word
        const currentWordResults = searchResults.value.results.filter(
          result => result.word_text === wordText
        )

        if (currentWordResults.length === 0) {
          // Load first batch (100 occurrences)
          await loadMoreOccurrences(wordText)
        }
      }
    }

    // Method: Load more occurrences for a specific word
    const loadMoreOccurrences = async (wordText) => {
      if (loadingWord.value === wordText) return

      loadingWord.value = wordText
      try {
        const tracking = loadedOccurrences.value[wordText] || { offset: 0, hasMore: true }

        const params = {
          q: wordText,
          match_type: 'exact',
          limit: 100,
          offset: tracking.offset
        }

        if (selectedWorks.value.length > 0 && selectedWorks.value.length < works.value.length) {
          params.work_ids = selectedWorks.value.join(',')
        }

        const response = await api.searchWords(params)

        // Append new results to existing results (don't remove existing ones for this word)
        const newResults = response.data.results || []

        searchResults.value = {
          ...searchResults.value,
          results: [...searchResults.value.results, ...newResults]
        }

        // Update tracking
        loadedOccurrences.value[wordText] = {
          offset: tracking.offset + newResults.length,
          hasMore: newResults.length === 100 // If we got 100, there might be more
        }
      } catch (err) {
        error.value = 'Failed to load word occurrences: ' + err.message
      } finally {
        loadingWord.value = null
      }
    }

    // Method: Get occurrences for a specific word (sorted by work name)
    const getWordOccurrences = (wordText) => {
      if (!searchResults.value || !searchResults.value.results) return []
      return searchResults.value.results.filter(result => result.word_text === wordText)
    }

    // Method: Get sorted occurrences for a specific word
    const getSortedWordOccurrences = (wordText) => {
      const occurrences = getWordOccurrences(wordText)
      return occurrences.sort((a, b) => {
        // Sort by work name (Tamil), then by verse number, then by line number
        const workCompare = (a.work_name_tamil || a.work_name).localeCompare(
          b.work_name_tamil || b.work_name,
          'ta'
        )
        if (workCompare !== 0) return workCompare

        const verseCompare = a.verse_number - b.verse_number
        if (verseCompare !== 0) return verseCompare

        return a.line_number - b.line_number
      })
    }

    // Method: Check if there are more occurrences to load
    const hasMoreOccurrences = (wordText) => {
      const tracking = loadedOccurrences.value[wordText]
      if (!tracking) return false

      const wordInfo = searchResults.value.unique_words?.find(w => w.word_text === wordText)
      const totalCount = wordInfo?.count || 0
      const loadedCount = getWordOccurrences(wordText).length

      return loadedCount < totalCount && tracking.hasMore
    }

    // Method: Get work counts for a specific word (from backend data, not loaded results)
    const getWorkCounts = (wordText) => {
      // Get work breakdown from unique_words (which has complete counts from backend)
      const wordInfo = searchResults.value.unique_words?.find(w => w.word_text === wordText)

      if (wordInfo && wordInfo.work_breakdown) {
        // Aggregate work_breakdown to get unique works with summed counts
        const workCounts = {}
        wordInfo.work_breakdown.forEach(item => {
          const workName = item.work_name
          if (!workCounts[workName]) {
            workCounts[workName] = {
              work_name: item.work_name,
              work_name_tamil: item.work_name_tamil,
              count: 0
            }
          }
          workCounts[workName].count += item.count
        })

        // Return unique works sorted alphabetically by Tamil name
        return Object.values(workCounts).sort((a, b) =>
          (a.work_name_tamil || a.work_name).localeCompare(
            b.work_name_tamil || b.work_name,
            'ta'
          )
        )
      }

      // Fallback: calculate from loaded occurrences (not recommended)
      const occurrences = getWordOccurrences(wordText)
      const workCounts = {}

      occurrences.forEach(result => {
        const workName = result.work_name
        const workNameTamil = result.work_name_tamil
        if (!workCounts[workName]) {
          workCounts[workName] = {
            work_name: workName,
            work_name_tamil: workNameTamil,
            count: 0
          }
        }
        workCounts[workName].count++
      })

      // Convert to array and sort alphabetically by Tamil name
      return Object.values(workCounts).sort((a, b) =>
        (a.work_name_tamil || a.work_name).localeCompare(
          b.work_name_tamil || b.work_name,
          'ta'
        )
      )
    }

    // Method: Clean hierarchy path - remove section type labels, keep only section names
    // If there's only one section, hide it from display
    const cleanHierarchyPath = (path) => {
      if (!path) return ''

      // Split by ' > ' to get each level
      const levels = path.split(' > ')

      // If there's only one section level, return empty (hide it)
      if (levels.length === 1) {
        return ''
      }

      // Clean each level - remove the "type:" prefix and keep only the name
      const cleanedLevels = levels.map(level => {
        // Split by ':' to separate level_type and section_name
        const parts = level.split(':')
        if (parts.length === 2) {
          // Return only the section name (part after the colon)
          return parts[1].trim()
        }
        // If no colon, return as-is
        return level.trim()
      })

      return cleanedLevels.join(' > ')
    }

    // Method: Format verse and line display with Tamil terminology
    // Order: Verse first, then Line (to follow hierarchy: sections > verse > line)
    const formatVerseAndLine = (result, includeLink = false) => {
      const hasHierarchy = result.hierarchy_path_tamil || result.hierarchy_path
      // Use verse_type_tamil first, fall back to verse_type, then default to 'பாடல்'
      const verseTypeTamil = result.verse_type_tamil || result.verse_type || 'பாடல்'

      // If there's no hierarchy (no sections), just show line number with அடி
      if (!hasHierarchy) {
        return `அடி ${result.line_number}`
      }

      // Show: verse_type_tamil verse_number > அடி line_number
      return `${verseTypeTamil} ${result.verse_number} > அடி ${result.line_number}`
    }

    // Method: Open verse view
    const openVerseView = (verseId, searchWord = '') => {
      selectedVerseId.value = verseId
      verseViewSearchWord.value = searchWord
      showVerseView.value = true
    }

    // Method: Close verse view
    const closeVerseView = () => {
      showVerseView.value = false
      selectedVerseId.value = null
      verseViewSearchWord.value = ''
    }

    // Method: Export lines for a specific word (CSV)
    const exportWordLines = (format, wordText) => {
      currentExportWordText.value = null
      if (format === 'csv') {
        exportWordLinesToCSV(wordText)
      }
    }

    // Method: Export lines for a specific word to CSV
    const exportWordLinesToCSV = (wordText) => {
      const occurrences = getWordOccurrences(wordText)
      if (occurrences.length === 0) return

      // Get word details
      const wordInfo = searchResults.value.unique_words?.find(w => w.word_text === wordText)
      const usageCount = wordInfo?.count || occurrences.length
      const verseCount = wordInfo?.verse_count || 0

      // Get work breakdown
      const workCounts = getWorkCounts(wordText)
      const worksList = workCounts.map(w => `${w.work_name_tamil} (${w.count})`).join(', ')

      // Create CSV content
      const headers = ['Work & Location', 'Line']
      const rows = occurrences.map(result => {
        const hierarchyPath = cleanHierarchyPath(result.hierarchy_path_tamil || result.hierarchy_path)
        const location = hierarchyPath
          ? `${result.work_name_tamil} • ${hierarchyPath} • ${formatVerseAndLine(result, false)}`
          : `${result.work_name_tamil} • ${formatVerseAndLine(result, false)}`
        return [location, result.line_text]
      })

      const csvContent = [
        '"Data Source: tamilconcordence.in"',
        '"Compiled by: Prof. Dr. P. Pandiyaraja"',
        '',
        `"Search Term: ${searchResults.value.search_term || searchQuery.value.trim()}"`,
        `"Found Word: ${wordText}"`,
        `"Total Works: ${workCounts.length}"`,
        `"Total Verses: ${verseCount}"`,
        `"Total Usage: ${usageCount}"`,
        `"Works: ${worksList}"`,
        '',
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
      ].join('\n')

      // Create and download file
      const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `tamil_lines_${wordText}_${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }


    return {
      currentPage,
      searchQuery,
      matchType,
      wordPosition,
      filterMode,
      selectedWorks,
      selectAllWorks,
      rememberSelection,
      works,
      searchResults,
      selectedWord,
      selectedWordText,
      loading,
      error,
      stats,
      filtersExpanded,
      uniqueWords,
      filteredResults,
      hasCustomFilter,
      worksFilterButtonText,
      getFilterButtonText,
      searchSummary,
      toggleAllWorks,
      clearSearch,
      performSearch,
      loadMore,
      selectWord,
      selectWordFromList,
      toggleFilters,
      closeFilters,
      clearFilters,
      handleFilterModeChange,
      highlightWord,
      exportWords,
      exportWordsToCSV,
      exportLinesToCSV,
      exportWordLines,
      exportWordLinesToCSV,
      autocompleteResults,
      showAutocomplete,
      handleAutocompleteInput,
      selectAutocomplete,
      hideAutocomplete,
      expandedWords,
      loadingWord,
      toggleWordExpansion,
      getWordOccurrences,
      getSortedWordOccurrences,
      hasMoreOccurrences,
      loadMoreOccurrences,
      getWorkCounts,
      cleanHierarchyPath,
      formatVerseAndLine,
      showVerseView,
      selectedVerseId,
      verseViewSearchWord,
      openVerseView,
      closeVerseView,
      showWordsExportMenu,
      currentExportWordText,
      showLinesExportMenu
    }
  }
}
</script>
