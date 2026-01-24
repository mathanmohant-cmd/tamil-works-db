<template>
  <nav class="app-navigation">
    <!-- Menu Button -->
    <button
      @click="menuOpen = !menuOpen"
      @blur="handleBlur"
      class="menu-button"
      aria-label="Navigation menu"
    >
      <span class="menu-icon">☰</span>
      <span class="menu-text">Menu</span>
    </button>

    <!-- Dropdown Menu -->
    <div v-if="menuOpen" class="menu-dropdown">
      <template v-for="item in menuItems" :key="item.name">
        <!-- Main menu item -->
        <router-link
          v-if="!item.submenu"
          :to="item.route"
          class="menu-item"
          @click="menuOpen = false"
        >
          {{ item.label }}
        </router-link>

        <!-- Menu item with collapsible submenu -->
        <div v-else class="menu-item-group">
          <div
            class="menu-group-label"
            @click="toggleSubmenu(item.name)"
            :class="{ expanded: expandedSubmenus[item.name] }"
          >
            <span>{{ item.label }}</span>
            <span class="submenu-arrow">{{ expandedSubmenus[item.name] ? '▼' : '▶' }}</span>
          </div>
          <div v-if="expandedSubmenus[item.name]" class="submenu-items">
            <router-link
              v-for="subitem in item.submenu"
              :key="subitem.name"
              :to="subitem.route"
              class="menu-subitem"
              @click="menuOpen = false"
            >
              {{ subitem.label }}
            </router-link>
          </div>
        </div>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { useUserRole } from '../composables/useUserRole.js'

const menuOpen = ref(false)
const expandedSubmenus = reactive({})
const { canBrowseWorks } = useUserRole()

// Watch menuOpen and collapse all submenus when menu closes or opens
watch(menuOpen, (isOpen) => {
  if (isOpen) {
    // Collapse all submenus when menu opens
    Object.keys(expandedSubmenus).forEach(key => {
      expandedSubmenus[key] = false
    })
  }
})

const menuItems = computed(() => {
  const items = [
    {
      name: 'Home',
      label: 'Acknowledgment',
      route: { name: 'Home' }
    },
    {
      name: 'Search',
      label: 'Search',
      route: { name: 'Search' }
    },
    {
      name: 'About',
      label: 'About & Help',
      submenu: [
        {
          name: 'AboutUnderstanding',
          label: 'Understanding this tool',
          route: { name: 'About', query: { tab: 'qa' } }
        },
        {
          name: 'AboutPrinciples',
          label: 'Word Segmentation',
          route: { name: 'About', query: { tab: 'principles' } }
        }
      ]
    },
    {
      name: 'Journey',
      label: 'The Story Behind',
      route: { name: 'Journey' }
    }
  ]

  // Insert Works Browser after Search if user has browse works permission
  if (canBrowseWorks.value) {
    items.splice(2, 0, {
      name: 'Works',
      label: 'Browse Works',
      route: { name: 'WorksList' }
    })
  }

  return items
})

function toggleSubmenu(name) {
  expandedSubmenus[name] = !expandedSubmenus[name]
}

function handleBlur(event) {
  // Delay closing to allow click events on menu items
  setTimeout(() => {
    if (!event.currentTarget.contains(document.activeElement)) {
      menuOpen.value = false
    }
  }, 200)
}
</script>

<style scoped>
.app-navigation {
  position: relative;
  flex-shrink: 0;
}

.menu-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 1.0rem;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(74, 144, 226, 0.5);
  border-radius: 4px;
  color: #4a90e2;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.menu-button:hover {
  background: #4a90e2;
  color: white;
}

.menu-icon {
  font-size: 1.2rem;
  line-height: 1;
}

.menu-text {
  font-weight: 600;
}

.menu-dropdown {
  position: fixed;
  top: 5rem;
  right: 2rem;
  background: white;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  min-width: 220px;
  max-width: 280px;
  max-height: calc(100vh - 6rem);
  overflow-y: auto;
  z-index: 1000;
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

.menu-item {
  display: block;
  padding: 0.8rem 1.2rem;
  text-decoration: none;
  color: #495057;
  transition: background-color 0.2s;
  font-size: 0.95rem;
  border-bottom: 1px solid #f1f3f5;
  font-weight: 500;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:hover {
  background-color: #f8f9fa;
  color: #212529;
}

.menu-item.router-link-active {
  background-color: #e7f3ff;
  color: #4a90e2;
  font-weight: 600;
  border-left: 4px solid #4a90e2;
  padding-left: calc(1.2rem - 4px);
}

.menu-item-group {
  border-bottom: 1px solid #dee2e6;
}

.menu-item-group:last-child {
  border-bottom: none;
}

.menu-group-label {
  padding: 0.8rem 1.2rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: #495057;
  background: #f8f9fa;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none;
}

.menu-group-label:hover {
  background: #e9ecef;
}

.menu-group-label.expanded {
  background: #e9ecef;
}

.submenu-arrow {
  font-size: 0.7rem;
  color: #6c757d;
  transition: transform 0.2s;
}

.submenu-items {
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 200px;
  }
}

.menu-subitem {
  display: block;
  padding: 0.7rem 1.2rem 0.7rem 2rem;
  text-decoration: none;
  color: #495057;
  transition: background-color 0.2s;
  font-size: 0.9rem;
  border-bottom: 1px solid #f8f9fa;
}

.menu-subitem:last-child {
  border-bottom: none;
}

.menu-subitem:hover {
  background-color: #f1f3f5;
  color: #212529;
}

.menu-subitem.router-link-active {
  background-color: #e7f3ff;
  color: #4a90e2;
  font-weight: 600;
}

@media (max-width: 768px) {
  .menu-button {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }

  .menu-dropdown {
    min-width: 200px;
    right: 1rem;
    top: 4rem;
  }

  .menu-item {
    padding: 0.7rem 1rem;
    font-size: 0.9rem;
  }

  .menu-subitem {
    padding: 0.6rem 1rem 0.6rem 1.5rem;
    font-size: 0.85rem;
  }
}
</style>
