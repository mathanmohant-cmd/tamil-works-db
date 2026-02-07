<template>
  <div class="section-view-container">
    <!-- Back Button -->
    <button @click="goBack" class="back-button">
      ← Back
    </button>

    <!-- Breadcrumb navigation -->
    <div v-if="breadcrumbs.length > 0" class="breadcrumb">
      <span
        v-for="(crumb, index) in breadcrumbs"
        :key="crumb.id || index"
        class="breadcrumb-item"
      >
        <span v-if="index > 0" class="separator">›</span>
        <button
          @click="navigateToBreadcrumb(crumb)"
          class="breadcrumb-link"
          :class="{ 'breadcrumb-current': crumb.isCurrent }"
          :disabled="crumb.isCurrent"
        >
          {{ crumb.name }}
        </button>
      </span>
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
        <!-- Parent hierarchy (if exists) -->
        <div v-if="cleanHierarchyPath(sectionData.section.parent_hierarchy_path)" class="section-parent-hierarchy">
          {{ cleanHierarchyPath(sectionData.section.parent_hierarchy_path) }}
        </div>

        <div class="section-title">
          <span class="level-type">
            {{ sectionData.section.level_type_tamil || sectionData.section.level_type }}:
          </span>
          <h1 class="section-name">
            {{ sectionData.section.section_name_tamil || sectionData.section.section_name }}
          </h1>
        </div>
        <div class="section-meta">
          <span class="verse-count">
            {{ sectionData.total_count }} {{ sectionData.total_count === 1 ? 'பாடல்' : 'பாடல்கள்' }}
          </span>
        </div>
      </div>

      <!-- Verses list -->
      <div class="verses-list">
        <div
          v-for="verse in sectionData.verses"
          :key="verse.verse_id"
          class="verse-card"
        >
          <div class="verse-header" @click="navigateToVerse(verse.verse_id)">
            <div class="verse-header-left">
              <span class="verse-number">
                {{ verse.verse_type_tamil || verse.verse_type || 'Verse' }}
                {{ verse.verse_number }}
              </span>
              <!-- Metadata icon with tooltip -->
              <div
                v-if="verse.metadata && Object.keys(verse.metadata).length > 0"
                class="metadata-icon-container"
                @mouseenter="showMetadata(verse.verse_id)"
                @mouseleave="hideMetadata"
                @click.stop
              >
                <span class="metadata-icon">ⓘ</span>
                <!-- Floating metadata panel -->
                <div
                  v-if="activeMetadataVerseId === verse.verse_id"
                  class="metadata-tooltip"
                >
                  <div class="metadata-header">Verse Metadata</div>
                  <div
                    v-for="(value, key) in verse.metadata"
                    :key="key"
                    class="metadata-item"
                  >
                    <span class="metadata-key">{{ formatMetadataKey(key) }}:</span>
                    <span class="metadata-value">{{ formatMetadataValue(value) }}</span>
                  </div>
                </div>
              </div>
            </div>
            <span class="verse-lines-count">
              {{ verse.total_lines }} {{ verse.total_lines === 1 ? 'அடி' : 'அடிகள்' }}
            </span>
          </div>
          <div class="verse-content">
            <div v-for="(line, index) in verse.lines" :key="index" class="verse-line">
              <span class="line-text">{{ line }}</span>
              <span v-if="(index + 1) % 5 === 0" class="line-number">{{ index + 1 }}</span>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../../api.js'
import { useCollectionState } from '../../../composables/useCollectionState.js'

const route = useRoute()
const router = useRouter()
const { currentCollectionPath } = useCollectionState()

const sectionData = ref(null)
const loading = ref(true)
const error = ref(null)
const limit = ref(100)
const offset = ref(0)
const activeMetadataVerseId = ref(null)

const workId = ref(route.params.workId)
const sectionId = ref(route.params.sectionId)

// Compute breadcrumbs from collection state and current section
const breadcrumbs = computed(() => {
  const crumbs = []

  // Add collection breadcrumbs from shared state
  if (currentCollectionPath.value.length > 0) {
    currentCollectionPath.value.forEach(collection => {
      crumbs.push({
        type: 'collection',
        id: collection.collection_id,
        name: collection.collection_name_tamil || collection.collection_name,
        routePath: '/works'
      })
    })
  }

  // Add work breadcrumb
  if (sectionData.value?.section?.work_name_tamil) {
    crumbs.push({
      type: 'work',
      id: workId.value,
      name: sectionData.value.section.work_name_tamil,
      routePath: `/works/${workId.value}`
    })
  }

  // Don't add section to breadcrumbs - it's already in the header
  return crumbs
})

// Navigate to breadcrumb
const navigateToBreadcrumb = (crumb) => {
  router.push(crumb.routePath)
}

// Go back to previous page
const goBack = () => {
  router.back()
}

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

// Metadata tooltip handlers
const showMetadata = (verseId) => {
  activeMetadataVerseId.value = verseId
}

const hideMetadata = () => {
  activeMetadataVerseId.value = null
}

// Format metadata key for display
const formatMetadataKey = (key) => {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

// Format metadata value for display
const formatMetadataValue = (value) => {
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  if (typeof value === 'object' && value !== null) {
    return JSON.stringify(value, null, 2)
  }
  return String(value)
}

// Clean hierarchy path for display
const cleanHierarchyPath = (path) => {
  if (!path) return ''

  // Split by ' > ' to get each level
  const levels = path.split(' > ')

  // Clean each level - remove the "type:" prefix and keep only the name
  const cleanedLevels = levels.map(level => {
    // Split by ':' to separate level_type and section_name
    const parts = level.split(':')
    if (parts.length === 2) {
      const sectionName = parts[1].trim()
      // Hide generic section labels like "முக்கிய தொகுப்பு"
      if (sectionName === 'முக்கிய தொகுப்பு' || sectionName === 'Main Collection') {
        return null
      }
      // Return only the section name (part after the colon)
      return sectionName
    }
    // If no colon, return as-is
    return level.trim()
  }).filter(level => level !== null)  // Remove nulls

  return cleanedLevels.join(' • ')
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

.back-button {
  margin-bottom: 1rem;
  padding: 0.75rem 1.5rem;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 2px 6px rgba(25, 118, 210, 0.3);
}

.back-button:hover {
  background: #1565c0;
  transform: translateX(-4px);
  box-shadow: 0 4px 10px rgba(25, 118, 210, 0.4);
}

.back-button:active {
  transform: translateX(-2px);
}

.breadcrumb {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 0.95rem;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.breadcrumb-link {
  color: #1976d2;
  background: none;
  border: none;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  font-size: 0.95rem;
  border-radius: 4px;
  transition: all 0.2s ease;
  font-weight: 500;
}

.breadcrumb-link:hover {
  background: #e3f2fd;
  text-decoration: underline;
}

.breadcrumb-link.breadcrumb-current {
  font-weight: 600;
  color: #2c3e50;
  cursor: default;
  pointer-events: none;
}

.breadcrumb-link:disabled {
  cursor: default;
  pointer-events: none;
}

.separator {
  color: #999;
  margin: 0 0.25rem;
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

.section-parent-hierarchy {
  font-size: 1rem;
  color: #666;
  font-style: italic;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f0f0f0;
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
  transition: all 0.2s ease;
}

.verse-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #1976d2;
}

.verse-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #f5f5f5;
  cursor: pointer;
  transition: background-color 0.2s ease;
  margin: -0.5rem -0.75rem 1rem -0.75rem;
  padding: 0.5rem 0.75rem 0.75rem 0.75rem;
  border-radius: 6px 6px 0 0;
}

.verse-header:hover {
  background-color: #f8f9fa;
}

.verse-header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.verse-number {
  font-weight: 600;
  color: #1976d2;
  font-size: 1.1rem;
}

.metadata-icon-container {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.metadata-icon {
  font-size: 1rem;
  color: #666;
  cursor: help;
  user-select: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: #e3f2fd;
  transition: all 0.2s ease;
}

.metadata-icon:hover {
  background-color: #1976d2;
  color: white;
  transform: scale(1.1);
}

.metadata-tooltip {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 0.5rem;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 250px;
  max-width: 400px;
}

.metadata-header {
  font-weight: 600;
  font-size: 0.95rem;
  color: #1976d2;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #f5f5f5;
}

.metadata-item {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.metadata-key {
  font-weight: 600;
  color: #555;
  min-width: 80px;
}

.metadata-value {
  color: #333;
  flex: 1;
}

.verse-lines-count {
  font-size: 0.85rem;
  color: #999;
}

.verse-content {
  background: transparent;
  border: none;
  border-radius: 0;
  padding: 1rem 0;
  margin-bottom: 2rem;
  line-height: 1.5;
}

.verse-line {
  display: flex;
  gap: 0.5rem;
  margin: 0;
  padding: 0.25rem 0;
  align-items: baseline;
  line-height: 1.3;
  border-bottom: 1px solid #d0d0d0;
}

.verse-line:last-child {
  border-bottom: none;
}

.line-text {
  font-size: 1.1rem;
  font-family: var(--tamil-font), var(--english-font);
  color: var(--text-primary);
  line-height: 1.3;
  margin: 0;
  padding: 0;
  flex: 1;
}

.line-number {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.75rem;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  margin-left: 0.5rem;
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

  .verse-header-left {
    gap: 0.5rem;
  }

  .metadata-tooltip {
    left: auto;
    right: 0;
    min-width: 200px;
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
