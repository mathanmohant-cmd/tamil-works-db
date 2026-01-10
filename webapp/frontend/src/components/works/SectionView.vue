<template>
  <div class="section-view-container">
    <!-- Breadcrumb navigation -->
    <div class="breadcrumb">
      <router-link to="/works">Works</router-link>
      <span class="separator">›</span>
      <router-link :to="`/works/${workId}`">{{ sectionData?.section?.work_name_tamil || 'Work' }}</router-link>
      <span class="separator">›</span>
      <span>{{ sectionData?.section?.section_name_tamil || 'Loading...' }}</span>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading">
      <p>Loading verses...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error">
      <p>Error loading section: {{ error }}</p>
      <button @click="loadSection">Retry</button>
    </div>

    <!-- Section content -->
    <div v-else-if="sectionData" class="section-content">
      <!-- Section header -->
      <div class="section-header">
        <div class="section-title">
          <span class="level-type">
            {{ sectionData.section.level_type_tamil || sectionData.section.level_type }}:
          </span>
          <h1 class="section-name">
            {{ sectionData.section.section_name_tamil || sectionData.section.section_name }}
          </h1>
        </div>
        <div class="section-meta">
          <span class="verse-count">{{ sectionData.total_count }} verses</span>
        </div>
      </div>

      <!-- Verses list -->
      <div class="verses-list">
        <div
          v-for="verse in sectionData.verses"
          :key="verse.verse_id"
          class="verse-card"
          @click="navigateToVerse(verse.verse_id)"
        >
          <div class="verse-header">
            <span class="verse-number">
              {{ verse.verse_type_tamil || verse.verse_type || 'Verse' }}
              {{ verse.verse_number }}
            </span>
            <span class="verse-lines-count">{{ verse.total_lines }} lines</span>
          </div>
          <div class="verse-content">
            <div v-for="(line, index) in verse.lines" :key="index" class="verse-line">
              {{ line }}
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="sectionData.total_count > limit" class="pagination">
        <button
          @click="loadPreviousPage"
          :disabled="offset === 0"
          class="pagination-btn"
        >
          ← Previous
        </button>

        <span class="page-info">
          Showing {{ offset + 1 }}-{{ Math.min(offset + limit, sectionData.total_count) }}
          of {{ sectionData.total_count }}
        </span>

        <button
          @click="loadNextPage"
          :disabled="offset + limit >= sectionData.total_count"
          class="pagination-btn"
        >
          Next →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api.js'

const route = useRoute()
const router = useRouter()

const sectionData = ref(null)
const loading = ref(true)
const error = ref(null)
const limit = ref(100)
const offset = ref(0)

const workId = ref(route.params.workId)
const sectionId = ref(route.params.sectionId)

// Load section verses
const loadSection = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await api.getSectionVerses(sectionId.value, limit.value, offset.value)
    sectionData.value = response.data
  } catch (err) {
    console.error('Error loading section:', err)
    error.value = err.message || 'Failed to load section verses'
  } finally {
    loading.value = false
  }
}

// Navigate to verse detail
const navigateToVerse = (verseId) => {
  router.push({
    name: 'VerseView',
    params: {
      workId: workId.value,
      verseId: verseId
    }
  })
}

// Pagination handlers
const loadPreviousPage = () => {
  if (offset.value >= limit.value) {
    offset.value -= limit.value
    loadSection()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const loadNextPage = () => {
  if (sectionData.value && offset.value + limit.value < sectionData.value.total_count) {
    offset.value += limit.value
    loadSection()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// Load on mount and when route changes
onMounted(() => {
  loadSection()
})

watch(() => route.params.sectionId, (newSectionId) => {
  if (newSectionId) {
    sectionId.value = newSectionId
    workId.value = route.params.workId
    offset.value = 0
    loadSection()
  }
})
</script>

<style scoped>
.section-view-container {
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.breadcrumb {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1.5rem;
}

.breadcrumb a {
  color: #1976d2;
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

.separator {
  margin: 0 0.5rem;
  color: #999;
}

.loading, .error {
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

.section-header {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.section-title {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.level-type {
  font-size: 0.9rem;
  font-weight: 600;
  color: #666;
}

.section-name {
  font-size: 1.8rem;
  color: #1976d2;
  font-weight: 600;
  margin: 0;
}

.section-meta {
  font-size: 0.9rem;
  color: #999;
}

.verses-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.verse-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.verse-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #1976d2;
  transform: translateY(-2px);
}

.verse-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #f5f5f5;
}

.verse-number {
  font-weight: 600;
  color: #1976d2;
  font-size: 1.1rem;
}

.verse-lines-count {
  font-size: 0.85rem;
  color: #999;
}

.verse-content {
  line-height: 1.8;
}

.verse-line {
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  padding: 2rem 0;
}

.pagination-btn {
  padding: 0.75rem 1.5rem;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #1565c0;
}

.pagination-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.9rem;
  color: #666;
}

/* Responsive design */
@media (max-width: 768px) {
  .section-view-container {
    padding: 1rem;
  }

  .section-header {
    padding: 1rem;
  }

  .section-title {
    flex-direction: column;
    gap: 0.25rem;
  }

  .section-name {
    font-size: 1.4rem;
  }

  .verse-card {
    padding: 1rem;
  }

  .verse-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .verse-line {
    font-size: 1rem;
  }

  .pagination {
    gap: 1rem;
  }

  .pagination-btn {
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
  }

  .page-info {
    font-size: 0.85rem;
  }
}
</style>
