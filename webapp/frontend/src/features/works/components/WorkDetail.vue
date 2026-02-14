<template>
  <div class="work-detail-container">
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
      <p>Loading work details...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error">
      <p>Error loading work: {{ error }}</p>
      <button @click="loadWorkDetail">Retry</button>
    </div>

    <!-- Work content -->
    <div v-else-if="work" class="work-content">
      <!-- Work header -->
      <div class="work-header">
        <h1 class="work-title-tamil">{{ work.work_name_tamil }}</h1>
        <h2 class="work-title-english">{{ work.work_name }}</h2>

        <div class="work-metadata">
          <div v-if="work.author_tamil || work.author" class="meta-item">
            <span class="meta-label">Author:</span>
            <span class="meta-value">{{ work.author_tamil || work.author }}</span>
          </div>

          <div v-if="work.chronology_start_year || work.chronology_end_year" class="meta-item">
            <span class="meta-label">Dating:</span>
            <span class="meta-value">
              {{ formatChronology(work.chronology_start_year, work.chronology_end_year) }}
              <span v-if="work.chronology_confidence" class="confidence">
                ({{ work.chronology_confidence }})
              </span>
            </span>
          </div>

          <div class="meta-item">
            <span class="meta-label">
              {{ work.verse_count === 1 ? 'பாடல்:' : 'பாடல்கள்:' }}
            </span>
            <span class="meta-value">{{ work.verse_count || 0 }}</span>
          </div>

          <div class="meta-item">
            <span class="meta-label">Sections:</span>
            <span class="meta-value">{{ work.section_count || 0 }}</span>
          </div>
        </div>

        <div v-if="work.description" class="work-description">
          {{ work.description }}
        </div>
      </div>

      <!-- Hierarchical sections tree -->
      <div class="sections-container">
        <div v-if="sectionTree.length === 0" class="no-sections">
          <p>No hierarchical structure available.</p>
        </div>
        <div v-else class="sections-tree">
          <SectionTreeNode
            v-for="section in sectionTree"
            :key="section.section_id"
            :section="section"
            :work-id="work.work_id"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../../api.js'
import SectionTreeNode from './SectionTreeNode.vue'
import { useCollectionState } from '../../../composables/useCollectionState.js'

const route = useRoute()
const router = useRouter()
const { currentCollectionPath } = useCollectionState()

const work = ref(null)
const sections = ref([])
const loading = ref(true)
const error = ref(null)

// Compute breadcrumbs from collection state and current work
const breadcrumbs = computed(() => {
  const crumbs = []

  // Add collection breadcrumbs from shared state
  if (currentCollectionPath.value.length > 0) {
    currentCollectionPath.value.forEach(collection => {
      crumbs.push({
        type: 'collection',
        id: collection.collection_id,
        name: collection.collection_name_tamil || collection.collection_name,
        routePath: '/works' // Will filter by collection
      })
    })
  }

  // Add current work
  if (work.value) {
    crumbs.push({
      type: 'work',
      id: work.value.work_id,
      name: work.value.work_name_tamil || work.value.work_name,
      routePath: `/works/${work.value.work_id}`,
      isCurrent: true
    })
  }

  return crumbs
})

// Navigate to breadcrumb
const navigateToBreadcrumb = (crumb) => {
  if (crumb.type === 'collection') {
    // Navigate back to WorksList with collection context
    // The collection filter will be maintained by useCollectionState
    router.push(crumb.routePath)
  } else if (crumb.type === 'work') {
    // Stay on current page (refresh)
    router.push(crumb.routePath)
  }
}

// Go back to previous page
const goBack = () => {
  router.back()
}

// Build hierarchical tree from flat sections list
const sectionTree = computed(() => {
  if (!sections.value.length) return []

  // Create a map for quick lookup
  const sectionMap = {}
  sections.value.forEach(section => {
    sectionMap[section.section_id] = { ...section, children: [] }
  })

  // Build tree structure
  const tree = []
  sections.value.forEach(section => {
    const node = sectionMap[section.section_id]
    if (section.parent_section_id === null || section.parent_section_id === undefined) {
      tree.push(node)
    } else {
      const parent = sectionMap[section.parent_section_id]
      if (parent) {
        parent.children.push(node)
      }
    }
  })

  return tree
})

// Load work details
const loadWorkDetail = async () => {
  const workId = route.params.workId
  if (!workId) return

  loading.value = true
  error.value = null

  try {
    // Load work details
    const workResponse = await api.getWorkDetail(workId)
    work.value = workResponse.data

    // Load sections hierarchy
    const sectionsResponse = await api.getWorkSections(workId)
    sections.value = sectionsResponse.data.sections
  } catch (err) {
    console.error('Error loading work detail:', err)
    error.value = err.message || 'Failed to load work details'
  } finally {
    loading.value = false
  }
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

// Load on mount and when route changes
onMounted(() => {
  loadWorkDetail()
})

watch(() => route.params.workId, () => {
  if (route.params.workId) {
    loadWorkDetail()
  }
})
</script>

<style scoped>
.work-detail-container {
  padding: 2rem;
  max-width: 1200px;
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

.work-header {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.work-title-tamil {
  font-size: 2.5rem;
  color: #1976d2;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.work-title-english {
  font-size: 1.5rem;
  color: #666;
  font-style: italic;
  font-weight: normal;
  margin-bottom: 1.5rem;
}

.work-metadata {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 4px;
}

.meta-item {
  display: flex;
  gap: 0.5rem;
}

.meta-label {
  font-weight: 600;
  color: #555;
  min-width: 80px;
}

.meta-value {
  color: #333;
}

.confidence {
  color: #999;
  font-size: 0.85rem;
}

.work-description {
  font-size: 1rem;
  line-height: 1.7;
  color: #444;
}

.sections-container {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 2rem;
}

.sections-container h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #f5f5f5;
  padding-bottom: 0.5rem;
}

.no-sections {
  text-align: center;
  padding: 2rem;
  color: #999;
}

.sections-tree {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Responsive design */
@media (max-width: 768px) {
  .work-detail-container {
    padding: 1rem;
  }

  .work-header {
    padding: 1.5rem;
  }

  .work-title-tamil {
    font-size: 1.8rem;
  }

  .work-title-english {
    font-size: 1.2rem;
  }

  .work-metadata {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .sections-container {
    padding: 1.5rem;
  }
}
</style>
