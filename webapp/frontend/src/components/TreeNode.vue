<template>
  <div class="tree-node">
    <div class="node-item" :class="{ 'has-children': hasChildren }">
      <!-- Expand/Collapse Icon (only this is clickable for expand/collapse) -->
      <span
        v-if="hasChildren"
        @click.stop="handleToggle"
        class="toggle-icon"
      >
        {{ isExpanded ? '▼' : '▶' }}
      </span>
      <span v-else class="toggle-spacer"></span>

      <!-- Checkbox for selecting collection works -->
      <input
        v-if="hasWorksInTree"
        type="checkbox"
        :checked="isSelected"
        @change="handleCheckboxChange"
        class="collection-checkbox"
        @click.stop
      />
      <span v-else class="checkbox-spacer"></span>

      <!-- Folder/Document Icon -->
      <span class="node-icon">
        {{ hasChildren ? (isExpanded ? '📂' : '📁') : '📄' }}
      </span>

      <!-- Collection Name (not clickable) -->
      <span class="node-name">
        {{ collection.collection_name_tamil || collection.collection_name }}
        <span v-if="totalWorkCount > 0" class="work-count">({{ totalWorkCount }})</span>
      </span>
    </div>

    <!-- Children (if expanded) -->
    <div v-if="isExpanded" class="node-children">
      <!-- Child collections -->
      <TreeNode
        v-for="child in collection.children"
        :key="'coll-' + child.collection_id"
        :collection="child"
        :expanded-nodes="expandedNodes"
        :selected-works="selectedWorks"
        :selected-collections="selectedCollections"
        @toggle-node="$emit('toggle-node', $event)"
        @load-works="$emit('load-works', $event)"
        @toggle-selection="$emit('toggle-selection', $event)"
        @toggle-work="$emit('toggle-work', $event)"
      />

      <!-- Works (leaf nodes) -->
      <div
        v-if="collection.work_count > 0 && collectionWorks.length > 0"
        class="works-list"
      >
        <div
          v-for="work in collectionWorks"
          :key="'work-' + work.work_id"
          class="work-node"
        >
          <span class="toggle-spacer"></span>
          <input
            type="checkbox"
            :checked="isWorkSelected(work.work_id)"
            @change="handleWorkToggle(work.work_id, $event)"
            class="work-checkbox"
            @click.stop
          />
          <span class="node-icon">📄</span>
          <span class="work-name">{{ work.work_name_tamil || work.work_name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  collection: {
    type: Object,
    required: true
  },
  expandedNodes: {
    type: Set,
    required: true
  },
  selectedWorks: {
    type: Array,
    required: true
  },
  selectedCollections: {
    type: Set,
    required: true
  }
})

const emit = defineEmits(['toggle-node', 'load-works', 'toggle-selection', 'toggle-work'])

const collectionWorks = ref([])

const hasChildren = computed(() => {
  // A collection "has children" if it has either child collections OR works
  return (props.collection.children && props.collection.children.length > 0) ||
         (props.collection.work_count > 0)
})

const isExpanded = computed(() => {
  return props.expandedNodes.has(props.collection.collection_id)
})

// Watch for expansion to load works
watch(() => props.expandedNodes.has(props.collection.collection_id), async (nowExpanded, wasExpanded) => {
  try {
    console.log('[WATCH]', props.collection.collection_name_tamil, 'nowExpanded:', nowExpanded, 'wasExpanded:', wasExpanded, 'work_count:', props.collection.work_count, 'collectionWorks.length:', collectionWorks.value.length)

    // If newly expanded and has works but not loaded yet
    // Handle both undefined and false for wasExpanded (immediate run vs normal run)
    const isNewlyExpanded = nowExpanded && (wasExpanded === false || wasExpanded === undefined)

    if (isNewlyExpanded && props.collection.work_count > 0 && collectionWorks.value.length === 0) {
      console.log('[AUTO-LOAD] Collection', props.collection.collection_name_tamil, 'was expanded externally, loading works...')
      await loadWorks()
    } else if (nowExpanded && props.collection.work_count > 0 && collectionWorks.value.length === 0) {
      console.warn('[WATCH SKIPPED]', props.collection.collection_name_tamil, 'Conditions not met - wasExpanded:', wasExpanded)
    }
  } catch (error) {
    console.error('[WATCH ERROR] for', props.collection.collection_name_tamil, error)
  }
})

// Calculate total work count including children recursively
const totalWorkCount = computed(() => {
  let count = props.collection.work_count || 0
  if (props.collection.children) {
    props.collection.children.forEach(child => {
      count += getTotalWorkCountRecursive(child)
    })
  }
  return count
})

const getTotalWorkCountRecursive = (coll) => {
  let count = coll.work_count || 0
  if (coll.children) {
    coll.children.forEach(child => {
      count += getTotalWorkCountRecursive(child)
    })
  }
  return count
}

// Check if this collection or any children have works
const hasWorksInTree = computed(() => {
  return totalWorkCount.value > 0
})

// Check if this collection is selected
const isSelected = computed(() => {
  return props.selectedCollections.has(props.collection.collection_id)
})

const handleToggle = async () => {
  const wasExpanded = isExpanded.value
  console.log('[TRIANGLE CLICK] Toggling collection:', props.collection.collection_name_tamil, 'Expanded:', wasExpanded, '-> Will be:', !wasExpanded)

  emit('toggle-node', props.collection.collection_id)

  // Load works when expanding (going from collapsed to expanded)
  if (!wasExpanded && props.collection.work_count > 0 && collectionWorks.value.length === 0) {
    // Wait a bit for expandedNodes to update
    await new Promise(resolve => setTimeout(resolve, 50))
    await loadWorks()
  }
  console.log('[TRIANGLE CLICK] Done toggling - NO SELECTION HAPPENED')
}

const loadWorks = async () => {
  // Emit load-works and wait for it to return the works
  emit('load-works', props.collection.collection_id)

  // The parent will handle loading, but we need to get the works
  // We'll use a workaround by importing axios here
  const axios = (await import('axios')).default
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

  try {
    const response = await axios.get(`${API_BASE_URL}/collections/${props.collection.collection_id}/works`)
    collectionWorks.value = response.data
    console.log(`[LOAD WORKS] Loaded ${response.data.length} works for collection:`, props.collection.collection_name_tamil)

    // Check which works are already selected
    const selectedCount = response.data.filter(w => props.selectedWorks.includes(w.work_id)).length
    if (selectedCount > 0) {
      console.warn(`[LOAD WORKS] ${selectedCount} of ${response.data.length} works are ALREADY SELECTED (probably from parent collection checkbox)`)
    } else {
      console.log(`[LOAD WORKS] None of the works are selected yet - checkboxes will be unchecked`)
    }
  } catch (err) {
    console.error('Error loading works:', err)
  }
}

const isWorkSelected = (workId) => {
  return props.selectedWorks.includes(workId)
}

const handleWorkToggle = (workId, event) => {
  const isChecked = event.target.checked
  emit('toggle-work', { workId, isChecked })
}

const handleCheckboxChange = (event) => {
  const isChecked = event.target.checked
  console.log('[CHECKBOX CLICK] Collection checkbox changed:', props.collection.collection_name_tamil, 'Checked:', isChecked)
  emit('toggle-selection', {
    collectionId: props.collection.collection_id,
    isChecked
  })
}
</script>

<style scoped>
.tree-node {
  margin-left: 0;
}

.node-item {
  display: flex;
  align-items: center;
  padding: 0.4rem 0.5rem;
  cursor: pointer;
  border-radius: 3px;
  transition: background-color 0.2s;
}

.node-item:hover {
  background-color: #e9ecef;
}

.toggle-icon {
  cursor: pointer;
  user-select: none;
  font-size: 0.75rem;
  width: 1rem;
  display: inline-block;
  color: #666;
}

.toggle-icon:hover {
  color: #000;
}

.toggle-spacer {
  width: 1rem;
  display: inline-block;
}

.collection-checkbox {
  margin: 0 0.5rem;
  cursor: pointer;
  width: 16px;
  height: 16px;
}

.checkbox-spacer {
  width: 16px;
  margin: 0 0.5rem;
  display: inline-block;
}

.node-icon {
  margin: 0 0.5rem;
  font-size: 1rem;
}

.node-name {
  flex: 1;
  font-size: 0.95rem;
  color: #333;
}

.work-count {
  font-size: 0.85rem;
  color: #666;
  margin-left: 0.25rem;
}

.node-children {
  margin-left: 1.5rem;
  padding-left: 0.5rem;
}

.has-children .node-name {
  font-weight: 500;
}

.works-list {
  margin-left: 0;
}

.work-node {
  display: flex;
  align-items: center;
  padding: 0.3rem 0.5rem;
  cursor: pointer;
  border-radius: 3px;
  transition: background-color 0.2s;
}

.work-node:hover {
  background-color: #f0f0f0;
}

.work-checkbox {
  margin: 0 0.5rem;
  cursor: pointer;
  width: 16px;
  height: 16px;
}

.work-name {
  flex: 1;
  font-size: 0.9rem;
  color: #555;
}
</style>
