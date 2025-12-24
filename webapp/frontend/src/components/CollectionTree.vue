<template>
  <div class="collection-tree">
    <div class="tree-header">
      <h3>Collection for Search Filter</h3>
      <div class="tree-actions">
        <button @click="expandAll" class="tree-action-btn" title="Expand all collections">
          Expand All
        </button>
        <button @click="collapseAll" class="tree-action-btn" title="Collapse all collections">
          Collapse All
        </button>
      </div>
    </div>

    <div v-if="loading" class="tree-loading">Loading collections...</div>
    <div v-else-if="error" class="tree-error">{{ error }}</div>
    <div v-else-if="collectionTree.length === 0" class="tree-empty">
      No collections available. Search will work with all works.
    </div>
    <div v-else class="tree-content">
      <TreeNode
        v-for="collection in collectionTree"
        :key="collection.collection_id"
        :collection="collection"
        :expanded-nodes="expandedNodes"
        :selected-works="selectedWorks"
        :selected-collections="selectedCollections"
        @toggle-node="toggleNode"
        @load-works="loadCollectionWorks"
        @toggle-selection="handleToggleSelection"
        @toggle-work="handleWorkToggle"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, defineEmits, defineProps } from 'vue'
import axios from 'axios'
import TreeNode from './TreeNode.vue'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const props = defineProps({
  selectedWorks: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['update:selectedWorks'])

const collectionTree = ref([])
const expandedNodes = ref(new Set())
const selectedCollections = ref(new Set())
const loading = ref(false)
const error = ref(null)
const collectionWorksCache = ref({})

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

// Load works for a collection (just load, don't select)
const loadCollectionWorks = async (collectionId) => {
  // This is called when TreeNode needs to load works for display
  // It should NOT select the works - only checkboxes should do that
  console.log('[LOAD COLLECTION WORKS] Loading works for cache, NOT selecting them')
  await loadCollectionWorksData(collectionId)
}

// Toggle node expansion
const toggleNode = (collectionId) => {
  if (expandedNodes.value.has(collectionId)) {
    expandedNodes.value.delete(collectionId)
  } else {
    expandedNodes.value.add(collectionId)
  }
}

// Expand all nodes and load all works
const expandAll = async () => {
  console.log('[EXPAND ALL] Starting expand all operation...')
  const addAllIds = async (collections) => {
    for (const coll of collections) {
      console.log('[EXPAND ALL] Expanding:', coll.collection_name_tamil, 'work_count:', coll.work_count)
      expandedNodes.value.add(coll.collection_id)

      // Give Vue time to process reactivity and trigger watches
      await new Promise(resolve => setTimeout(resolve, 10))

      // Recursively expand children
      if (coll.children && coll.children.length > 0) {
        await addAllIds(coll.children)
      }
    }
  }
  await addAllIds(collectionTree.value)
  console.log('[EXPAND ALL] Finished. Total expanded:', expandedNodes.value.size)
  console.log('[EXPAND ALL] Selected works count:', props.selectedWorks.length)
  console.log('[EXPAND ALL] Selected collections:', selectedCollections.value.size)
}

// Collapse all nodes
const collapseAll = () => {
  expandedNodes.value.clear()
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

  // Get all descendant collection IDs to mark them as selected/unselected
  const descendantCollectionIds = getAllDescendantCollectionIds(collection)

  if (isChecked) {
    // Mark this collection and all descendants as selected
    descendantCollectionIds.forEach(id => selectedCollections.value.add(id))
  } else {
    // Unmark this collection and all descendants
    descendantCollectionIds.forEach(id => selectedCollections.value.delete(id))
  }

  // Get all work IDs from this collection and descendants
  const workIds = await getAllWorkIdsFromCollection(collection)
  const workIdsArray = Array.from(workIds)

  if (isChecked) {
    // Add these work IDs to selected works (union)
    const updatedSelection = new Set([...props.selectedWorks, ...workIdsArray])
    emit('update:selectedWorks', Array.from(updatedSelection))
  } else {
    // Remove these work IDs from selected works
    const updatedSelection = props.selectedWorks.filter(id => !workIds.has(id))
    emit('update:selectedWorks', updatedSelection)
  }
}


// Clear all selections (called from parent)
const clearSelections = () => {
  selectedCollections.value.clear()
}

// Select all collections (called from parent when switching to "All works")
const selectAll = () => {
  const addAllCollectionIds = (collections) => {
    collections.forEach(coll => {
      if (coll.work_count > 0 || (coll.children && coll.children.length > 0)) {
        selectedCollections.value.add(coll.collection_id)
      }
      if (coll.children && coll.children.length > 0) {
        addAllCollectionIds(coll.children)
      }
    })
  }
  addAllCollectionIds(collectionTree.value)
}

// Expose methods to parent component
defineExpose({
  clearSelections,
  selectAll
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

  // Expand collections
  collectionsToExpand.forEach(id => expandedNodes.value.add(id))

  // Update selected collections
  collectionsToSelect.forEach(id => selectedCollections.value.add(id))
}, { deep: true })

onMounted(async () => {
  await loadCollectionTree()

  // After tree loads, check if there are already selected works
  if (props.selectedWorks && props.selectedWorks.length > 0) {
    // Expand only collections containing selected works
    const { collectionsToExpand, collectionsToSelect } = await findCollectionsWithWorks(props.selectedWorks)
    collectionsToExpand.forEach(id => expandedNodes.value.add(id))
    collectionsToSelect.forEach(id => selectedCollections.value.add(id))
  } else {
    // No selected works - expand all to help user browse
    await expandAll()
  }
})
</script>

<style scoped>
.collection-tree {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 1rem;
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

.tree-actions {
  display: flex;
  gap: 0.5rem;
}

.tree-action-btn {
  padding: 0.25rem 0.75rem;
  font-size: 0.85rem;
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.2s;
}

.tree-action-btn:hover {
  background: #e9ecef;
  border-color: #999;
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

.tree-content {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.tree-content::-webkit-scrollbar {
  width: 8px;
}

.tree-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.tree-content::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.tree-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
