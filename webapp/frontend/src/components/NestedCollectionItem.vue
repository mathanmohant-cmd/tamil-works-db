<template>
  <div class="nested-collection-item">
    <div class="nested-header" @click="handleHeaderClick" :class="{ expanded: isExpanded }">
      <input
        type="checkbox"
        class="collection-checkbox"
        :checked="isCollectionSelected"
        :disabled="readOnly"
        @change="handleCheckboxChange"
        @click.stop
      />
      <span class="collection-name">
        {{ collection.collection_name_tamil || collection.collection_name }}
        <span v-if="totalWorkCount > 0" class="work-count">({{ selectedWorkCount }}/{{ totalWorkCount }})</span>
      </span>
      <span
        v-if="hasChildren || hasWorks"
        class="nested-chevron"
        @click.stop="handleChevronClick"
      >
        <span
          class="chevron-icon"
          :class="isExpanded ? 'chevron-up' : 'chevron-down'"
        ></span>
      </span>
    </div>

    <div v-if="isExpanded" class="nested-content">
      <!-- Recursive nested collections -->
      <NestedCollectionItem
        v-for="child in collection.children"
        :key="child.collection_id"
        :collection="child"
        :expanded-nodes="expandedNodes"
        :selected-works="selectedWorks"
        :selected-collections="selectedCollections"
        :collection-works="collectionWorks"
        :read-only="readOnly"
        @toggle-node="$emit('toggle-node', $event)"
        @toggle-selection="$emit('toggle-selection', $event)"
        @toggle-work="$emit('toggle-work', $event)"
        @load-works="$emit('load-works', $event)"
      />

      <!-- Works list -->
      <div v-if="works.length > 0" class="works-list">
        <div
          v-for="work in works"
          :key="work.work_id"
          class="work-item"
        >
          <input
            type="checkbox"
            class="work-checkbox"
            :checked="isWorkSelected(work.work_id)"
            :disabled="readOnly"
            @change="handleWorkToggle(work.work_id, $event)"
            @click.stop
          />
          <span class="work-name">{{ work.work_name_tamil || work.work_name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

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
  },
  collectionWorks: {
    type: Object,
    required: true
  },
  readOnly: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggle-node', 'toggle-selection', 'toggle-work', 'load-works'])

// Computed properties
const isExpanded = computed(() => props.expandedNodes.has(props.collection.collection_id))

const isCollectionSelected = computed(() =>
  props.selectedCollections.has(props.collection.collection_id)
)

const hasChildren = computed(() =>
  props.collection.children && props.collection.children.length > 0
)

const hasWorks = computed(() =>
  props.collection.work_count > 0
)

const works = computed(() =>
  props.collectionWorks[props.collection.collection_id] || []
)

const totalWorkCount = computed(() => {
  let count = props.collection.work_count || 0
  if (props.collection.children) {
    props.collection.children.forEach(child => {
      count += getTotalWorkCountRecursive(child)
    })
  }
  return count
})

const selectedWorkCount = computed(() => {
  let count = 0

  // Count selected works directly in this collection
  const collectionWorks = props.collectionWorks[props.collection.collection_id] || []
  collectionWorks.forEach(work => {
    if (props.selectedWorks.includes(work.work_id)) {
      count++
    }
  })

  // Recursively count in children
  if (props.collection.children) {
    props.collection.children.forEach(child => {
      count += getSelectedWorkCountRecursive(child)
    })
  }

  return count
})

// Helper methods
const getTotalWorkCountRecursive = (collection) => {
  let count = collection.work_count || 0
  if (collection.children) {
    collection.children.forEach(child => {
      count += getTotalWorkCountRecursive(child)
    })
  }
  return count
}

const getSelectedWorkCountRecursive = (collection) => {
  let count = 0

  // Count selected works directly in this collection
  const collectionWorks = props.collectionWorks[collection.collection_id] || []
  collectionWorks.forEach(work => {
    if (props.selectedWorks.includes(work.work_id)) {
      count++
    }
  })

  // Recursively count in children
  if (collection.children) {
    collection.children.forEach(child => {
      count += getSelectedWorkCountRecursive(child)
    })
  }

  return count
}

const isWorkSelected = (workId) => {
  return props.selectedWorks.includes(workId)
}

// Event handlers
const handleHeaderClick = () => {
  if (hasChildren.value || hasWorks.value) {
    handleChevronClick()
  }
}

const handleChevronClick = () => {
  emit('toggle-node', props.collection.collection_id)

  // Load works if expanding and has works
  if (!isExpanded.value && hasWorks.value) {
    emit('load-works', props.collection.collection_id)
  }
}

const handleCheckboxChange = (event) => {
  const isChecked = event.target.checked
  emit('toggle-selection', {
    collectionId: props.collection.collection_id,
    isChecked
  })
}

const handleWorkToggle = (workId, event) => {
  const isChecked = event.target.checked
  emit('toggle-work', { workId, isChecked })
}
</script>

<style scoped>
.nested-collection-item {
  padding-left: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.nested-header {
  display: flex;
  align-items: center;
  padding: 0.5rem 0.5rem;
  gap: 0.5rem;
  cursor: pointer;
  min-height: 44px;
  transition: all 0.3s ease;
  user-select: none;
  border-left: 3px solid transparent;
}

.nested-header:hover {
  background: transparent;
  border-left: 3px solid transparent;
}

.nested-header.expanded {
  background: transparent;
  border-left: 3px solid transparent;
}

.collection-checkbox {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  cursor: pointer;
}

.nested-chevron {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nested-chevron .chevron-icon {
  width: 8px;
  height: 8px;
  display: inline-block;
  border: none;
  border-right: 2px solid currentColor;
  border-bottom: 2px solid currentColor;
  transition: transform 0.2s ease;
  color: #666;
}

.chevron-up {
  transform: rotate(-135deg); /* Points up ▲ */
}

.chevron-down {
  transform: rotate(45deg);   /* Points down ▼ */
}

.collection-name {
  flex: 1;
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.work-count {
  font-size: 0.85rem;
  font-weight: 400;
  color: #666;
}

.nested-content {
  padding-left: 1rem;
}

.works-list {
  margin-top: 0.25rem;
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
  background: #f5f5f5;
}

.work-name {
  flex: 1;
  font-size: 0.95rem;
}

.work-checkbox {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  cursor: pointer;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .nested-collection-item {
    padding-left: 1rem;
  }

  .nested-header {
    padding: 0.5rem 0.25rem;
    gap: 0.4rem;
  }

  .collection-name {
    font-size: 0.95rem;
  }

  .nested-content {
    padding-left: 0.5rem;
  }

  .work-item {
    padding: 0.5rem;
    gap: 0.5rem;
  }

  .work-name {
    font-size: 0.9rem;
  }
}
</style>
