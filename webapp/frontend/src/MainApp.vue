<template>
  <div id="app">
    <!-- Header -->
    <header class="app-header">
      <h1>தமிழ் இலக்கியத் தொடரடைவு</h1>
      <h2 >Searchable Concordance for Thamizh Literature</h2 >
  
      <!-- Database Summary -->
      <div class="database-summary" v-if="stats">
        <span>{{ stats.total_works }} Works | {{ stats.total_verses.toLocaleString() }} Verses | {{ stats.distinct_words.toLocaleString() }} Distinct Words | {{ stats.total_words.toLocaleString() }} Usage</span>
        <span class="attribution-note">Built upon Prof. P. Pandiyaraja's <a href="http://tamilconcordance.in/" target="_blank" rel="noopener noreferrer" class="concordance-link">Thamizh Concordance</a></span>
      </div>
      <div class="header-bottom">
        <div class="search-section">
          <div class="search-row">
            <div class="search-box">
              <div class="autocomplete-wrapper">
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Enter a word... (e.g., அறம்)"
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
            <div class="filter-group-inline" :class="{ 'filter-disabled': matchType === 'exact' }">
              <span class="filter-label">Position:</span>
              <label>
                <input type="radio" v-model="wordPosition" value="beginning" :disabled="matchType === 'exact'" />
                Beginning
              </label>
              <label>
                <input type="radio" v-model="wordPosition" value="end" :disabled="matchType === 'exact'" />
                End
              </label>
              <label>
                <input type="radio" v-model="wordPosition" value="anywhere" :disabled="matchType === 'exact'" />
                Anywhere
              </label>
            </div>
          </div>
          <!-- Navigation -->
          <nav class="main-nav">
            <button @click="currentPage = 'home'" :class="{active: currentPage === 'home'}">Acknowledgment</button>
            <button @click="currentPage = 'search'; showWelcome = true" :class="{active: currentPage === 'search'}">Search</button>
            <button @click="currentPage = 'about'" :class="{active: currentPage === 'about'}">About & Help</button>
            <button @click="currentPage = 'journey'" :class="{active: currentPage === 'journey'}">The Story Behind</button>
          </nav>
        </div>
      </div>
    </header>

    <!-- Home Page (Acknowledgment) -->
    <Home v-if="currentPage === 'home'" />

    <!-- About Concordance Page -->
    <AboutConcordance v-if="currentPage === 'about'" :initialTab="aboutInitialTab" />

    <!-- Principles Page -->
    <Principles v-if="currentPage === 'principles'" />

    <!-- The Story Behind Page -->
    <OurJourney v-if="currentPage === 'journey'" />

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
          <div style="flex: 1;"></div>
          <div class="filter-header-actions">
            <button @click="clearFilters" class="clear-filter-button" title="Uncheck all works">
              Clear Filter
            </button>
            <button @click="closeFilters" class="done-button">Done</button>
          </div>
        </div>

        <!-- Collection Tree Filter -->
        <div class="filter-content-wrapper">
          <CollectionTree
            ref="collectionTreeRef"
            :selected-works="selectedWorks"
            :root-collection-id="designatedCollectionId"
            @update:selectedWorks="handleCollectionSelection"
          />

          <!-- Selected Works Summary -->
          <div class="selected-works-summary">
            <div class="selected-works-header">
              <strong>Selected Works: {{ selectedWorks.length }}</strong>
              <button v-if="selectedWorks.length > 0" @click="clearFilters" class="clear-selection-btn">
                Clear All
              </button>
            </div>
            <div v-if="selectedWorks.length > 0" class="selected-works-preview">
              <div class="selected-work-chip" v-for="workId in sortedSelectedWorks.slice(0, 15)" :key="workId">
                <span class="work-chip-name">{{ getWorkName(workId) }}</span>
                <button @click="removeWork(workId)" class="remove-chip-btn" title="Remove">×</button>
              </div>
              <div v-if="selectedWorks.length > 15" class="more-works-indicator">
                +{{ selectedWorks.length - 15 }} more
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-container">
      <!-- Help/Welcome Message -->
      <div v-if="currentPage === 'search' && !loading && showWelcome" class="welcome">
        <h2>Welcome to Searchable Thamizh Concordance</h2>
        <p class="welcome-subtitle">Search for words across Thamizh literary works</p>
        <div class="quick-start">
          <h3>&#128640; Quick Start</h3>
          <ul class="tips-list">
            <li><strong>Type a Thamizh word</strong> in the search box above — it auto-completes as you type!</li>
            <li><strong>Choose match type:</strong> Partial (finds similar words) or Exact (precise match)</li>
            <li><strong>Set position:</strong> Beginning, End, or Anywhere in the word</li>
            <li><strong>Filter by works</strong> (optional) to search specific texts</li>
            <li></li>
          </ul>
          <p>Understanding what a concordance is and the <strong>word segmentation principles</strong> will help you use this tool more effectively.
          </p>
          <p class="learn-more">
            <a href="#" @click.prevent="aboutInitialTab = 'qa'; currentPage = 'about'" class="principles-link">Learn more about concordance and how it works →</a>
          </p>
        </div>

        <div class="try-examples">
          <h3>Try These Examples</h3>
          <div class="example-buttons">
            <button @click="tryExampleSearch('அறம்')" class="example-btn">அறம்</button>
            <button @click="tryExampleSearch('தமிழ்நாடு')" class="example-btn">தமிழ்நாடு</button>
            <button @click="tryExampleSearch('எஃகு')" class="example-btn">எஃகு</button>
            <button @click="tryExampleSearch('இம்மென்')" class="example-btn">இம்மென்</button>
            <button @click="tryExampleSearch('ஈனில்')" class="example-btn">ஈனில்</button>
          </div>
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

          <!-- Word List Sort Options -->
          <div class="word-list-sort-options">
            <span class="filter-label">Sort words by:</span>
            <label>
              <input type="radio" v-model="wordListSortBy" value="alphabetical" />
              Alphabetical
            </label>
            <label>
              <input type="radio" v-model="wordListSortBy" value="count_high_to_low" />
              Count (High to Low)
            </label>
            <label>
              <input type="radio" v-model="wordListSortBy" value="count_low_to_high" />
              Count (Low to High)
            </label>
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
                  <span class="word-count-badge">({{ word.count }})</span>
                </div>
                <div class="word-actions">
                  <a
                    :href="`https://dsal.uchicago.edu/cgi-bin/app/tamil-lex_query.py?qs=${encodeURIComponent(word.text)}&searchhws=yes&matchtype=default`"
                    target="_blank"
                    class="action-icon dictionary-icon"
                    @click.stop
                    title="Look up in Thamizh Lexicon"
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

                <!-- Sort Lines Options -->
                <div class="lines-sort-options">
                  <span class="filter-label">Sort lines by work order:</span>
                  <label>
                    <input type="radio" v-model="sortBy" value="canonical" />
                    Traditional Canon
                  </label>
                  <label>
                    <input type="radio" v-model="sortBy" value="alphabetical" />
                    Alphabetical
                  </label>
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
                    :data-word-id="result.word_id"
                    class="occurrence-item"
                  >
                    <div class="occurrence-content">
                      <div class="occurrence-metadata">
                        <span class="occurrence-number">{{ occIndex + 1 }}.</span>
                        <span class="work-name">{{ result.work_name_tamil }}</span>
                        <template v-if="cleanHierarchyPath(result.hierarchy_path_tamil || result.hierarchy_path)">
                          <span class="separator"> • </span>
                          <span class="hierarchy-path">{{ cleanHierarchyPath(result.hierarchy_path_tamil || result.hierarchy_path) }}</span>
                        </template>
                        <span class="separator"> • </span>
                        <span class="verse-link-text" @click="openVerseView(result.verse_id, word.text, result.word_id)" title="Click to view full verse">{{ formatVerseAndLine(result, false) }}</span>
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
        <button @click="exportWords('txt')" class="export-modal-option">
          📄 Export as TXT
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
        <button @click="exportWordLines('txt', currentExportWordText)" class="export-modal-option">
          📄 Export as TXT
        </button>
        <button @click="currentExportWordText = null" class="export-modal-cancel">
          Cancel
        </button>
      </div>
    </div>

  </div>
</template>

<script>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import axios from 'axios'
import api from './api.js'
import Home from './Home.vue'
import OurJourney from './OurJourney.vue'
import Principles from './Principles.vue'
import AboutConcordance from './AboutConcordance.vue'
import VerseView from './VerseView.vue'
import CollectionTree from './components/CollectionTree.vue'

export default {
  name: 'App',
  components: {
    Home,
    OurJourney,
    Principles,
    AboutConcordance,
    VerseView,
    CollectionTree
  },
  setup() {
    // Page navigation
    const currentPage = ref('search')  // Default to search page
    const showWelcome = ref(true)
    const aboutInitialTab = ref('qa')  // Track which About tab to show

    // State
    const searchQuery = ref('')
    const matchType = ref('partial')
    const wordPosition = ref('beginning')  // beginning, end, anywhere
    const sortBy = ref('canonical')  // canonical (default), alphabetical
    const collections = ref([])
    const selectedCollectionId = ref(null)
    const filterMode = ref('all')  // 'all' or 'select'
    const selectedWorks = ref([])
    const selectAllWorks = ref(true)
    const collectionTreeRef = ref(null)  // Ref to CollectionTree component
    const designatedCollectionId = ref(null)  // ID of the designated filter collection
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
    const clickedOccurrenceWordId = ref(null)  // Track which occurrence was clicked

    // Export menu state
    const showWordsExportMenu = ref(false)
    const currentExportWordText = ref(null)

    // Word list sort state
    const wordListSortBy = ref('alphabetical')

    // Load initial data
    onMounted(async () => {
      try {
        console.log('[DEBUG] onMounted: Loading initial data...')

        // Load works
        const worksResponse = await api.getWorks()
        works.value = worksResponse.data
        console.log('[DEBUG] Loaded works:', works.value.length)

        // Load collections for sort options (optional - fallback to empty if not available)
        try {
          if (api.getPublicCollections) {
            const collectionsResponse = await api.getPublicCollections()
            collections.value = collectionsResponse.data
            console.log('[DEBUG] Loaded collections:', collections.value.length)
          } else {
            console.warn('[DEBUG] getPublicCollections not available, skipping')
            collections.value = []
          }
        } catch (collErr) {
          console.warn('[DEBUG] Failed to load collections:', collErr.message)
          collections.value = []
        }

        // Load designated filter collection ID
        try {
          const settingsResponse = await axios.get(`${api.getBaseURL()}/settings/designated_filter_collection`)
          designatedCollectionId.value = settingsResponse.data.collection_id
          console.log('[DEBUG] Loaded designated collection ID:', designatedCollectionId.value)
        } catch (settingsErr) {
          console.warn('[DEBUG] Failed to load designated collection, using default tree view:', settingsErr.message)
          designatedCollectionId.value = null
        }

        // Check for saved selection in session storage (always restore if available)
        const savedSelection = sessionStorage.getItem('selectedWorks')
        const savedMode = sessionStorage.getItem('filterMode')

        if (savedSelection) {
          selectedWorks.value = JSON.parse(savedSelection)
          filterMode.value = savedMode || 'all'
          console.log('[DEBUG] Restored saved selection:', selectedWorks.value.length, 'works')
        } else {
          selectedWorks.value = works.value.map(w => w.work_id)
          filterMode.value = 'all'
          console.log('[DEBUG] Initialized all works:', selectedWorks.value.length, 'works')
        }

        // Load stats
        const statsResponse = await api.getStatistics()
        stats.value = statsResponse.data
        console.log('[DEBUG] Loaded stats:', stats.value)
      } catch (err) {
        console.error('[DEBUG] onMounted error:', err)
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

    // Watch sortBy to reload occurrences for expanded words with new sort order
    watch(sortBy, async (newSortBy, oldSortBy) => {
      // Only reload if there are expanded words and sort actually changed
      if (expandedWords.value.size === 0 || newSortBy === oldSortBy) return

      const wordsToReload = Array.from(expandedWords.value)

      for (const wordText of wordsToReload) {
        // Remove all occurrences for this word
        if (searchResults.value && searchResults.value.results) {
          searchResults.value.results = searchResults.value.results.filter(
            r => r.word_text !== wordText
          )
        }

        // Reset tracking to reload from beginning
        loadedOccurrences.value[wordText] = {
          offset: 0,
          hasMore: true
        }
      }

      // Now reload each word's first batch sequentially
      for (const wordText of wordsToReload) {
        await loadMoreOccurrences(wordText)
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
      showWelcome.value = true // Show welcome/help content when clearing
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
      showWelcome.value = false // Hide welcome/help content when searching

      loading.value = true
      error.value = null
      offset.value = 0
      expandedWords.value = new Set() // Reset expanded words on new search
      loadedOccurrences.value = {} // Reset loaded occurrences

      try {
        console.log('[DEBUG] performSearch called:', {
          selectedWorksCount: selectedWorks.value.length,
          totalWorksCount: works.value.length,
          filterMode: filterMode.value,
          searchQuery: trimmedQuery
        })

        // If no works are selected, show empty results
        if (selectedWorks.value.length === 0) {
          console.warn('[DEBUG] No works selected! Returning empty results')
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
          offset: 0,
          sort_by: sortBy.value
        }

        if (selectedWorks.value.length > 0 && selectedWorks.value.length < works.value.length) {
          params.work_ids = selectedWorks.value.join(',')
        }

        if (sortBy.value === 'collection' && selectedCollectionId.value) {
          params.collection_id = selectedCollectionId.value
        }

        const response = await api.searchWords(params)
        console.log('[DEBUG] API response:', {
          hasUniqueWords: !!response.data.unique_words,
          uniqueWordsLength: response.data.unique_words?.length,
          totalCount: response.data.total_count
        })
        searchResults.value = {
          ...response.data,
          results: [] // Start with empty results
        }
        console.log('[DEBUG] searchResults after assignment:', {
          hasUniqueWords: !!searchResults.value.unique_words,
          uniqueWordsLength: searchResults.value.unique_words?.length
        })

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
          offset: offset.value,
          sort_by: sortBy.value
        }

        if (selectedWorks.value.length > 0 && selectedWorks.value.length < works.value.length) {
          params.work_ids = selectedWorks.value.join(',')
        }

        if (sortBy.value === 'collection' && selectedCollectionId.value) {
          params.collection_id = selectedCollectionId.value
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
          offset: 0,
          sort_by: sortBy.value
        }

        if (selectedWorks.value.length > 0 && selectedWorks.value.length < works.value.length) {
          params.work_ids = selectedWorks.value.join(',')
        }

        if (sortBy.value === 'collection' && selectedCollectionId.value) {
          params.collection_id = selectedCollectionId.value
        }

        const response = await api.searchWords(params)

        // CRITICAL: Replace all results with the newly fetched ones (already sorted by backend)
        // DO NOT merge with existing results - merging would destroy the backend's sort order
        // The backend returns results sorted according to sort_by parameter (alphabetical/canonical/chronological/collection)
        // Any client-side merging or concatenation will break this ordering
        searchResults.value = {
          ...searchResults.value,
          results: response.data.results,  // Use ONLY the new results, not [...existingResults, ...newResults]
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

    // Computed: Get unique words with counts from backend (sorted by user preference)
    const uniqueWords = computed(() => {
      if (!searchResults.value) return []

      let words = []

      // ALWAYS use backend's unique_words if available (includes complete counts and work breakdown)
      if (searchResults.value.unique_words && Array.isArray(searchResults.value.unique_words) && searchResults.value.unique_words.length > 0) {
        console.log('Using backend unique_words:', searchResults.value.unique_words.length, 'words')
        words = searchResults.value.unique_words.map(word => ({
          text: word.word_text,
          count: word.count, // Usage count (total occurrences)
          verse_count: word.verse_count || 0, // Verse count
          work_breakdown: word.work_breakdown || [] // Include work breakdown from backend
        }))
      } else {
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

        words = Object.values(wordMap)
      }

      // Sort based on user preference
      if (wordListSortBy.value === 'alphabetical') {
        return words.sort((a, b) => a.text.localeCompare(b.text, 'ta'))
      } else if (wordListSortBy.value === 'count_high_to_low') {
        return words.sort((a, b) => b.count - a.count)
      } else if (wordListSortBy.value === 'count_low_to_high') {
        return words.sort((a, b) => a.count - b.count)
      }

      return words
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

    // Computed: Sort works by canonical order (canonical_position field)
    const sortedWorks = computed(() => {
      if (!works.value || works.value.length === 0) return []

      // Sort by canonical_position field (ascending)
      return [...works.value].sort((a, b) => {
        const orderA = a.canonical_position || 999
        const orderB = b.canonical_position || 999
        return orderA - orderB
      })
    })

    // Computed: Sort selected works by canonical order
    const sortedSelectedWorks = computed(() => {
      if (!selectedWorks.value || selectedWorks.value.length === 0) return []
      if (!works.value || works.value.length === 0) return selectedWorks.value

      // Create a map of work_id to canonical_position for fast lookup
      const positionMap = new Map()
      works.value.forEach(work => {
        positionMap.set(work.work_id, work.canonical_position || 999)
      })

      // Sort selected work IDs by their canonical position
      return [...selectedWorks.value].sort((a, b) => {
        const posA = positionMap.get(a) || 999
        const posB = positionMap.get(b) || 999
        return posA - posB
      })
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

      // Always save to session storage
      sessionStorage.setItem('selectedWorks', JSON.stringify(selectedWorks.value))
      sessionStorage.setItem('filterMode', filterMode.value)
    }

    // Method: Get work name by ID
    const getWorkName = (workId) => {
      const work = works.value.find(w => w.work_id === workId)
      return work ? (work.work_name_tamil || work.work_name) : 'Unknown'
    }

    // Method: Remove a single work from selection
    const removeWork = (workId) => {
      selectedWorks.value = selectedWorks.value.filter(id => id !== workId)
      // Update selectAllWorks checkbox state
      selectAllWorks.value = selectedWorks.value.length === works.value.length
    }

    const clearFilters = () => {
      selectedWorks.value = []
      selectAllWorks.value = false
      // Clear accordion filter checkboxes
      if (collectionTreeRef.value) {
        collectionTreeRef.value.clearSelections()
      }
    }

    // Method: Handle filter mode change
    const handleFilterModeChange = () => {
      if (filterMode.value === 'all') {
        selectedWorks.value = works.value.map(w => w.work_id)
        selectAllWorks.value = true
        // Mark all collections as selected in the accordion
        if (collectionTreeRef.value) {
          collectionTreeRef.value.selectAll()
        }
      } else {
        // Switch to select mode - uncheck all by default
        selectedWorks.value = []
        selectAllWorks.value = false
        // Clear accordion filter checkboxes
        if (collectionTreeRef.value) {
          collectionTreeRef.value.clearSelections()
        }
        // Switch to search page and open filters panel for selection
        currentPage.value = 'search'
        filtersExpanded.value = true
      }
    }

    // Method: Handle collection selection from tree
    const handleCollectionSelection = (workIds) => {
      selectedWorks.value = workIds
      // Update selectAllWorks checkbox state
      selectAllWorks.value = workIds.length === works.value.length
      // Update filter mode to select if not all works are selected
      if (workIds.length < works.value.length) {
        filterMode.value = 'select'
      }
      console.log('[DEBUG] Collection selection updated:', workIds.length, 'works selected')
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

    // Method: Export words to CSV or TXT
    const exportWords = (format) => {
      showWordsExportMenu.value = false
      if (!uniqueWords.value || uniqueWords.value.length === 0) return

      if (format === 'csv') {
        exportWordsToCSV()
      } else if (format === 'txt') {
        exportWordsToTXT()
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
      link.setAttribute('download', `tamizh_words_${searchTerm}_${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }

    // Method: Export words to TXT
    const exportWordsToTXT = () => {
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

      // Create TXT content
      let content = 'Data Source: tamilconcordence.in\n'
      content += 'Compiled by: Prof. Dr. P. Pandiyaraja\n\n'
      content += `Search Term: ${searchTerm}\n`
      content += `Match Type: ${matchType.value}\n`
      content += `Word Position: ${wordPosition.value}\n`
      content += `Total Works Found: ${worksSet.size}\n`
      content += `Total Verses Found: ${totalVerses}\n`
      content += `Distinct Words Found: ${totalWords}\n`
      content += `Total Usage Count: ${totalUsage}\n\n`
      content += '---\n\n'

      uniqueWords.value.forEach((word, index) => {
        content += `${index + 1}. ${word.text} - ${word.count} usage\n`
      })

      // Create and download file
      const blob = new Blob(['\ufeff' + content], { type: 'text/plain;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `tamizh_words_${searchTerm}_${new Date().toISOString().split('T')[0]}.txt`)
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

    // Method: Try example search
    const tryExampleSearch = (word) => {
      searchQuery.value = word
      performSearch()
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
          offset: tracking.offset,
          sort_by: sortBy.value
        }

        if (selectedWorks.value.length > 0 && selectedWorks.value.length < works.value.length) {
          params.work_ids = selectedWorks.value.join(',')
        }

        if (sortBy.value === 'collection' && selectedCollectionId.value) {
          params.collection_id = selectedCollectionId.value
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
    // Sort by: user's sort order (canonical/alphabetical for works) → section hierarchy → verse → line
    const getSortedWordOccurrences = (wordText) => {
      const occurrences = getWordOccurrences(wordText)

      // Sort by user's preference, then by hierarchy
      return occurrences.sort((a, b) => {
        // First, sort by work according to user's selected sort order
        if (a.work_id !== b.work_id) {
          if (sortBy.value === 'alphabetical') {
            // Alphabetical sort by work name (Tamil)
            const aWorkName = a.work_name_tamil || a.work_name
            const bWorkName = b.work_name_tamil || b.work_name
            return aWorkName.localeCompare(bWorkName, 'ta')
          } else {
            // Canonical sort by canonical_position
            const aCanonical = a.canonical_position !== undefined ? a.canonical_position : a.work_id
            const bCanonical = b.canonical_position !== undefined ? b.canonical_position : b.work_id
            return aCanonical - bCanonical
          }
        }

        // Within same work, sort by section_id (sections are numbered sequentially in canonical order)
        // The section_id represents the canonical order better than section_sort_order
        // because it was assigned during import in the correct sequence
        if (a.section_id !== b.section_id) {
          return a.section_id - b.section_id
        }

        // Then sort by verse_sort_order (if available) or verse_number
        const aVerseOrder = a.verse_sort_order !== undefined ? a.verse_sort_order : a.verse_number
        const bVerseOrder = b.verse_sort_order !== undefined ? b.verse_sort_order : b.verse_number

        if (aVerseOrder !== bVerseOrder) {
          return aVerseOrder - bVerseOrder
        }

        // Finally, sort by line_number
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

      return cleanedLevels.join(' • ')
    }

    // Method: Format verse and line display with Tamil terminology
    // Order: Verse first, then Line (to follow hierarchy: sections > verse > line)
    const formatVerseAndLine = (result, includeLink = false) => {
      const hasHierarchy = result.hierarchy_path_tamil || result.hierarchy_path
      // Use verse_type_tamil first, fall back to verse_type, then default to 'பாடல்'
      const verseTypeTamil = result.verse_type_tamil || result.verse_type || 'பாடல்'

      // For single-poem works (work_verse_count = 1), only show line number
      if (result.work_verse_count === 1) {
        return `அடி ${result.line_number}`
      }

      // For Manimegalai and Silapathikaram, each section (Kathai/Kaathai) is one verse
      // Hide redundant verse number (always 1 per section)
      if (result.work_name === 'Manimegalai' || result.work_name === 'Silapathikaram') {
        return `அடி ${result.line_number}`
      }

      // For collection works (work_verse_count > 1), show verse number
      // Show: verse_type_tamil verse_number • அடி line_number
      return `${verseTypeTamil} ${result.verse_number} • அடி ${result.line_number}`
    }

    // Method: Open verse view
    const openVerseView = (verseId, searchWord = '', wordId = null) => {
      selectedVerseId.value = verseId
      verseViewSearchWord.value = searchWord
      clickedOccurrenceWordId.value = wordId
      showVerseView.value = true
    }

    // Method: Close verse view
    const closeVerseView = () => {
      showVerseView.value = false
      selectedVerseId.value = null
      verseViewSearchWord.value = ''

      // Scroll back to the clicked occurrence
      if (clickedOccurrenceWordId.value) {
        nextTick(() => {
          const element = document.querySelector(`[data-word-id="${clickedOccurrenceWordId.value}"]`)
          if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'center' })
          }
          clickedOccurrenceWordId.value = null
        })
      }
    }

    // Method: Export lines for a specific word (CSV or TXT)
    const exportWordLines = (format, wordText) => {
      currentExportWordText.value = null
      if (format === 'csv') {
        exportWordLinesToCSV(wordText)
      } else if (format === 'txt') {
        exportWordLinesToTXT(wordText)
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
      link.setAttribute('download', `tamizh_lines_${wordText}_${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }

    // Method: Export lines for a specific word to TXT
    const exportWordLinesToTXT = (wordText) => {
      const occurrences = getWordOccurrences(wordText)
      if (occurrences.length === 0) return

      // Get word details
      const wordInfo = searchResults.value.unique_words?.find(w => w.word_text === wordText)
      const usageCount = wordInfo?.count || occurrences.length
      const verseCount = wordInfo?.verse_count || 0

      // Get work breakdown
      const workCounts = getWorkCounts(wordText)
      const worksList = workCounts.map(w => `${w.work_name_tamil} (${w.count})`).join(', ')

      // Create TXT content
      let content = 'Data Source: tamilconcordence.in\n'
      content += 'Compiled by: Prof. Dr. P. Pandiyaraja\n\n'
      content += `Search Term: ${searchResults.value.search_term || searchQuery.value.trim()}\n`
      content += `Found Word: ${wordText}\n`
      content += `Total Works: ${workCounts.length}\n`
      content += `Total Verses: ${verseCount}\n`
      content += `Total Usage: ${usageCount}\n`
      content += `Works: ${worksList}\n\n`
      content += '---\n\n'

      occurrences.forEach((result, index) => {
        const hierarchyPath = cleanHierarchyPath(result.hierarchy_path_tamil || result.hierarchy_path)
        const location = hierarchyPath
          ? `${result.work_name_tamil} • ${hierarchyPath} • ${formatVerseAndLine(result, false)}`
          : `${result.work_name_tamil} • ${formatVerseAndLine(result, false)}`

        content += `${index + 1}. ${location}\n`
        content += `   ${result.line_text}\n\n`
      })

      // Create and download file
      const blob = new Blob(['\ufeff' + content], { type: 'text/plain;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `tamizh_lines_${wordText}_${new Date().toISOString().split('T')[0]}.txt`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }

    return {
      currentPage,
      showWelcome,
      aboutInitialTab,
      searchQuery,
      matchType,
      wordPosition,
      sortBy,
      collections,
      selectedCollectionId,
      filterMode,
      selectedWorks,
      selectAllWorks,
      collectionTreeRef,
      designatedCollectionId,
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
      sortedWorks,
      sortedSelectedWorks,
      worksFilterButtonText,
      getFilterButtonText,
      searchSummary,
      wordListSortBy,
      toggleAllWorks,
      clearSearch,
      performSearch,
      loadMore,
      selectWord,
      selectWordFromList,
      toggleFilters,
      closeFilters,
      clearFilters,
      getWorkName,
      removeWork,
      handleFilterModeChange,
      handleCollectionSelection,
      highlightWord,
      exportWords,
      exportWordsToCSV,
      exportWordsToTXT,
      exportLinesToCSV,
      exportWordLines,
      exportWordLinesToCSV,
      exportWordLinesToTXT,
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
      showLinesExportMenu,
      tryExampleSearch
    }
  }
}
</script>
