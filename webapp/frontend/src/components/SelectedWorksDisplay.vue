<template>
  <div class="selected-works-overlay" @click.self="handleClose">
    <div class="selected-works-panel">
      <!-- Header -->
      <div class="panel-header">
        <h2>Selected Works: {{ selectedWorks.length }}</h2>
        <button @click="handleClose" class="close-btn" title="Close">×</button>
      </div>

      <!-- CollectionTree in Read-Only Mode -->
      <div class="panel-content">
        <CollectionTree
          :selected-works="selectedWorks"
          :root-collection-id="designatedCollectionId"
          :read-only="true"
          @update:selectedWorks="() => {}"
        />
      </div>

      <!-- Footer Actions -->
      <div class="panel-footer">
        <button @click="handleClose" class="secondary-btn">
          Close
        </button>
        <button @click="handleChangeSelection" class="primary-btn">
          Change Selection
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineEmits } from 'vue'
import { useFilterState } from '../composables/useFilterState.js'
import CollectionTree from './CollectionTree.vue'

const emit = defineEmits(['close', 'change-selection'])

// Get filter state
const { selectedWorks, designatedCollectionId } = useFilterState()

const handleClose = () => {
  emit('close')
}

const handleChangeSelection = () => {
  emit('change-selection')
}
</script>

<style scoped>
.selected-works-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.selected-works-panel {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  max-width: 800px;
  width: 90%;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 2px solid #dee2e6;
  background: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

.panel-header h2 {
  margin: 0;
  font-size: 1.3rem;
  color: #2c3e50;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 2rem;
  line-height: 1;
  color: #6c757d;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e9ecef;
  color: #495057;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.panel-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #dee2e6;
  background: #f8f9fa;
  border-radius: 0 0 8px 8px;
}

.secondary-btn,
.primary-btn {
  padding: 0.6rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.secondary-btn {
  background: #6c757d;
  color: white;
}

.secondary-btn:hover {
  background: #5a6268;
}

.primary-btn {
  background: #218838;
  color: white;
}

.primary-btn:hover {
  background: #1e7e34;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .selected-works-panel {
    width: 95%;
  }

  .panel-header {
    padding: 1rem;
  }

  .panel-header h2 {
    font-size: 1.1rem;
  }

  .panel-content {
    padding: 1rem;
  }

  .panel-footer {
    padding: 0.75rem 1rem;
    flex-direction: column;
  }

  .secondary-btn,
  .primary-btn {
    width: 100%;
  }
}
</style>
