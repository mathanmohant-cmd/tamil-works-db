<template>
  <div class="works-list-container">
    <div class="works-header">
      <h2>Browse Works</h2>
      <p class="subtitle">Explore Tamil literary works by period, tradition, and genre</p>

      <!-- Breadcrumb Navigation -->
      <div v-if="breadcrumbs.length > 1" class="breadcrumb-nav">
        <span
          v-for="(crumb, index) in breadcrumbs"
          :key="crumb.collection_id"
          class="breadcrumb-wrapper"
        >
          <span v-if="index > 0" class="breadcrumb-separator">›</span>
          <button
            class="breadcrumb-item"
            :class="{ 'breadcrumb-current': index === breadcrumbs.length - 1 }"
            @click="navigateToCollection(crumb, index)"
          >
            {{ crumb.collection_name_tamil || crumb.collection_name }}
          </button>
        </span>
      </div>

      <!-- Sort options (only show when displaying works) -->
      <div v-if="works.length > 0" class="sort-controls">
        <label for="sort-by">Sort by:</label>
        <select id="sort-by" v-model="sortBy" @change="sortWorks">
          <option value="collection">Collection Order</option>
          <option value="alphabetical">Alphabetical</option>
          <option value="canonical">Traditional Order (1-22)</option>
          <option value="chronological">Chronological</option>
        </select>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading">
      <p>Loading...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error">
      <p>Error: {{ error }}</p>
      <button @click="loadCurrentView">Retry</button>
    </div>

    <!-- Main content area -->
    <div v-else>
      <!-- Collections grid -->
      <div v-if="collections.length > 0">
        <h3 v-if="works.length > 0" class="section-heading">Collections</h3>
        <div class="collections-grid">
          <div
            v-for="collection in collections"
            :key="collection.collection_id"
            class="collection-card"
            @click="navigateToCollection(collection)"
          >
            <div class="collection-card-header">
              <h3 class="collection-title-tamil">
                {{ collection.collection_name_tamil || collection.collection_name }}
              </h3>
              <p v-if="collection.collection_name_tamil" class="collection-title-english">
                {{ collection.collection_name }}
              </p>
            </div>

            <div class="collection-card-body">
              <div v-if="collection.description" class="collection-description">
                {{ truncateText(collection.description, 120) }}
              </div>

              <div class="collection-meta">
                <span v-if="collection.children && collection.children.length > 0" class="meta-badge">
                  {{ collection.children.length }}
                  {{ collection.children.length === 1 ? 'collection' : 'collections' }}
                </span>
                <span v-if="collection.work_count > 0" class="meta-badge">
                  {{ collection.work_count }}
                  {{ collection.work_count === 1 ? 'work' : 'works' }}
                </span>
              </div>
            </div>

            <div class="collection-card-footer">
              <span class="explore-link">Explore →</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Works grid -->
      <div v-if="works.length > 0" :class="{ 'works-section': collections.length > 0 }">
        <h3 v-if="collections.length > 0" class="section-heading">Works</h3>
        <div class="works-grid">
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
      </div>

      <!-- Empty state -->
      <div v-if="collections.length === 0 && works.length === 0" class="empty-state">
        <p>No collections or works found.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../../api.js'
import { useCollectionState } from '../../../composables/useCollectionState.js'

const router = useRouter()
const { setCollectionPath, currentCollectionPath } = useCollectionState()

const collections = ref([])
const works = ref([])
const loading = ref(true)
const error = ref(null)
const sortBy = ref('collection')  // Default to collection order
const currentCollection = ref(null)
const breadcrumbs = ref([])
const rootCollection = ref(null)

// Load designated filter collection (தமிழ் இலக்கியம்)
const loadRootCollection = async () => {
  loading.value = true
  error.value = null
  collections.value = []
  works.value = []
  breadcrumbs.value = []
  currentCollection.value = null

  try {
    // Get designated filter collection ID (should be 1)
    const settingsResponse = await api.getDesignatedFilterCollection()
    const rootCollectionId = settingsResponse.data.collection_id

    // Get the root collection tree
    const response = await api.getCollectionTreePublic(rootCollectionId)
    const rootData = Array.isArray(response.data) ? response.data[0] : response.data

    // Store root collection
    rootCollection.value = rootData

    // Set up breadcrumbs with root collection
    breadcrumbs.value = [rootData]
    currentCollection.value = rootData

    // Show children of root collection
    if (rootData.children && rootData.children.length > 0) {
      collections.value = rootData.children
    }

    // Also check for works at root level
    try {
      const worksResponse = await api.getWorksByCollection(rootCollectionId)
      if (worksResponse.data && worksResponse.data.length > 0) {
        works.value = worksResponse.data
        sortWorks()
      }
    } catch (worksErr) {
      console.log('No works at root level:', worksErr)
    }

  } catch (err) {
    console.error('Error loading root collection:', err)
    error.value = err.message || 'Failed to load collections'
  } finally {
    loading.value = false
  }
}

// Load a specific collection's children and works
const loadCollection = async (collection) => {
  loading.value = true
  error.value = null
  collections.value = []
  works.value = []

  try {
    console.log('Loading collection:', collection.collection_name_tamil || collection.collection_name)

    // Get the full tree from root to find children
    const treeResponse = await api.getCollectionTreePublic(rootCollection.value.collection_id)
    const fullTree = Array.isArray(treeResponse.data) ? treeResponse.data[0] : treeResponse.data

    console.log('Full tree loaded:', fullTree)

    // Find this collection in the tree
    const findCollection = (node, targetId) => {
      if (node.collection_id === targetId) return node
      if (node.children) {
        for (const child of node.children) {
          const found = findCollection(child, targetId)
          if (found) return found
        }
      }
      return null
    }

    const collectionData = findCollection(fullTree, collection.collection_id)
    console.log('Found collection data:', collectionData)

    if (collectionData && collectionData.children && collectionData.children.length > 0) {
      // Has child collections - show them
      collections.value = collectionData.children
      console.log('Setting child collections:', collections.value.length, 'collections')
    } else {
      console.log('No child collections found')
    }

    // Also try to load works for this collection
    try {
      const worksResponse = await api.getWorksByCollection(collection.collection_id)
      if (worksResponse.data && worksResponse.data.length > 0) {
        works.value = worksResponse.data
        console.log('Loaded works:', works.value.length, 'works')
        sortWorks()
      }
    } catch (worksErr) {
      console.log('No works in this collection:', worksErr)
    }

    console.log('Final state - Collections:', collections.value.length, 'Works:', works.value.length)

  } catch (err) {
    console.error('Error loading collection:', err)
    error.value = err.message || 'Failed to load collection'
  } finally {
    loading.value = false
  }
}

// Navigate to a collection
const navigateToCollection = (collection, breadcrumbIndex = null) => {
  currentCollection.value = collection

  // If navigating to root collection, reload root (do this before breadcrumb updates)
  if (collection.collection_id === rootCollection.value?.collection_id) {
    loadRootCollection()
    return // loadRootCollection() handles breadcrumbs internally
  }

  // Update breadcrumbs for non-root collections
  if (breadcrumbIndex !== null) {
    // Clicked on a breadcrumb - truncate to that level
    breadcrumbs.value = breadcrumbs.value.slice(0, breadcrumbIndex + 1)
  } else {
    const existingIndex = breadcrumbs.value.findIndex(c => c.collection_id === collection.collection_id)
    if (existingIndex !== -1) {
      // Going back to a previous level
      breadcrumbs.value = breadcrumbs.value.slice(0, existingIndex + 1)
    } else {
      // Going deeper
      breadcrumbs.value.push(collection)
    }
  }

  // Share collection path with other components via composable
  setCollectionPath(breadcrumbs.value)

  // Load the non-root collection
  loadCollection(collection)
}

// Load current view (for retry)
const loadCurrentView = () => {
  if (currentCollection.value && currentCollection.value.collection_id !== rootCollection.value?.collection_id) {
    loadCollection(currentCollection.value)
  } else {
    loadRootCollection()
  }
}

// Sort works based on selected option
const sortWorks = () => {
  if (!works.value || works.value.length === 0) return

  if (sortBy.value === 'collection') {
    works.value.sort((a, b) => {
      // Sort by position_in_collection, with nulls at the end
      const posA = a.position_in_collection !== null && a.position_in_collection !== undefined ? a.position_in_collection : 9999
      const posB = b.position_in_collection !== null && b.position_in_collection !== undefined ? b.position_in_collection : 9999
      return posA - posB
    })
  } else if (sortBy.value === 'alphabetical') {
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
  // Collection context is already shared via useCollectionState composable
  router.push({
    name: 'WorkDetail',
    params: { workId }
  })
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

// Load root collection or restore previous collection on mount
onMounted(async () => {
  // Check if there's a saved collection path from previous navigation
  if (currentCollectionPath.value && currentCollectionPath.value.length > 0) {
    // Restore the previous collection view
    const lastCollection = currentCollectionPath.value[currentCollectionPath.value.length - 1]

    // First load root to initialize rootCollection.value
    await loadRootCollection()

    // Then navigate to the saved collection
    breadcrumbs.value = [...currentCollectionPath.value]
    currentCollection.value = lastCollection

    if (lastCollection.collection_id === rootCollection.value?.collection_id) {
      // Already at root, no need to load again
    } else {
      loadCollection(lastCollection)
    }
  } else {
    // No saved path, load root collection
    loadRootCollection()
  }
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

/* Breadcrumb Navigation */
.breadcrumb-nav {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin: 1rem 0;
  padding: 0.75rem;
  background-color: #f8f9fa;
  border-radius: 6px;
  font-size: 0.95rem;
}

.breadcrumb-wrapper {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.breadcrumb-item {
  color: #1976d2;
  background: none;
  border: none;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  font-size: 0.95rem;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.breadcrumb-item:hover {
  background-color: #e3f2fd;
  text-decoration: underline;
}

.breadcrumb-separator {
  color: #999;
  margin: 0 0.25rem;
}

.breadcrumb-current {
  color: #2c3e50;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
}

/* Sort Controls */
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

/* Collections Grid */
.collections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.collection-card {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  min-height: 180px;
}

.collection-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
  border-color: #1976d2;
}

.collection-card-header {
  margin-bottom: 1rem;
  border-bottom: 2px solid #f5f5f5;
  padding-bottom: 0.75rem;
}

.collection-title-tamil {
  font-size: 1.5rem;
  color: #1976d2;
  margin-bottom: 0.25rem;
  font-weight: 600;
}

.collection-title-english {
  font-size: 0.95rem;
  color: #666;
  font-style: italic;
}

.collection-card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.collection-description {
  font-size: 0.9rem;
  color: #666;
  line-height: 1.5;
}

.collection-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: auto;
}

.meta-badge {
  background-color: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.collection-card-footer {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f5f5f5;
  text-align: right;
}

/* Section Headings */
.section-heading {
  font-size: 1.5rem;
  color: #2c3e50;
  margin: 2rem 0 1rem 0;
  font-weight: 600;
  border-bottom: 2px solid #1976d2;
  padding-bottom: 0.5rem;
}

.works-section {
  margin-top: 2rem;
}

/* Works Grid */
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

  .breadcrumb-nav {
    font-size: 0.85rem;
  }

  .collections-grid,
  .works-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .collection-card,
  .work-card {
    padding: 1rem;
  }

  .collection-title-tamil,
  .work-title-tamil {
    font-size: 1.2rem;
  }
}
</style>
