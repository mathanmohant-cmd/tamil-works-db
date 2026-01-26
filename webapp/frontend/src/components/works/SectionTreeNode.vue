<template>
  <div class="section-node">
    <div
      class="section-header"
      :class="{
        'clickable-leaf': isLeafSection,
        'clickable-container': isContainerSection
      }"
      @click="handleSectionClick"
    >
      <div class="section-info">
        <span class="section-icon">
          {{ isLeafSection ? '📄' : '📁' }}
        </span>
        <!-- Hide generic section names for single-section works -->
        <template v-if="!isGenericSingleSection">
          <span class="section-level-type">
            {{ section.level_type_tamil || section.level_type }}
            {{ section.section_number }}:
          </span>
          <span class="section-name">
            {{ section.section_name_tamil || section.section_name }}
          </span>
        </template>
        <template v-else>
          <span class="section-name">
            {{ section.verse_count === 1 ? 'பாடல்' : 'தொகுப்பு' }}
          </span>
        </template>
      </div>
      <div class="section-actions">
        <span
          class="verse-count"
          v-if="section.verse_count > 0"
          @click.stop="navigateToSection"
        >
          {{ section.verse_count }} {{ section.verse_count === 1 ? 'பாடல்' : 'பாடல்கள்' }} →
        </span>
        <button
          v-if="section.children && section.children.length > 0"
          @click.stop="toggleExpanded"
          class="expand-collapse-button"
          :title="isExpanded ? 'Collapse' : 'Expand'"
        >
          <span class="expand-icon">
            <span
              class="chevron-icon"
              :class="isExpanded ? 'chevron-up' : 'chevron-down'"
            ></span>
          </span>
        </button>
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
import { ref, computed } from 'vue'
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

// Detect if section is a leaf (has verses, no/few children)
const isLeafSection = computed(() => {
  const hasVerses = props.section.verse_count > 0
  const hasChildren = props.section.children && props.section.children.length > 0
  return hasVerses && !hasChildren
})

// Detect if section is a container (has children)
const isContainerSection = computed(() => {
  return props.section.children && props.section.children.length > 0
})

// Detect if this is a generic single section that should be hidden
// For works with only one section with generic names like "Main", "முக்கிய தொகுப்பு", etc.
const isGenericSingleSection = computed(() => {
  // List of generic section names to hide
  const genericNames = [
    'Main',
    'Main Collection',
    'முக்கிய தொகுப்பு',
    'தொகுப்பு 1',
    'Collection 1',
    ''  // Empty string for sections with no name
  ]

  const sectionName = props.section.section_name_tamil || props.section.section_name || ''

  // Check if it's a generic name or empty, and has no parent (top-level section)
  const isGeneric = genericNames.includes(sectionName)
  const isTopLevel = !props.section.parent_section_id

  return isGeneric && isTopLevel
})

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

// Smart click handler - adapts behavior based on section type
const handleSectionClick = () => {
  if (isLeafSection.value) {
    // Leaf section with verses - navigate to SectionView
    navigateToSection()
  } else if (isContainerSection.value) {
    // Container section with children - expand accordion
    toggleExpanded()
  }
  // Empty section (no verses, no children) - do nothing
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
  transition: all 0.2s ease;
}

.section-header.clickable-leaf {
  cursor: pointer;
}

.section-header.clickable-leaf:hover {
  background: #e3f2fd;
  border-color: #1976d2;
}

.section-header.clickable-container {
  cursor: pointer;
}

.section-header.clickable-container:hover {
  background: #f0f0f0;
  border-color: #d0d0d0;
}

.section-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.section-icon {
  font-size: 1.1rem;
  margin-right: 0.25rem;
  flex-shrink: 0;
}

.section-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Expand/Collapse Button - Match CollectionTree */
.expand-collapse-button {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.expand-collapse-button:hover {
  transform: scale(1.1);
}

.expand-icon {
  font-size: 1.2rem;
  color: #4a90e2;
  display: flex;
  align-items: center;
}

/* Rotated Box Chevron - Match SearchResults */
.chevron-icon {
  display: inline-block;
  width: 10px;
  height: 10px;
  border: none;
  border-right: 2px solid currentColor;
  border-bottom: 2px solid currentColor;
  color: var(--primary-color);
  transition: transform 0.2s ease;
}

.chevron-up {
  transform: rotate(-135deg); /* Expanded state - points UP ▲ */
}

.chevron-down {
  transform: rotate(45deg); /* Collapsed state - points DOWN ▼ */
}

.section-level-type {
  font-weight: 600;
  color: #555;
  font-size: 0.9rem;
}

.section-name {
  color: #1976d2;
  font-size: 1rem;
  font-weight: 500;
}

.verse-count {
  font-size: 0.85rem;
  color: #1976d2;
  background: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 600;
}

.verse-count:hover {
  background: #e3f2fd;
  border-color: #1976d2;
  transform: scale(1.05);
  color: #1565c0;
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
  }

  .section-actions {
    gap: 0.75rem;
  }

  .section-children {
    margin-left: 1rem;
  }

  .section-level-type,
  .section-name {
    font-size: 0.9rem;
  }

  .verse-count {
    font-size: 0.8rem;
    padding: 0.2rem 0.6rem;
  }
}
</style>
