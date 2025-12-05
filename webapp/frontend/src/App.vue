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
              <button @click="performSearch" class="search-button" :disabled="loading">
                {{ loading ? 'Searching...' : 'Search' }}
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

    <!-- Search Page -->
    <div v-if="currentPage === 'search'" class="search-page">
    <!-- Collapsible Filters -->
    <div class="filters-panel" v-show="filtersExpanded">
      <div class="filter-group" v-if="works.length">
        <div class="filter-header">
          <label><strong>Filter by Work:</strong></label>
          <div class="filter-header-actions">
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

      <!-- Two-Panel Results Layout -->
      <div v-if="searchResults && !loading" class="results-layout">
        <!-- Left Panel: Word List -->
        <aside class="word-list-panel">
          <div class="word-table-container">
            <div class="table-toolbar">
              <span class="search-summary-panel">{{ searchSummary }}</span>
              <button @click="exportWordsToCSV" class="export-button-icon" title="Export list of found words to CSV">
                📥
              </button>
            </div>
            <table class="word-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Word</th>
                  <th>Dict</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(word, index) in uniqueWords"
                  :key="word.text"
                  class="word-row"
                  :class="{ active: selectedWordText === word.text }"
                  @click="selectWordFromList(word.text)"
                >
                  <td class="word-number">{{ index + 1 }}</td>
                  <td class="word-text">
                    {{ word.text }} <span class="word-count-bracket">({{ word.count }})</span>
                  </td>
                  <td class="dictionary-cell">
                    <a
                      :href="`https://dsal.uchicago.edu/cgi-bin/app/tamil-lex_query.py?qs=${encodeURIComponent(word.text)}&searchhws=yes&matchtype=default`"
                      target="_blank"
                      class="dictionary-link"
                      @click.stop
                      title="Look up in Tamil Lexicon"
                    >
                      📖
                    </a>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </aside>

        <!-- Right Panel: Occurrences -->
        <main class="occurrences-panel">
          <div class="occurrences-table-container">
            <table class="occurrences-table">
              <thead>
                <tr>
                  <th colspan="2">
                    <div class="table-header-content">
                      <div class="header-left">
                        <span class="selected-word-title">{{ selectedWordText || 'Occurrences' }}</span>
                        <span class="occurrence-count">
                          {{ filteredResults.length }} / {{ selectedWordText ? uniqueWords.find(w => w.text === selectedWordText)?.count || filteredResults.length : searchResults.total_count }} results
                        </span>
                      </div>
                      <div class="header-right" v-if="selectedWordText">
                        <button @click="exportLinesToCSV" class="export-button-icon" title="Export occurrences of selected word to CSV">
                          📥
                        </button>
                      </div>
                    </div>
                  </th>
                </tr>
                <tr>
                  <th class="line-num-header">#</th>
                  <th>Location & Line</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="filteredResults.length === 0">
                  <td colspan="2" class="no-results">No occurrences found</td>
                </tr>
                <tr
                  v-for="(result, index) in filteredResults"
                  :key="result.word_id"
                  class="result-row"
                  :class="{ selected: selectedWord?.word_id === result.word_id }"
                  @click="selectWord(result)"
                >
                  <td class="line-number-cell">{{ index + 1 }}</td>
                  <td class="result-content">
                    <!-- Consolidated metadata: Work, Sections, Verse #, Line # -->
                    <div class="result-metadata">
                      {{ result.work_name_tamil }}: {{ result.hierarchy_path_tamil || result.hierarchy_path }} | Verse {{ result.verse_number }}, Line {{ result.line_number }}
                    </div>
                    <!-- Line Text with Highlighted Word -->
                    <div class="line-text" v-html="highlightWord(result.line_text, selectedWordText || result.word_text)"></div>
                  </td>
                </tr>
              </tbody>
            </table>

            <!-- Pagination -->
            <div v-if="searchResults.total_count > searchResults.limit" class="pagination">
              <button
                @click="loadMore"
                :disabled="loading || searchResults.results.length >= searchResults.total_count"
              >
                Load More
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
    </div>
    <!-- End Search Page -->

  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import api from './api.js'
import Home from './Home.vue'
import OurInspiration from './OurInspiration.vue'
import About from './About.vue'

export default {
  name: 'App',
  components: {
    Home,
    OurInspiration,
    About
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
    })

    // Methods
    const toggleAllWorks = () => {
      if (selectAllWorks.value) {
        selectedWorks.value = works.value.map(w => w.work_id)
      } else {
        selectedWorks.value = []
      }
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

      try {
        // If no works are selected, show empty results
        if (selectedWorks.value.length === 0) {
          searchResults.value = {
            results: [],
            total_count: 0,
            limit: 100,
            offset: 0,
            search_term: trimmedQuery,
            match_type: matchType.value,
            word_position: wordPosition.value
          }
          loading.value = false
          return
        }

        const params = {
          q: trimmedQuery,
          match_type: matchType.value,
          word_position: wordPosition.value,
          limit: 100,
          offset: 0
        }

        if (selectedWorks.value.length > 0 && selectedWorks.value.length < works.value.length) {
          params.work_ids = selectedWorks.value.join(',')
        }

        const response = await api.searchWords(params)
        searchResults.value = response.data
        selectedWord.value = null
        selectedWordText.value = null
      } catch (err) {
        error.value = 'Search failed: ' + err.message
        searchResults.value = null
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

      // ALWAYS use backend's unique_words if available (includes complete counts)
      if (searchResults.value.unique_words && Array.isArray(searchResults.value.unique_words) && searchResults.value.unique_words.length > 0) {
        console.log('Using backend unique_words:', searchResults.value.unique_words.length, 'words')
        return searchResults.value.unique_words.map(word => ({
          text: word.word_text,
          count: word.count
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
          wordMap[text] = { text, count: 1 }
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

    // Computed: Search summary statistics
    const searchSummary = computed(() => {
      if (!searchResults.value || !searchResults.value.results) return ''

      const results = searchResults.value.results

      // Count unique works
      const uniqueWorkNames = new Set(results.map(r => r.work_name))
      const worksCount = uniqueWorkNames.size

      // Count unique verses
      const uniqueVerses = new Set(results.map(r => r.verse_id))
      const versesCount = uniqueVerses.size

      // Total word occurrences
      const wordOccurrences = searchResults.value.total_count

      // Distinct words
      const distinctWords = uniqueWords.value.length

      return `${worksCount} work${worksCount !== 1 ? 's' : ''}, ${versesCount} verse${versesCount !== 1 ? 's' : ''}, ${wordOccurrences.toLocaleString()} word occurrence${wordOccurrences !== 1 ? 's' : ''}, ${distinctWords} distinct word${distinctWords !== 1 ? 's' : ''}`
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

    // Method: Handle filter mode change
    const handleFilterModeChange = () => {
      if (filterMode.value === 'all') {
        selectedWorks.value = works.value.map(w => w.work_id)
        selectAllWorks.value = true
      } else {
        // Open filters panel for selection
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
    const exportWordsToCSV = () => {
      if (!uniqueWords.value || uniqueWords.value.length === 0) return

      // Create CSV content
      const headers = ['Word', 'Count']
      const rows = uniqueWords.value.map(word => [word.text, word.count])

      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
      ].join('\n')

      // Create and download file
      const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `tamil_words_${searchQuery.value.trim()}_${new Date().toISOString().split('T')[0]}.csv`)
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
      performSearch,
      loadMore,
      selectWord,
      selectWordFromList,
      toggleFilters,
      closeFilters,
      handleFilterModeChange,
      highlightWord,
      exportWordsToCSV,
      exportLinesToCSV,
      autocompleteResults,
      showAutocomplete,
      handleAutocompleteInput,
      selectAutocomplete,
      hideAutocomplete
    }
  }
}
</script>
