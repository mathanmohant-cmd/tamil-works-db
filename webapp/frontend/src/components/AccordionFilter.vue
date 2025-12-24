<template>
  <div class="accordion-filter">
    <div class="accordion-header">
      <h3>Select Collection/Work</h3>
      <div class="accordion-actions">
        <button @click="expandAll" class="action-btn" title="Expand all collections">
          Expand All
        </button>
        <button @click="collapseAll" class="action-btn" title="Collapse all collections">
          Collapse All
        </button>
      </div>
    </div>

    <div v-if="loading" class="accordion-loading">Loading collections...</div>
    <div v-else-if="error" class="accordion-error">{{ error }}</div>
    <div v-else-if="flatCollections.length === 0" class="accordion-empty">
      No collections available. Search will work with all works.
    </div>
    <div v-else class="accordion-content">
      <div
        v-for="collection in flatCollections"
        :key="collection.collection_id"
        class="accordion-item"
        :class="{ 'is-expanded': isExpanded(collection.collection_id) }"
      >
        <!-- Collection Header -->
        <div class="accordion-item-header">
          <button
            @click="toggleCollection(collection.collection_id)"
            class="accordion-toggle-icon"
            :aria-expanded="isExpanded(collection.collection_id)"
            title="Expand/Collapse"
          >
            <span class="expand-icon">
              {{ isExpanded(collection.collection_id) ? '▼' : '▶' }}
            </span>
          </button>
          <span class="collection-name-label">
            {{ collection.collection_name_tamil || collection.collection_name }}
            <span v-if="collection.work_count > 0" class="work-count">
              ({{ collection.work_count }} {{ collection.work_count === 1 ? 'work' : 'works' }})
            </span>
          </span>
          <input
            v-if="collection.work_count > 0"
            type="checkbox"
            :checked="isCollectionSelected(collection.collection_id)"
            @change="handleCollectionToggle(collection, $event)"
            class="collection-checkbox"
            @click.stop
            title="Select/deselect all works in this collection"
          />
        </div>

        <!-- Collection Content (Works List) -->
        <div
          v-if="isExpanded(collection.collection_id) && collection.work_count > 0"
          class="accordion-item-content"
        >
          <div v-if="loadingWorks[collection.collection_id]" class="loading-works">
            Loading works...
          </div>
          <div v-else-if="collectionWorks[collection.collection_id]" class="works-list">
            <div
              v-for="work in collectionWorks[collection.collection_id]"
              :key="work.work_id"
              class="work-item"
            >
              <label :for="`work-${work.work_id}`" class="work-label">
                <span class="work-icon">📄</span>
                <span class="work-name">{{ work.work_name_tamil || work.work_name }}</span>
              </label>
              <input
                type="checkbox"
                :checked="isWorkSelected(work.work_id)"
                @change="handleWorkToggle(work.work_id, $event)"
                class="work-checkbox"
                :id="`work-${work.work_id}`"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const props = defineProps({
  selectedWorks: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['update:selectedWorks'])

const collectionTree = ref([])
const expandedCollections = ref(new Set())
const collectionWorks = ref({})
const loadingWorks = ref({})
const loading = ref(false)
const error = ref(null)

// Flatten the tree structure for accordion display
// Skip pure container collections (collections with 0 works that only group others)
const flatCollections = computed(() => {
  const flatten = (collections, level = 0, skipContainers = true) => {
    const result = []
    collections.forEach(collection => {
      const hasWorks = collection.work_count > 0
      const hasChildren = collection.children && collection.children.length > 0

      if (skipContainers && !hasWorks && hasChildren) {
        // Skip this container and promote its children
        result.push(...flatten(collection.children, level, skipContainers))
      } else {
        // Include this collection
        result.push({ ...collection, level })
        if (hasChildren) {
          result.push(...flatten(collection.children, level + 1, skipContainers))
        }
      }
    })
    return result
  }
  return flatten(collectionTree.value)
})

// Load collection tree
const loadCollectionTree = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get(`${API_BASE_URL}/collections/tree`)
    collectionTree.value = response.data
  } catch (err) {
    error.value = 'Failed to load collections: ' + err.message
    console.error('Error loading collection tree:', err)
  } finally {
    loading.value = false
  }
}

// Check if collection is expanded
const isExpanded = (collectionId) => {
  return expandedCollections.value.has(collectionId)
}

// Toggle collection expansion
const toggleCollection = async (collectionId) => {
  if (expandedCollections.value.has(collectionId)) {
    expandedCollections.value.delete(collectionId)
  } else {
    expandedCollections.value.add(collectionId)
    // Load works if not already loaded
    if (!collectionWorks.value[collectionId]) {
      await loadCollectionWorks(collectionId)
    }
  }
}

// Load works for a collection
const loadCollectionWorks = async (collectionId) => {
  if (collectionWorks.value[collectionId]) return

  loadingWorks.value[collectionId] = true
  try {
    const response = await axios.get(`${API_BASE_URL}/collections/${collectionId}/works`)
    collectionWorks.value[collectionId] = response.data
  } catch (err) {
    console.error(`Error loading works for collection ${collectionId}:`, err)
  } finally {
    loadingWorks.value[collectionId] = false
  }
}

// Check if work is selected
const isWorkSelected = (workId) => {
  return props.selectedWorks.includes(workId)
}

// Check if all works in collection are selected
const isCollectionSelected = (collectionId) => {
  const works = collectionWorks.value[collectionId]
  if (!works || works.length === 0) return false
  return works.every(work => isWorkSelected(work.work_id))
}

// Handle work toggle
const handleWorkToggle = (workId, event) => {
  const isChecked = event.target.checked
  if (isChecked) {
    if (!props.selectedWorks.includes(workId)) {
      emit('update:selectedWorks', [...props.selectedWorks, workId])
    }
  } else {
    emit('update:selectedWorks', props.selectedWorks.filter(id => id !== workId))
  }
}

// Handle collection toggle
const handleCollectionToggle = async (collection, event) => {
  const isChecked = event.target.checked

  // Load works if not loaded
  if (!collectionWorks.value[collection.collection_id]) {
    await loadCollectionWorks(collection.collection_id)
  }

  const works = collectionWorks.value[collection.collection_id] || []
  const workIds = works.map(w => w.work_id)

  if (isChecked) {
    // Add all works from this collection
    const updatedSelection = new Set([...props.selectedWorks, ...workIds])
    emit('update:selectedWorks', Array.from(updatedSelection))
  } else {
    // Remove all works from this collection
    const updatedSelection = props.selectedWorks.filter(id => !workIds.includes(id))
    emit('update:selectedWorks', updatedSelection)
  }
}

// Expand all collections
const expandAll = async () => {
  flatCollections.value.forEach(collection => {
    if (collection.work_count > 0) {
      expandedCollections.value.add(collection.collection_id)
      if (!collectionWorks.value[collection.collection_id]) {
        loadCollectionWorks(collection.collection_id)
      }
    }
  })
}

// Collapse all collections
const collapseAll = () => {
  expandedCollections.value.clear()
}

// Clear all selections
const clearSelections = () => {
  // This will be called from parent
  emit('update:selectedWorks', [])
}

// Select all works
const selectAll = async () => {
  // Load all works first
  for (const collection of flatCollections.value) {
    if (collection.work_count > 0 && !collectionWorks.value[collection.collection_id]) {
      await loadCollectionWorks(collection.collection_id)
    }
  }

  // Collect all work IDs
  const allWorkIds = new Set()
  Object.values(collectionWorks.value).forEach(works => {
    works.forEach(work => allWorkIds.add(work.work_id))
  })

  emit('update:selectedWorks', Array.from(allWorkIds))
}

// Expose methods to parent
defineExpose({
  clearSelections,
  selectAll
})

onMounted(async () => {
  await loadCollectionTree()
})
</script>

<style scoped>
.accordion-filter {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #dee2e6;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.accordion-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
}

.accordion-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.4rem 0.8rem;
  font-size: 0.9rem;
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.action-btn:hover {
  background: #e9ecef;
  border-color: #999;
}

.accordion-loading,
.accordion-error,
.accordion-empty {
  padding: 1rem;
  text-align: center;
  color: #666;
}

.accordion-error {
  color: #dc3545;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}

.accordion-empty {
  color: #6c757d;
  font-style: italic;
}

.accordion-content {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.accordion-content::-webkit-scrollbar {
  width: 8px;
}

.accordion-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.accordion-content::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.accordion-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.accordion-item {
  margin-bottom: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  background: #fff;
  overflow: hidden;
}

.accordion-item.is-expanded {
  border-color: #0066cc;
}

.accordion-item-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #fff;
  border-bottom: 1px solid transparent;
  transition: background-color 0.2s;
}

.accordion-item.is-expanded .accordion-item-header {
  background: #f0f7ff;
  border-bottom-color: #dee2e6;
}

.collection-checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
  flex-shrink: 0;
  margin: 0;
}

.collection-name-label {
  flex: 1;
  font-size: 1rem;
  color: #333;
  font-weight: 500;
  cursor: default;
}

.accordion-toggle-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  padding: 0;
  background: white;
  color: var(--kurinji-primary);
  border: 2px solid var(--kurinji-light);
  border-bottom: 3px solid var(--life-pulse);
  border-radius: 50%;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.accordion-toggle-icon:hover {
  border-color: var(--kurinji-primary);
  border-bottom-color: var(--life-pulse);
  color: var(--kurinji-dark);
  transform: scale(1.05);
}

.accordion-toggle-icon:active {
  transform: scale(1);
}

.accordion-item.is-expanded .accordion-toggle-icon {
  background: var(--mullai-accent);
  border-color: var(--mullai-primary);
  border-bottom-color: var(--life-pulse);
}

.accordion-toggle-icon .expand-icon {
  font-size: 1rem;
  line-height: 1;
}

.work-count {
  font-size: 0.85rem;
  color: var(--marutham-primary);
  font-weight: 600;
  margin-left: 0.5rem;
}

.accordion-item-content {
  padding: 0.5rem 0.75rem 0.75rem 0.75rem;
  background: #fafbfc;
}

.loading-works {
  padding: 1rem;
  text-align: center;
  color: #666;
  font-size: 0.9rem;
}

.works-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.work-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  transition: all 0.2s;
  min-height: 44px; /* Minimum touch target size for mobile */
}

.work-item:hover {
  background: #f8f9fa;
  border-color: #dee2e6;
}

.work-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  margin-left: 0.75rem;
  flex-shrink: 0;
}

.work-label {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  margin: 0;
  font-size: 0.95rem;
}

.work-icon {
  font-size: 1rem;
}

.work-name {
  color: #333;
}

/* Mobile-specific styles */
@media (max-width: 768px) {
  .accordion-filter {
    padding: 0.75rem;
  }

  .accordion-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .accordion-header h3 {
    font-size: 1rem;
    width: 100%;
  }

  .accordion-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .action-btn {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    flex: 1;
  }

  .accordion-content {
    max-height: 400px;
  }

  .accordion-toggle {
    font-size: 0.95rem;
  }

  .collection-name {
    font-size: 0.95rem;
  }

  .work-count {
    font-size: 0.8rem;
  }

  .work-label {
    font-size: 0.9rem;
  }

  /* Larger touch targets on mobile */
  .collection-checkbox,
  .work-checkbox {
    width: 22px;
    height: 22px;
  }

  .accordion-item-header {
    gap: 0.5rem;
    padding: 0.6rem;
  }

  .accordion-toggle.no-checkbox {
    padding-left: 32px; /* Account for larger checkbox on mobile */
  }
}

/* Extra small screens */
@media (max-width: 480px) {
  .accordion-header h3 {
    font-size: 0.95rem;
  }

  .action-btn {
    font-size: 0.85rem;
    padding: 0.4rem 0.8rem;
  }

  .accordion-toggle {
    font-size: 0.9rem;
    gap: 0.4rem;
  }

  .work-item {
    padding: 0.4rem;
  }
}
</style>
