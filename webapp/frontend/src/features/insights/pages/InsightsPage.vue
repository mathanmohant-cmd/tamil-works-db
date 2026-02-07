<template>
  <div class="insights-page">
    <!-- Page Header -->
    <div class="page-header">
      <h1>Insights: Grammatical Pattern Explorer</h1>
      <p class="subtitle">
        Explore Tamil grammatical patterns through phoneme-based searches.
        Discover case markers, plurals, derivational affixes, and more.
      </p>
    </div>

    <!-- Pattern Selector Section -->
    <div class="pattern-selector-section">
      <div class="selector-controls">
        <div class="pattern-dropdown-container">
          <label for="pattern-select">Select Pattern:</label>
          <select
            id="pattern-select"
            v-model="selectedPatternId"
            @change="handlePatternChange"
            class="pattern-dropdown"
          >
            <option value="">-- Choose a pattern --</option>
            <optgroup
              v-for="category in groupedPatterns"
              :key="category.name"
              :label="category.name"
            >
              <option
                v-for="pattern in category.patterns"
                :key="pattern.pattern_id"
                :value="pattern.pattern_id"
              >
                {{ pattern.name }} ({{ pattern.name_tamil }})
              </option>
            </optgroup>
          </select>
        </div>

        <button
          @click="searchPattern"
          :disabled="!selectedPatternId || loading"
          class="search-button"
        >
          {{ loading ? 'Searching...' : 'Search' }}
        </button>
      </div>

      <!-- Pattern Description Panel -->
      <div v-if="selectedPattern" class="pattern-description">
        <h3>{{ selectedPattern.name }} ({{ selectedPattern.name_tamil }})</h3>
        <p class="description">{{ selectedPattern.description }}</p>
        <p class="examples"><strong>Examples:</strong> {{ selectedPattern.example }}</p>
      </div>
    </div>

    <!-- Work/Collection Filters (Optional) -->
    <div v-if="selectedPatternId" class="filter-section">
      <button
        @click="toggleFilters"
        class="filter-toggle-button"
      >
        {{ showFilters ? 'Hide Filters' : 'Show Filters' }}
      </button>

      <div v-if="showFilters" class="filter-controls">
        <p class="filter-info">
          <em>Optional: Filter results to specific works or collections</em>
        </p>
        <!-- Reuse existing filter UI from search feature -->
        <div class="filter-mode-selector">
          <label>
            <input type="radio" value="all" v-model="filterMode" />
            All Works
          </label>
          <label>
            <input type="radio" value="select" v-model="filterMode" />
            Select Works
          </label>
        </div>

        <div v-if="filterMode === 'select'" class="works-selector">
          <p>Select works to search within:</p>
          <div class="works-checklist">
            <label
              v-for="work in works"
              :key="work.work_id"
              class="work-checkbox"
            >
              <input
                type="checkbox"
                :value="work.work_id"
                v-model="selectedWorks"
              />
              {{ work.work_name_tamil || work.work_name }}
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Results Section -->
    <div v-if="results.length > 0 || loading" class="results-section">
      <!-- Loading State -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Searching for patterns...</p>
      </div>

      <!-- Results Summary -->
      <div v-else-if="!loading && results.length > 0" class="results-container">
        <div class="results-summary">
          <h2>
            {{ totalCount }} Words | {{ totalVerses }} Verses
          </h2>
        </div>

        <!-- Word List -->
        <div class="word-list">
          <div
            v-for="(word, index) in results"
            :key="`${word.word_text}-${index}`"
            class="word-item"
          >
            <div class="word-number">{{ offset + index + 1 }}.</div>
            <div class="word-content">
              <div class="word-text-row">
                <span class="word-text">{{ word.word_text }}</span>
                <span class="phoneme">({{ word.phoneme }})</span>
              </div>
              <div class="word-stats">
                <span class="usage-count">{{ word.usage_count }} usage</span>
                <span class="verse-count">{{ word.verse_count }} verses</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Load More Button -->
        <div v-if="hasMore" class="load-more-container">
          <button
            @click="loadMore"
            :disabled="loadingMore"
            class="load-more-button"
          >
            {{ loadingMore ? 'Loading...' : 'Load More' }}
          </button>
        </div>
      </div>

      <!-- No Results -->
      <div v-else-if="!loading && searched" class="no-results">
        <p>No words found matching this pattern.</p>
        <p class="suggestion">Try selecting different works or a different pattern.</p>
      </div>
    </div>

    <!-- Empty State (Before First Search) -->
    <div v-else-if="!searched" class="empty-state">
      <p>Select a pattern above and click "Search" to explore Tamil grammatical patterns.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../../api.js'

// State
const patterns = ref([])
const selectedPatternId = ref('')
const results = ref([])
const totalCount = ref(0)
const totalVerses = ref(0)
const offset = ref(0)
const limit = ref(100)
const loading = ref(false)
const loadingMore = ref(false)
const searched = ref(false)
const showFilters = ref(false)

// Filter state
const filterMode = ref('all')
const selectedWorks = ref([])
const works = ref([])

// Computed properties
const groupedPatterns = computed(() => {
  const groups = {}

  patterns.value.forEach(pattern => {
    const category = pattern.category || 'Other'
    if (!groups[category]) {
      groups[category] = {
        name: category,
        patterns: []
      }
    }
    groups[category].patterns.push(pattern)
  })

  // Return in specific order
  const order = ['Case Markers', 'Number & Person', 'Derivational', 'Other']
  return order
    .filter(cat => groups[cat])
    .map(cat => groups[cat])
})

const selectedPattern = computed(() => {
  if (!selectedPatternId.value) return null
  return patterns.value.find(p => p.pattern_id === selectedPatternId.value)
})

const hasMore = computed(() => {
  return results.value.length < totalCount.value
})

// Methods
const loadPatterns = async () => {
  try {
    const response = await api.getPhonemePatterns()
    patterns.value = response.data
  } catch (error) {
    console.error('Failed to load patterns:', error)
    alert('Failed to load pattern list. Please refresh the page.')
  }
}

const loadWorks = async () => {
  try {
    const response = await api.getWorks()
    works.value = response.data
  } catch (error) {
    console.error('Failed to load works:', error)
  }
}

const handlePatternChange = () => {
  // Clear results when pattern changes
  clearResults()
}

const searchPattern = async () => {
  if (!selectedPatternId.value) return

  loading.value = true
  searched.value = false
  clearResults()

  try {
    const params = {
      limit: limit.value,
      offset: 0,
      expand: false
    }

    // Add work filter if selected
    if (filterMode.value === 'select' && selectedWorks.value.length > 0) {
      params.work_ids = selectedWorks.value.join(',')
    }

    const response = await api.searchPhonemePattern(selectedPatternId.value, params)
    results.value = response.data.results
    totalCount.value = response.data.total_count
    totalVerses.value = response.data.total_verses || 0
    offset.value = 0
    searched.value = true
  } catch (error) {
    console.error('Search failed:', error)
    alert('Search failed. Please try again.')
  } finally {
    loading.value = false
  }
}

const loadMore = async () => {
  if (!hasMore.value || loadingMore.value) return

  loadingMore.value = true

  try {
    const newOffset = offset.value + limit.value
    const params = {
      limit: limit.value,
      offset: newOffset,
      expand: false
    }

    // Add work filter if selected
    if (filterMode.value === 'select' && selectedWorks.value.length > 0) {
      params.work_ids = selectedWorks.value.join(',')
    }

    const response = await api.searchPhonemePattern(selectedPatternId.value, params)
    results.value = [...results.value, ...response.data.results]
    offset.value = newOffset
  } catch (error) {
    console.error('Load more failed:', error)
    alert('Failed to load more results. Please try again.')
  } finally {
    loadingMore.value = false
  }
}

const clearResults = () => {
  results.value = []
  totalCount.value = 0
  totalVerses.value = 0
  offset.value = 0
  searched.value = false
}

const toggleFilters = () => {
  showFilters.value = !showFilters.value
}

// Initialize
onMounted(async () => {
  await loadPatterns()
  await loadWorks()
})
</script>

<style scoped>
.insights-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #6c757d;
  font-size: 1rem;
  line-height: 1.5;
}

/* Pattern Selector */
.pattern-selector-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.selector-controls {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  margin-bottom: 1rem;
}

.pattern-dropdown-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.pattern-dropdown-container label {
  font-weight: 600;
  color: #495057;
}

.pattern-dropdown {
  padding: 0.75rem;
  font-size: 1rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background: white;
}

.search-button {
  padding: 0.75rem 2rem;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.search-button:hover:not(:disabled) {
  background: #357abd;
}

.search-button:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.pattern-description {
  background: white;
  padding: 1rem;
  border-radius: 4px;
  border-left: 4px solid #4a90e2;
}

.pattern-description h3 {
  font-size: 1.25rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.description {
  color: #495057;
  margin-bottom: 0.5rem;
}

.examples {
  color: #6c757d;
  font-style: italic;
}

/* Filters */
.filter-section {
  margin-bottom: 1.5rem;
}

.filter-toggle-button {
  padding: 0.5rem 1rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 1rem;
}

.filter-toggle-button:hover {
  background: #5a6268;
}

.filter-controls {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
}

.filter-info {
  color: #6c757d;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.filter-mode-selector {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
}

.filter-mode-selector label {
  cursor: pointer;
}

.works-selector {
  margin-top: 1rem;
}

.works-checklist {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
  padding: 1rem;
  background: white;
  border-radius: 4px;
}

.work-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

/* Results */
.results-section {
  margin-top: 2rem;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4a90e2;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.results-summary {
  background: #e7f3ff;
  padding: 1rem 1.5rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.results-summary h2 {
  font-size: 1.25rem;
  color: #2c3e50;
  margin: 0;
}

.word-list {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  overflow: hidden;
}

.word-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid #f1f3f5;
  transition: background 0.2s;
}

.word-item:last-child {
  border-bottom: none;
}

.word-item:hover {
  background: #f8f9fa;
}

.word-number {
  font-weight: 600;
  color: #6c757d;
  min-width: 3rem;
  text-align: right;
}

.word-content {
  flex: 1;
}

.word-text-row {
  margin-bottom: 0.5rem;
}

.word-text {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin-right: 0.75rem;
}

.phoneme {
  color: #6c757d;
  font-size: 1rem;
}

.word-stats {
  display: flex;
  gap: 1.5rem;
  font-size: 0.9rem;
  color: #6c757d;
}

.usage-count {
  font-weight: 600;
  color: #4a90e2;
}

.load-more-container {
  text-align: center;
  margin-top: 1.5rem;
}

.load-more-button {
  padding: 0.75rem 2rem;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.load-more-button:hover:not(:disabled) {
  background: #357abd;
}

.load-more-button:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.no-results {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
}

.suggestion {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #adb5bd;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
  background: #f8f9fa;
  border-radius: 4px;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .insights-page {
    padding: 1rem;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .selector-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .search-button {
    width: 100%;
    padding: 1rem;
  }

  .filter-mode-selector {
    flex-direction: column;
    gap: 0.5rem;
  }

  .works-checklist {
    grid-template-columns: 1fr;
  }

  .word-item {
    flex-direction: column;
    gap: 0.5rem;
  }

  .word-number {
    text-align: left;
  }

  .word-text-row {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .word-stats {
    flex-direction: column;
    gap: 0.25rem;
  }
}
</style>
