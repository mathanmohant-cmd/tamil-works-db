<template>
  <div class="work-detail-container">
    <!-- Breadcrumb navigation -->
    <div class="breadcrumb">
      <router-link to="/works">Works</router-link>
      <span class="separator">›</span>
      <span>{{ work?.work_name_tamil || 'Loading...' }}</span>
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

          <div v-if="work.period" class="meta-item">
            <span class="meta-label">Period:</span>
            <span class="meta-value">{{ work.period }}</span>
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
            <span class="meta-label">Verses:</span>
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
        <h3>Structure</h3>
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
import { useRoute } from 'vue-router'
import api from '../../api.js'
import SectionTreeNode from './SectionTreeNode.vue'

const route = useRoute()

const work = ref(null)
const sections = ref([])
const loading = ref(true)
const error = ref(null)

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
