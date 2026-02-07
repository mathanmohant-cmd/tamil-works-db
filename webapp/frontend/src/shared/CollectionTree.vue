<template>
  <div class="collection-tree">
    <div class="tree-header">
      <h3>Choose collection/works to search</h3>
    </div>

    <!-- Control Buttons -->
    <div v-if="!loading && !error && collectionTree.length > 0" class="tree-controls">
      <div class="control-buttons-left">
        <button @click="handleSelectAll" class="control-btn">Select All</button>
        <button @click="handleDeselectAll" class="control-btn">Deselect All</button>
      </div>
      <div class="control-buttons-right">
        <button @click="handleApplyFilter" class="apply-filter-btn">Apply Filter</button>
      </div>
    </div>

    <div v-if="loading" class="tree-loading">Loading collections...</div>
    <div v-else-if="error" class="tree-error">{{ error }}</div>
    <div v-else-if="collectionTree.length === 0" class="tree-empty">
      No collections available. Search will work with all works.
    </div>
    <section
      v-else
      v-for="collection in collectionTree"
      :key="collection.collection_id"
      class="accordion-section"
    >
      <div
        class="accordion-header"
        @click="toggleCollection(collection.collection_id)"
        :class="{ expanded: expandedNodes.has(collection.collection_id) }"
      >
        <input
          type="checkbox"
          class="collection-checkbox"
          :checked="isCollectionSelected(collection)"
          :disabled="readOnly"
          @change="handleCollectionCheckbox(collection, $event)"
          @click.stop
        />
        <span class="collection-name">
          {{ collection.collection_name_tamil || collection.collection_name }}
          <span v-if="getTotalWorkCount(collection) > 0" class="work-count">
            ({{ getSelectedWorkCount(collection) }}/{{ getTotalWorkCount(collection) }})
          </span>
        </span>
        <span class="accordion-icon">
          <span
            class="chevron-icon"
            :class="expandedNodes.has(collection.collection_id) ? 'chevron-up' : 'chevron-down'"
          ></span>
        </span>
      </div>

      <div
        v-if="expandedNodes.has(collection.collection_id)"
        class="accordion-content"
      >
        <!-- Nested collections -->
        <NestedCollectionItem
          v-for="child in collection.children"
          :key="child.collection_id"
          :collection="child"
          :expanded-nodes="expandedNodes"
          :selected-works="selectedWorks"
          :selected-collections="selectedCollections"
          :collection-works="collectionWorksCache"
          :read-only="readOnly"
          @toggle-node="toggleNode"
          @toggle-selection="handleToggleSelection"
          @toggle-work="handleWorkToggle"
          @load-works="loadCollectionWorks"
        />

        <!-- Works list -->
        <div v-if="collectionWorksCache[collection.collection_id]?.length > 0" class="works-list">
          <div
            v-for="work in collectionWorksCache[collection.collection_id]"
            :key="work.work_id"
            class="work-item"
          >
            <input
              type="checkbox"
              class="work-checkbox"
              :checked="selectedWorks.includes(work.work_id)"
              :disabled="readOnly"
              @change="handleWorkCheckbox(work.work_id, $event)"
              @click.stop
            />
            <span class="work-name">{{ work.work_name_tamil || work.work_name }}</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, defineEmits, defineProps } from 'vue'
import axios from 'axios'
import NestedCollectionItem from './NestedCollectionItem.vue'
import api from '../api.js'

const API_BASE_URL = api.getBaseURL()

const props = defineProps({
  selectedWorks: {
    type: Array,
    required: true
  },
  rootCollectionId: {
    type: Number,
    default: null  // If null, show all top-level collections
  },
  readOnly: {
    type: Boolean,
    default: false  // If true, tree is read-only (no checkboxes clickable)
  }
})

const emit = defineEmits(['update:selectedWorks', 'applyFilter'])

const collectionTree = ref([])
const expandedNodes = ref(new Set())
const selectedCollections = ref(new Set())
const loading = ref(false)
const error = ref(null)
const collectionWorksCache = ref({})
const allExpanded = ref(true)  // Start expanded (per existing onMounted behavior)

// Load collection tree
const loadCollectionTree = async () => {
  loading.value = true
  error.value = null
  try {
    let url = `${API_BASE_URL}/collections/tree`
    if (props.rootCollectionId) {
      url += `?root=${props.rootCollectionId}`
    }
    const response = await axios.get(url)
    collectionTree.value = response.data

    // Auto-expand designated collection if specified
    if (props.rootCollectionId && response.data.length > 0) {
      expandedNodes.value.add(response.data[0].collection_id)
    }
  } catch (err) {
    error.value = 'Failed to load collections: ' + err.message
    console.error('Error loading collection tree:', err)
  } finally {
    loading.value = false
  }
}

// Load works for a collection (just load, don't select)
const loadCollectionWorks = async (collectionId) => {
  // This is called when TreeNode needs to load works for display
  // It should NOT select the works - only checkboxes should do that
  console.log('[LOAD COLLECTION WORKS] Loading works for cache, NOT selecting them')
  await loadCollectionWorksData(collectionId)
}

// Toggle node expansion
const toggleNode = (collectionId) => {
  const newSet = new Set(expandedNodes.value)
  if (newSet.has(collectionId)) {
    newSet.delete(collectionId)
  } else {
    newSet.add(collectionId)
  }
  expandedNodes.value = newSet
}

// Expand all nodes and load all works
const expandAll = async () => {
  console.log('[EXPAND ALL] Starting expand all operation...')
  const newSet = new Set()
  const addAllIds = async (collections) => {
    for (const coll of collections) {
      console.log('[EXPAND ALL] Expanding:', coll.collection_name_tamil, 'work_count:', coll.work_count)
      newSet.add(coll.collection_id)

      // Recursively expand children
      if (coll.children && coll.children.length > 0) {
        await addAllIds(coll.children)
      }
    }
  }
  await addAllIds(collectionTree.value)
  expandedNodes.value = newSet
  console.log('[EXPAND ALL] Finished. Total expanded:', expandedNodes.value.size)
  console.log('[EXPAND ALL] Selected works count:', props.selectedWorks.length)
  console.log('[EXPAND ALL] Selected collections:', selectedCollections.value.size)
}

// Collapse all nodes
const collapseAll = () => {
  expandedNodes.value = new Set()
}

// Toggle expand/collapse all
const toggleExpandCollapse = async () => {
  if (allExpanded.value) {
    collapseAll()
    allExpanded.value = false
  } else {
    await expandAll()
    allExpanded.value = true
  }
}

// Find collection by ID in the tree
const findCollection = (collections, collectionId) => {
  for (const coll of collections) {
    if (coll.collection_id === collectionId) {
      return coll
    }
    if (coll.children && coll.children.length > 0) {
      const found = findCollection(coll.children, collectionId)
      if (found) return found
    }
  }
  return null
}

// Recursively get all work IDs from a collection and its children
const getAllWorkIdsFromCollection = async (collection) => {
  const workIds = new Set()

  // Get works directly in this collection
  if (collection.work_count > 0) {
    const works = await loadCollectionWorksData(collection.collection_id)
    works.forEach(w => workIds.add(w.work_id))
  }

  // Recursively get works from children
  if (collection.children && collection.children.length > 0) {
    for (const child of collection.children) {
      const childWorkIds = await getAllWorkIdsFromCollection(child)
      childWorkIds.forEach(id => workIds.add(id))
    }
  }

  return workIds
}

// Load collection works and return the data (not emit)
const loadCollectionWorksData = async (collectionId) => {
  if (collectionWorksCache.value[collectionId]) {
    return collectionWorksCache.value[collectionId]
  }

  try {
    const response = await axios.get(`${API_BASE_URL}/collections/${collectionId}/works`)
    collectionWorksCache.value[collectionId] = response.data
    return response.data
  } catch (err) {
    console.error(`Error loading works for collection ${collectionId}:`, err)
    return []
  }
}

// Get all descendant collection IDs (including the collection itself)
const getAllDescendantCollectionIds = (collection) => {
  const ids = new Set([collection.collection_id])

  if (collection.children && collection.children.length > 0) {
    collection.children.forEach(child => {
      const childIds = getAllDescendantCollectionIds(child)
      childIds.forEach(id => ids.add(id))
    })
  }

  return ids
}

// Handle individual work toggle
const handleWorkToggle = ({ workId, isChecked }) => {
  if (isChecked) {
    // Add this work to selected works
    if (!props.selectedWorks.includes(workId)) {
      emit('update:selectedWorks', [...props.selectedWorks, workId])
    }
  } else {
    // Remove this work from selected works
    emit('update:selectedWorks', props.selectedWorks.filter(id => id !== workId))
  }
}

// Handle checkbox toggle selection
const handleToggleSelection = async ({ collectionId, isChecked }) => {
  const collection = findCollection(collectionTree.value, collectionId)
  if (!collection) return

  console.log('[CollectionTree] Toggle selection:', {
    collectionId,
    collectionName: collection.collection_name_tamil,
    isChecked,
    workCount: collection.work_count
  })

  // Get all descendant collection IDs to mark them as selected/unselected
  const descendantCollectionIds = getAllDescendantCollectionIds(collection)

  // Create new Set for reactivity
  const newSelectedCollections = new Set(selectedCollections.value)

  if (isChecked) {
    // Mark this collection and all descendants as selected
    descendantCollectionIds.forEach(id => newSelectedCollections.add(id))
  } else {
    // Unmark this collection and all descendants
    descendantCollectionIds.forEach(id => newSelectedCollections.delete(id))
  }

  // Update selectedCollections with new Set
  selectedCollections.value = newSelectedCollections

  // Get all work IDs from this collection and descendants
  const workIds = await getAllWorkIdsFromCollection(collection)
  const workIdsArray = Array.from(workIds)

  console.log('[CollectionTree] Work IDs loaded:', {
    count: workIdsArray.length,
    workIds: workIdsArray
  })

  if (isChecked) {
    // Add these work IDs to selected works (union)
    const updatedSelection = new Set([...props.selectedWorks, ...workIdsArray])
    const finalArray = Array.from(updatedSelection)
    console.log('[CollectionTree] Emitting selected works:', finalArray)
    emit('update:selectedWorks', finalArray)
  } else {
    // Remove these work IDs from selected works
    const updatedSelection = props.selectedWorks.filter(id => !workIds.has(id))
    console.log('[CollectionTree] Emitting deselected works:', updatedSelection)
    emit('update:selectedWorks', updatedSelection)
  }
}

// Toggle accordion + load works if needed
const toggleCollection = (collectionId) => {
  toggleNode(collectionId)
  if (expandedNodes.value.has(collectionId)) {
    loadCollectionWorksIfNeeded(collectionId)
  }
}

// Load works if not already cached
const loadCollectionWorksIfNeeded = async (collectionId) => {
  if (!collectionWorksCache.value[collectionId]) {
    await loadCollectionWorksData(collectionId)
  }
}

// Collection checkbox handler
const handleCollectionCheckbox = async (collection, event) => {
  event.stopPropagation()
  const isChecked = event.target.checked
  await handleToggleSelection({
    collectionId: collection.collection_id,
    isChecked
  })
}

// Work checkbox handler
const handleWorkCheckbox = (workId, event) => {
  event.stopPropagation()
  const isChecked = event.target.checked
  handleWorkToggle({ workId, isChecked })
}

// Calculate total work count recursively
const getTotalWorkCount = (collection) => {
  let count = collection.work_count || 0
  if (collection.children) {
    collection.children.forEach(child => {
      count += getTotalWorkCount(child)
    })
  }
  return count
}

// Calculate selected work count for a collection and its descendants
const getSelectedWorkCount = (collection) => {
  let count = 0

  // Count selected works directly in this collection
  const works = collectionWorksCache.value[collection.collection_id] || []
  works.forEach(work => {
    if (props.selectedWorks.includes(work.work_id)) {
      count++
    }
  })

  // Recursively count in children
  if (collection.children) {
    collection.children.forEach(child => {
      count += getSelectedWorkCount(child)
    })
  }

  return count
}

// Check if collection is selected
const isCollectionSelected = (collection) => {
  return selectedCollections.value.has(collection.collection_id)
}

// Handle Select All button - expand all and select all
const handleSelectAll = async () => {
  await expandAll()
  await selectAll()
}

// Handle Deselect All button - deselect all and collapse all
const handleDeselectAll = () => {
  clearSelections()
  collapseAll()
}

// Handle Apply Filter button - emit event for parent
const handleApplyFilter = () => {
  emit('applyFilter')
}

// Clear all selections (called from parent)
const clearSelections = () => {
  selectedCollections.value = new Set()
  emit('update:selectedWorks', [])
}

// Select all collections (called from parent when switching to "All works")
const selectAll = async () => {
  const allWorkIds = new Set()
  const allCollectionIds = new Set()

  const addAllCollectionIdsAndWorks = async (collections) => {
    for (const coll of collections) {
      if (coll.work_count > 0 || (coll.children && coll.children.length > 0)) {
        allCollectionIds.add(coll.collection_id)

        // Load works for this collection
        if (coll.work_count > 0) {
          const works = await loadCollectionWorksData(coll.collection_id)
          works.forEach(w => allWorkIds.add(w.work_id))
        }
      }

      if (coll.children && coll.children.length > 0) {
        await addAllCollectionIdsAndWorks(coll.children)
      }
    }
  }

  await addAllCollectionIdsAndWorks(collectionTree.value)

  // Update selected collections with new Set
  selectedCollections.value = allCollectionIds

  // Emit all collected work IDs
  emit('update:selectedWorks', Array.from(allWorkIds))
  console.log('[CollectionTree] Select All - emitted work IDs:', Array.from(allWorkIds))
}

// Expose methods and state to parent component
defineExpose({
  clearSelections,
  selectAll,
  expandAll,
  collapseAll,
  loading
})

// Find all collections that contain any of the selected works
const findCollectionsWithWorks = async (workIds) => {
  const collectionsToExpand = new Set()
  const collectionsToSelect = new Set()

  const checkCollection = async (collection, parentIds = []) => {
    // Load works for this collection if it has any
    if (collection.work_count > 0) {
      const works = await loadCollectionWorksData(collection.collection_id)
      const workIdsInCollection = works.map(w => w.work_id)

      // Check if any selected works are in this collection
      const hasSelectedWorks = workIdsInCollection.some(id => workIds.includes(id))

      if (hasSelectedWorks) {
        // Expand this collection and all parents
        collectionsToExpand.add(collection.collection_id)
        parentIds.forEach(id => collectionsToExpand.add(id))

        // If ALL works in this collection are selected, mark it as selected
        const allWorksSelected = workIdsInCollection.every(id => workIds.includes(id))
        if (allWorksSelected) {
          collectionsToSelect.add(collection.collection_id)
        }
      }
    }

    // Recursively check children
    if (collection.children && collection.children.length > 0) {
      for (const child of collection.children) {
        await checkCollection(child, [...parentIds, collection.collection_id])
      }
    }
  }

  // Check all root collections
  for (const rootCollection of collectionTree.value) {
    await checkCollection(rootCollection)
  }

  return { collectionsToExpand, collectionsToSelect }
}

// Watch for changes to selectedWorks and auto-expand/select
watch(() => props.selectedWorks, async (newSelectedWorks) => {
  if (!newSelectedWorks || newSelectedWorks.length === 0 || collectionTree.value.length === 0) {
    return
  }

  const { collectionsToExpand, collectionsToSelect } = await findCollectionsWithWorks(newSelectedWorks)

  // Expand collections - create new Set for reactivity
  const newExpandedSet = new Set(expandedNodes.value)
  collectionsToExpand.forEach(id => newExpandedSet.add(id))
  expandedNodes.value = newExpandedSet

  // Update selected collections - create new Set for reactivity
  const newSelectedSet = new Set(selectedCollections.value)
  collectionsToSelect.forEach(id => newSelectedSet.add(id))
  selectedCollections.value = newSelectedSet
}, { deep: true })

onMounted(async () => {
  await loadCollectionTree()

  // After tree loads, check if there are already selected works
  if (props.selectedWorks && props.selectedWorks.length > 0) {
    // Expand only collections containing selected works
    const { collectionsToExpand, collectionsToSelect } = await findCollectionsWithWorks(props.selectedWorks)

    // Create new Sets for reactivity
    expandedNodes.value = new Set(collectionsToExpand)
    selectedCollections.value = new Set(collectionsToSelect)
  }
  // If no selected works, start with everything collapsed for cleaner UX
})
</script>

<style scoped>
.collection-tree {
  /* No separate box - blend into parent container */
  margin-bottom: 1rem;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #dee2e6;
}

.tree-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
}

.tree-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.control-buttons-left {
  display: flex;
  gap: 0.5rem;
}

.control-buttons-right {
  display: flex;
  gap: 0.5rem;
}

.control-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.control-btn:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.apply-filter-btn {
  padding: 0.5rem 1.25rem;
  background: #218838;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background 0.2s ease;
}

.apply-filter-btn:hover {
  background: #1e7e34;
}

.tree-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  width: 32px;
  height: 32px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.tree-action-btn:hover {
  background: linear-gradient(135deg, #1a3a5a 0%, #1e2a5a 100%);
}

.tree-action-btn .chevron-icon {
  display: inline-block;
  width: 10px;
  height: 10px;
  border: none;
  border-right: 2px solid white;
  border-bottom: 2px solid white;
  transition: transform 0.2s ease;
}

.chevron-up {
  transform: rotate(-135deg); /* Points up ▲ */
}

.chevron-down {
  transform: rotate(45deg);   /* Points down ▼ */
}

.tree-loading,
.tree-error,
.tree-empty {
  padding: 1rem;
  text-align: center;
  color: #666;
}

.tree-error {
  color: #dc3545;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}

.tree-empty {
  color: #6c757d;
  font-style: italic;
}

/* Accordion styles */
.accordion-section {
  border-bottom: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-left: 3px solid transparent;
  gap: 0.75rem;
  transition: all 0.3s ease;
  user-select: none;
}

.accordion-header:hover {
  background: transparent;
  border-left: 3px solid transparent;
}

.accordion-header.expanded {
  background: transparent;
  border-left: 3px solid transparent;
}

.collection-checkbox {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  cursor: pointer;
}

.collection-name {
  flex: 1;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--primary-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.work-count {
  font-size: 0.9rem;
  font-weight: 400;
  color: #666;
}

.accordion-icon {
  width: 30px;
  height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.accordion-content {
  padding: 0.5rem 0 0.5rem 1rem;
  background: white;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.works-list {
  margin-top: 0.5rem;
}

.work-item {
  display: flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  min-height: 44px;
  gap: 0.75rem;
  transition: background 0.2s ease;
}

.work-item:hover {
  background: #f9f9f9;
}

.work-name {
  flex: 1;
  font-size: 1rem;
}

.work-checkbox {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  cursor: pointer;
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .collection-tree {
    margin-bottom: 1rem;
    overflow-x: hidden; /* Prevent horizontal scroll */
  }

  .tree-header {
    flex-direction: row;
    align-items: flex-start;
    justify-content: space-between;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }

  .tree-header h3 {
    font-size: 1rem; /* Slightly smaller on mobile */
    margin: 0;
  }

  .tree-actions {
    width: 100%;
    justify-content: space-between;
  }

  .tree-action-btn {

    padding: 0.4rem 0.5rem; /* Slightly smaller buttons */
    font-size: 0.85rem;
    width: 32px;
    height: 32px;
  }

  .accordion-header {
    padding: 0.75rem 0.5rem;
    gap: 0.5rem;
  }

  .collection-name {
    font-size: 1rem;
  }

  .accordion-content {
    padding-left: 0.5rem;
  }

  .work-item {
    padding: 0.5rem;
  }
}
</style>
