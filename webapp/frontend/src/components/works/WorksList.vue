<template>
  <div class="works-list-container">
    <div class="works-header">
      <h2>Browse Works</h2>
      <p class="subtitle">Explore Tamil literary works by period, tradition, and genre</p>

      <!-- Sort options -->
      <div class="sort-controls">
        <label for="sort-by">Sort by:</label>
        <select id="sort-by" v-model="sortBy" @change="loadWorks">
          <option value="alphabetical">Alphabetical</option>
          <option value="canonical">Traditional Order (1-22)</option>
          <option value="chronological">Chronological</option>
        </select>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading">
      <p>Loading works...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error">
      <p>Error loading works: {{ error }}</p>
      <button @click="loadWorks">Retry</button>
    </div>

    <!-- Works grid -->
    <div v-else class="works-grid">
      <div
        v-for="work in works"
        :key="work.work_id"
        class="work-card"
        @click="navigateToWork(work.work_id)"
      >
        <div class="work-card-header">
          <h3 class="work-title-tamil">{{ work.work_name_tamil }}</h3>
          <p class="work-title-english">{{ work.work_name }}</p>
        </div>

        <div class="work-card-body">
          <div v-if="work.author_tamil || work.author" class="work-meta">
            <span class="meta-label">Author:</span>
            <span class="meta-value">
              {{ work.author_tamil || work.author }}
            </span>
          </div>

          <div v-if="work.period" class="work-meta">
            <span class="meta-label">Period:</span>
            <span class="meta-value">{{ work.period }}</span>
          </div>

          <div v-if="work.chronology_start_year || work.chronology_end_year" class="work-meta">
            <span class="meta-label">Dating:</span>
            <span class="meta-value">
              {{ formatChronology(work.chronology_start_year, work.chronology_end_year) }}
              <span v-if="work.chronology_confidence" class="confidence">
                ({{ work.chronology_confidence }})
              </span>
            </span>
          </div>

          <div v-if="work.description" class="work-description">
            {{ truncateText(work.description, 150) }}
          </div>
        </div>

        <div class="work-card-footer">
          <span class="explore-link">Explore →</span>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!loading && !error && works.length === 0" class="empty-state">
      <p>No works found.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api.js'

const router = useRouter()

const works = ref([])
const loading = ref(true)
const error = ref(null)
const sortBy = ref('alphabetical')

// Load works from API
const loadWorks = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await api.getWorks()
    works.value = response.data

    // Apply sorting on frontend
    sortWorks()
  } catch (err) {
    console.error('Error loading works:', err)
    error.value = err.message || 'Failed to load works'
  } finally {
    loading.value = false
  }
}

// Sort works based on selected option
const sortWorks = () => {
  if (sortBy.value === 'alphabetical') {
    works.value.sort((a, b) => a.work_name_tamil.localeCompare(b.work_name_tamil))
  } else if (sortBy.value === 'canonical') {
    works.value.sort((a, b) => (a.canonical_order || 999) - (b.canonical_order || 999))
  } else if (sortBy.value === 'chronological') {
    works.value.sort((a, b) => {
      const yearA = a.chronology_start_year || 9999
      const yearB = b.chronology_start_year || 9999
      return yearA - yearB
    })
  }
}

// Navigate to work detail page
const navigateToWork = (workId) => {
  router.push({ name: 'WorkDetail', params: { workId } })
}

// Format chronology years
const formatChronology = (startYear, endYear) => {
  if (!startYear && !endYear) return ''

  const formatYear = (year) => {
    if (!year) return ''
    if (year < 0) return `${Math.abs(year)} BCE`
    return `${year} CE`
  }

  if (startYear && endYear) {
    return `${formatYear(startYear)} - ${formatYear(endYear)}`
  }
  return formatYear(startYear || endYear)
}

// Truncate text to specified length
const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// Load works on mount
onMounted(() => {
  loadWorks()
})
</script>

<style scoped>
.works-list-container {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.works-header {
  margin-bottom: 2rem;
}

.works-header h2 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

.sort-controls label {
  font-weight: 500;
  color: #2c3e50;
}

.sort-controls select {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  background-color: white;
  cursor: pointer;
}

.sort-controls select:hover {
  border-color: #999;
}

.loading, .error, .empty-state {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.error {
  color: #d32f2f;
}

.error button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.error button:hover {
  background-color: #1565c0;
}

.works-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.work-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
}

.work-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
  border-color: #1976d2;
}

.work-card-header {
  margin-bottom: 1rem;
  border-bottom: 2px solid #f5f5f5;
  padding-bottom: 0.75rem;
}

.work-title-tamil {
  font-size: 1.4rem;
  color: #1976d2;
  margin-bottom: 0.25rem;
  font-weight: 600;
}

.work-title-english {
  font-size: 0.95rem;
  color: #666;
  font-style: italic;
}

.work-card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.work-meta {
  font-size: 0.9rem;
  display: flex;
  gap: 0.5rem;
}

.meta-label {
  font-weight: 600;
  color: #555;
  min-width: 60px;
}

.meta-value {
  color: #333;
}

.confidence {
  color: #999;
  font-size: 0.85rem;
}

.work-description {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #666;
  line-height: 1.5;
}

.work-card-footer {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f5f5f5;
  text-align: right;
}

.explore-link {
  color: #1976d2;
  font-weight: 500;
  font-size: 0.9rem;
}

/* Responsive design */
@media (max-width: 768px) {
  .works-list-container {
    padding: 1rem;
  }

  .works-header h2 {
    font-size: 1.5rem;
  }

  .works-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .work-card {
    padding: 1rem;
  }

  .work-title-tamil {
    font-size: 1.2rem;
  }
}
</style>
