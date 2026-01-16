<template>
  <div v-if="localVisible" class="search-controls">
    <!-- Work Filter Radio Buttons -->
    <div class="work-filter-options">
      <div class="filter-group-inline">
        <span class="filter-label">Search in:</span>
        <label>
          <input type="radio" v-model="filterMode" value="all" @change="handleFilterModeChange" />
          All works
        </label>
        <label>
          <input type="radio" v-model="filterMode" value="select" @change="handleFilterModeChange" />
          Selected works
        </label>
      </div>
      <button v-if="filterMode === 'select'" @click="toggleFilters" class="filter-selection-button">
        {{ worksFilterButtonText }}
      </button>
    </div>

    <!-- Match Type & Word Position -->
    <div class="match-type-options">
      <div class="filter-group-inline">
        <span class="filter-label">Match:</span>
        <label>
          <input type="radio" v-model="matchType" value="partial" />
          Partial
        </label>
        <label>
          <input type="radio" v-model="matchType" value="exact" />
          Exact
        </label>
      </div>
      <div class="filter-group-inline" :class="{ 'filter-disabled': matchType === 'exact' }">
        <span class="filter-label">Position:</span>
        <label>
          <input type="radio" v-model="wordPosition" value="beginning" :disabled="matchType === 'exact'" />
          Start
        </label>
        <label>
          <input type="radio" v-model="wordPosition" value="end" :disabled="matchType === 'exact'" />
          End
        </label>
        <label>
          <input type="radio" v-model="wordPosition" value="anywhere" :disabled="matchType === 'exact'" />
          Any
        </label>
      </div>
    </div>

    <!-- Collapsible Filters Panel -->
    <div class="filters-panel" v-show="filtersExpanded">
      <div class="filter-group" v-if="works.length">
        <div class="filter-header">
          <div style="flex: 1;"></div>
          <div class="filter-header-actions">
            <button @click="clearFilters" class="clear-filter-button" title="Uncheck all works">
              Deselect All
            </button>
            <button @click="closeFilters" class="done-button">Done</button>
          </div>
        </div>

        <!-- Collection Tree Filter -->
        <div class="filter-content-wrapper">
          <CollectionTree
            ref="collectionTreeRef"
            :selected-works="selectedWorks"
            :root-collection-id="designatedCollectionId"
            @update:selectedWorks="handleCollectionSelection"
          />

          <!-- Selected Works Summary -->
          <div class="selected-works-summary">
            <div class="selected-works-header">
              <strong>Selected Works: {{ selectedWorks.length }}</strong>
              <button v-if="selectedWorks.length > 0" @click="clearFilters" class="clear-selection-btn">
                Deselect All
              </button>
            </div>
            <div v-if="selectedWorks.length > 0" class="selected-works-preview">
              <div class="selected-work-chip" v-for="workId in sortedSelectedWorks.slice(0, 15)" :key="workId">
                <span
                  class="work-chip-name"
                  :title="getWorkChronologyTooltip(getWorkById(workId))"
                >
                  {{ getWorkName(workId) }}
                </span>
                <button @click="removeWork(workId)" class="remove-chip-btn" title="Remove">×</button>
              </div>
              <div v-if="selectedWorks.length > 15" class="more-works-indicator">
                +{{ selectedWorks.length - 15 }} more
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSearchState } from '../../composables/useSearchState.js'
import { useFilterState } from '../../composables/useFilterState.js'
import CollectionTree from '../CollectionTree.vue'

const router = useRouter()
const route = useRoute()

// Use composables
const { matchType, wordPosition, searchQuery } = useSearchState()
const {
  filterMode,
  selectedWorks,
  works,
  filtersExpanded,
  designatedCollectionId,
  worksFilterButtonText,
  sortedSelectedWorks,
  hasFiltersChanged,
  getWorkName,
  getWorkById,
  getWorkChronologyTooltip,
  toggleFilters,
  closeFilters: closeFiltersOriginal,
  clearFilters,
  removeWork,
  handleFilterModeChange,
  handleCollectionSelection
} = useFilterState()

// Local visibility state controlled by header toggle (default to closed)
const localVisible = ref(false)

// Override closeFilters to trigger search if filters changed
const closeFilters = () => {
  // Check if we're on SearchResults page and filters have changed
  if (hasFiltersChanged.value && route.name === 'SearchResults' && searchQuery.value) {
    // Trigger search with timestamp to force route change
    router.push({
      name: 'SearchResults',
      query: {
        ...route.query,
        _t: Date.now() // Timestamp forces route change even if other params same
      }
    })
  }
  // Close the filters panel
  closeFiltersOriginal()
}

// Listen for toggle event from header
const handleToggleEvent = (event) => {
  localVisible.value = event.detail.expanded
}

onMounted(() => {
  window.addEventListener('toggle-filter-options', handleToggleEvent)
})

onUnmounted(() => {
  window.removeEventListener('toggle-filter-options', handleToggleEvent)
})
</script>

<style scoped>
.search-controls {
  margin-bottom: 1rem;
}

.work-filter-options,
.match-type-options {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
  padding: 0.75rem .05rem;
  background: #f8f9fa;
  border-radius: 6px;
}

.filter-group-inline {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.filter-label {
  font-weight: 600;
  color: #495057;
  white-space: nowrap;
}

.filter-group-inline label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  cursor: pointer;
  font-size: 0.95rem;
  color: #495057;
  white-space: nowrap;
}

.filter-group-inline input[type="radio"] {
  cursor: pointer;
  width: 16px;
  height: 16px;
}

.filter-disabled {
  opacity: 0.5;
  pointer-events: none;
}

.filter-selection-button {
  padding: 0.4rem 1rem;
  background-color: #218838;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.filter-selection-button:hover {
  background-color: #1e7e34;
}

/* Filters Panel */
.filters-panel {
  background: #ffffff;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  animation: slideDown 0.2s ease-out;
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

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #dee2e6;
  background: #f8f9fa;
  border-radius: 6px 6px 0 0;
}

.filter-header-actions {
  display: flex;
  gap: 0.5rem;
}

.clear-filter-button,
.done-button {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: background-color 0.2s;
}

.clear-filter-button {
  background-color: #218838;
  color: white;
}

.clear-filter-button:hover {
  background-color: #1e7e34;
}

.done-button {
  background-color: #218838;
  color: white;
}

.done-button:hover {
  background-color: #1e7e34;
}

.filter-content-wrapper {
  padding: 1rem;
  /* No scroll here - let CollectionTree handle scrolling */
}

/* Selected Works Summary */
.selected-works-summary {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 2px solid #dee2e6;
}

.selected-works-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.clear-selection-btn {
  padding: 0.3rem 0.7rem;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: background-color 0.2s;
}

.clear-selection-btn:hover {
  background-color: #c82333;
}

.selected-works-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.selected-work-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.6rem;
  background: #e7f3ff;
  border: 1px solid #4a90e2;
  border-radius: 16px;
  font-size: 0.85rem;
}

.work-chip-name {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-chip-btn {
  background: transparent;
  border: none;
  color: #4a90e2;
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.remove-chip-btn:hover {
  color: #dc3545;
}

.more-works-indicator {
  padding: 0.3rem 0.8rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 16px;
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 600;
}

/* Mobile Responsive */
@media (max-width: 968px) {
  .match-type-options {
    /* Keep radio buttons in one line on mobile */
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .filter-group-inline {
    /* Allow wrapping but don't force full width */
    flex-shrink: 0;
  }
}

@media (max-width: 768px) {
  .work-filter-options,
  .match-type-options {
    padding: 0.5rem 0.5rem;
  }

  .filter-group-inline label {
    font-size: 0.9rem;
  }

  .filter-selection-button {
    font-size: 0.85rem;
    padding: 0.35rem 0.5rem;
  }
}
</style>
