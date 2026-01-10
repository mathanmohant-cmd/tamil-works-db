<template>
  <div class="section-node">
    <div class="section-header" @click="navigateToSection">
      <div class="section-info">
        <span v-if="section.children && section.children.length > 0" class="toggle-icon" @click.stop="toggleExpanded">
          {{ isExpanded ? '▼' : '▶' }}
        </span>
        <span class="section-level-type">
          {{ section.level_type_tamil || section.level_type }}
          {{ section.section_number }}:
        </span>
        <span class="section-name">
          {{ section.section_name_tamil || section.section_name }}
        </span>
      </div>
      <div class="section-meta">
        <span class="verse-count" v-if="section.verse_count > 0">
          {{ section.verse_count }} verses
        </span>
      </div>
    </div>

    <!-- Children sections (recursive) -->
    <div v-if="isExpanded && section.children && section.children.length > 0" class="section-children">
      <SectionTreeNode
        v-for="child in section.children"
        :key="child.section_id"
        :section="child"
        :work-id="workId"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  section: {
    type: Object,
    required: true
  },
  workId: {
    type: [String, Number],
    required: true
  }
})

const router = useRouter()
const isExpanded = ref(false)

// Toggle expand/collapse
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

// Navigate to section view
const navigateToSection = () => {
  router.push({
    name: 'SectionView',
    params: {
      workId: props.workId,
      sectionId: props.section.section_id
    }
  })
}
</script>

<style scoped>
.section-node {
  margin-left: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.section-header:hover {
  background: #f0f0f0;
  border-color: #1976d2;
}

.section-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.toggle-icon {
  font-size: 0.8rem;
  color: #666;
  width: 20px;
  text-align: center;
  cursor: pointer;
  user-select: none;
}

.toggle-icon:hover {
  color: #1976d2;
}

.section-level-type {
  font-weight: 600;
  color: #555;
  font-size: 0.9rem;
}

.section-name {
  color: #1976d2;
  font-size: 1rem;
}

.section-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.verse-count {
  font-size: 0.85rem;
  color: #999;
  background: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
}

.section-children {
  margin-left: 2rem;
  margin-top: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Responsive design */
@media (max-width: 768px) {
  .section-header {
    padding: 0.6rem 0.75rem;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .section-info {
    width: 100%;
  }

  .section-meta {
    width: 100%;
    justify-content: flex-start;
  }

  .section-children {
    margin-left: 1rem;
  }

  .section-level-type,
  .section-name {
    font-size: 0.9rem;
  }
}
</style>
