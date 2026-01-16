<template>
  <div class="header-wrapper" key="header-root">
    <header class="app-header">
      <div class="header-content">
        <!-- Top Row: Title (hidden on mobile) - Renders once, never updates -->
        <div class="header-top-row">
          <div class="header-titles">
            <h1 class="desktop-only">தமிழ் இலக்கிய சொல் தேடல்</h1>
            <h3 class="desktop-only">Search Words in Thamizh Literature</h3>
          </div>
        </div>

        <!-- Database Summary - Only re-renders if stats change -->
        <div class="database-summary">
          <span v-if="stats">{{ stats.total_works }} தமிழ் இலக்கிய நூல்கள் | {{ stats.distinct_words.toLocaleString() }} சொற்கள்</span>
          <span v-else>Loading statistics...</span>
          <span class="data-source-note">Data Source: <a href="http://tamilconcordance.in" target="_blank" rel="noopener noreferrer" class="concordance-link">http://tamilconcordance.in</a></span>
        </div>

        <!-- Compact Search Box with External Icons -->
        <div class="header-search">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search for a word... (e.g., அறம்)"
            @keyup.enter="handleSearch"
            class="search-input"
          />
          <button @click="handleSearch" class="search-icon-button" :disabled="!searchQuery.trim()" title="Search">
            🔍
          </button>
          <button
            @click="clearSearchInput"
            class="clear-icon-button"
            :disabled="!searchQuery.trim()"
            title="Clear search"
          >
            ✕
          </button>
        </div>

      </div>

      <!-- Bottom Row: Navigation Tabs (Three Column Layout) -->
      <div class="header-bottom-row">
        <nav class="header-nav-tabs">
          <!-- Column 1: Current Tab Name -->
          <div class="current-tab-name">
            {{ currentTabName }}
          </div>

          <!-- Column 2: Blank Space -->
          <div class="tab-spacer"></div>

          <!-- Column 3: Menu Toggle -->
          <div class="menu-toggle-wrapper">
            <button @click="toggleMenu" class="menu-toggle" :class="{ active: menuExpanded }">
              ☰
            </button>
          </div>
        </nav>

      </div>
    </header>

    <!-- Backdrop (click to close menu) -->
    <div v-if="menuExpanded" class="menu-backdrop" @click="closeMenu"></div>

    <!-- Dropdown Menu (outside header, shown when menu is expanded) -->
    <div v-if="menuExpanded" class="tab-menu-dropdown">
      <router-link :to="{ name: 'Home' }" class="menu-item" @click="closeMenu">Acknowledgment</router-link>
      <router-link :to="{ name: 'Search' }" class="menu-item" @click="closeMenu">Search</router-link>
      <router-link v-if="isWorksBrowserVisible" :to="{ name: 'WorksList' }" class="menu-item" @click="closeMenu">Browse Works</router-link>
      <router-link :to="{ name: 'About' }" class="menu-item" @click="closeMenu">About & Help</router-link>
      <router-link :to="{ name: 'Journey' }" class="menu-item" @click="closeMenu">The Story Behind</router-link>
    </div>

    <!-- Filter Options Toggle (only shown on Search page, in content area) -->
    <div v-if="isSearchPage" class="filter-toggle-wrapper">
      <button
        @click="toggleFilterOptions"
        class="filter-toggle-button"
      >
        <span>Search Options</span>
        <span class="toggle-icon">{{ filterOptionsExpanded ? '▼' : '▲' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, shallowRef, defineOptions } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSearchState } from '../composables/useSearchState.js'
import { useStats } from '../composables/useStats.js'

// Prevent component from re-creating
defineOptions({
  name: 'AppHeader',
  inheritAttrs: false
})

const router = useRouter()
const route = useRoute()
const searchQuery = ref('')
const filterOptionsExpanded = ref(false)
const menuExpanded = ref(false)

// Get clearSearch method from composable
const { clearSearch } = useSearchState()

// Get stats from composable (persistent across navigation)
const { stats, loadStats } = useStats()

// Load stats only once - check if already loaded
if (!stats.value) {
  loadStats()
}

// Check if Works Browser should be visible (only for localhost or 192.168.1.198)
// This is static, computed once
const isWorksBrowserVisible = computed(() => {
  const hostname = window.location.hostname
  return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '192.168.1.198'
})

// Use shallow refs for values that change with route to minimize reactivity
const isSearchPage = shallowRef(route.name === 'Search' || route.name === 'SearchResults')
const currentTabName = shallowRef('Search')

// Update these values only when route changes (manual control)
const updateRouteState = () => {
  isSearchPage.value = route.name === 'Search' || route.name === 'SearchResults'

  const tabNames = {
    'Home': 'Acknowledgment',
    'Search': 'Search',
    'SearchResults': 'Search',
    'WorksList': 'Browse Works',
    'WorkDetail': 'Browse Works',
    'SectionView': 'Browse Works',
    'VerseView': 'Browse Works',
    'About': 'About & Help',
    'Journey': 'The Story Behind'
  }
  currentTabName.value = tabNames[route.name] || 'Search'
}

// Initialize on mount
updateRouteState()

// Watch route name changes and update state
watch(() => route.name, () => {
  updateRouteState()
})

// Sync search box with URL query param (only watch, don't trigger on mount)
watch(() => route.query.q, (newQuery) => {
  if (newQuery) {
    searchQuery.value = newQuery
  } else if (route.name !== 'Search') {
    // Clear search box when navigating away from Search page
    searchQuery.value = ''
  }
})

// Initialize search box from URL on mount
if (route.query.q) {
  searchQuery.value = route.query.q
}

function handleSearch() {
  if (searchQuery.value.trim()) {
    const newSearchTerm = searchQuery.value.trim()
    const currentSearchTerm = route.query.q

    // Only clear search results if the search term has changed
    if (newSearchTerm !== currentSearchTerm) {
      clearSearch()
    }

    // Close filter options when search is clicked
    filterOptionsExpanded.value = false
    window.dispatchEvent(new CustomEvent('toggle-filter-options', {
      detail: { expanded: false }
    }))

    router.push({
      name: 'Search',
      query: { q: newSearchTerm }
    })
  }
}

function clearSearchInput() {
  searchQuery.value = ''
  // Optionally clear search results and navigate to search page
  clearSearch()
  router.push({ name: 'Search' })
}

function toggleFilterOptions() {
  filterOptionsExpanded.value = !filterOptionsExpanded.value

  // Scroll to top when expanding filter options
  if (filterOptionsExpanded.value) {
    // Target the .app-content scrollable container
    const appContent = document.querySelector('.app-content')
    if (appContent) {
      appContent.scrollTo({
        top: 0,
        behavior: 'smooth'
      })
    }
  }

  // Emit event to SearchControls to control visibility
  window.dispatchEvent(new CustomEvent('toggle-filter-options', {
    detail: { expanded: filterOptionsExpanded.value }
  }))
}

function toggleMenu() {
  menuExpanded.value = !menuExpanded.value
}

function closeMenu() {
  menuExpanded.value = false
}

// Close menu and update route state when route changes
watch(() => route.path, () => {
  menuExpanded.value = false
  updateRouteState()
})
</script>

<style scoped>
.header-wrapper {
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 100;
  background: white;
  overflow: visible; /* Allow dropdown menu to extend beyond */
}

.app-header {
  background: #1a3a5a; /* linear-gradient(135deg, #4a5f8c 0%, #2d4168 100%); */
  border-bottom: 3px solid #1a2942;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
  margin: 0;
  overflow: visible; /* Allow dropdown menu to extend beyond */
}

.header-content {
  padding: 0.5rem 2rem 0 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.header-top-row {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0;
  padding: 0;
}

.header-titles {
  text-align: center;
}

.desktop-only {
  display: block;
}

.app-header h1 {
  margin: 0;
  font-size: 1.2rem;
  color: white;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.app-header h3 {
  margin: 0.3rem 0 0 0;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 400;
}

.header-search {
  display: flex;
  gap: 0.5rem;
  max-width: 500px;
  margin: 0.5rem auto 0 auto;
  position: relative;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 0.6rem 1rem;
  font-size: 0.95rem;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #4a90e2;
}

.search-icon-button,
.clear-icon-button {
  background: transparent;
  border: 2px solid rgba(255, 255, 255, 0.6);
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  border-radius: 6px;
  min-width: 44px;
  height: 44px;
}

.search-icon-button:hover:not(:disabled) {
  background: transparent;
  border-color: white;
  color: white;
  transform: scale(1.05);
}

.search-icon-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.clear-icon-button {
  font-size: 1.4rem;
}

.clear-icon-button:hover:not(:disabled) {
  background: transparent;
  border-color: #ff6b6b;
  color: #ff6b6b;
  transform: scale(1.05);
}

.clear-icon-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.database-summary {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0rem;
  font-size: 0.9rem;
  font-weight: 400;
  margin: 0.25rem 0;
  background: #1a3a5a;
}

.database-summary span {
  display: block;
}

.data-source-note {
  font-size: 0.75rem;
  font-weight: 500;
}

.concordance-link {
  color: rgba(255, 255, 255, 0.95);
  text-decoration: none;
  font-weight: 500;
  border-bottom: 1px solid rgba(255, 255, 255, 0.4);
}

.concordance-link:hover {
  color: white;
  border-bottom-color: white;
}

/* Navigation Tabs - Three Column Layout */
.header-bottom-row {
  position: relative;
  padding: 0;
  margin: 0;
  overflow: visible; /* Allow dropdown menu to extend beyond */
}

.header-nav-tabs {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding: 0.5rem 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.current-tab-name {
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-bottom: 3px solid white;
  justify-self: start;
  white-space: nowrap;
}

.tab-spacer {
  /* Empty middle column for spacing */
}

.menu-toggle-wrapper {
  justify-self: end;
}

.menu-toggle {
  background: transparent;
  border: 2px solid rgba(255, 255, 255, 0.6);
  border-radius: 4px;
  color: white;
  font-size: 1.3rem;
  cursor: pointer;
  padding: 0.3rem 0.6rem;
  transition: all 0.2s;
  min-width: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-toggle:hover,
.menu-toggle.active {
  background: rgba(255, 255, 255, 0.1);
  border-color: white;
}

/* Menu Backdrop */
.menu-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: transparent;
  z-index: 999; /* Below dropdown but above everything else */
}

/* Dropdown Menu */
.tab-menu-dropdown {
  position: fixed; /* Fixed positioning relative to viewport */
  top: auto; /* Will be positioned below the header */
  right: 2rem;
  background: white;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  z-index: 1000; /* Very high z-index to appear above everything */
  animation: slideDown 0.2s ease-out;
  margin-top: 0; /* Sits right below the header */
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
  padding: 0.75rem 1rem;
  color: #2c3e50;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background-color 0.2s;
  border-bottom: 1px solid #dee2e6;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:hover {
  background-color: #f8f9fa;
}

.menu-item.router-link-active {
  background-color: #e7f3ff;
  color: #4a90e2;
  font-weight: 600;
}

/* Filter Toggle Wrapper (in content area) */
.filter-toggle-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 0 2rem;
  max-width: 1400px;
  margin: 0 auto;
  background: white;
}

.filter-toggle-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  border: 2px solid #4a90e2;
  border-top: none;
  border-radius: 0 0 6px 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  color: #4a90e2;
  transition: all 0.2s;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.filter-toggle-button:hover {
  background: #f8f9fa;
  color: #357abd;
  border-color: #357abd;
}

.toggle-icon {
  font-size: 0.7rem;
  font-weight: 700;
}

/* Mobile Styles */
@media (max-width: 768px) {
  /* Hide titles on mobile */
  .desktop-only {
    display: none !important;
  }

  .header-content {
    padding: 0.5rem 1rem 0 1rem;
  }

  .filter-toggle-wrapper {
    padding: 0 1rem;
  }

  .header-top-row {
    display: none; /* Completely hide the title row on mobile */
  }

  .database-summary {
    font-size: 0.1rem;
    margin: 0.5rem 0;
  }

  .data-source-note {
    font-size: 0.65rem;
  }

  .header-search {
    margin-top: 0.5rem;
    gap: 0.25rem;
  }

  .search-input {
    padding: 0.5rem 0.8rem;
    font-size: 0.9rem;
  }

  .search-icon-button,
  .clear-icon-button {
    padding: 0.4rem 0.6rem;
    font-size: 1.1rem;
    min-width: 40px;
    height: 40px;
  }

  .header-nav-tabs {
    padding: 0.5rem 1rem;
  }

  .current-tab-name {
    font-size: 0.85rem;
  }

  .menu-toggle {
    font-size: 1.2rem;
    padding: 0.25rem 0.5rem;
    min-width: 40px;
    min-height: 40px;
  }

  .tab-menu-dropdown {
    right: 1rem;
    left: auto;
    max-width: calc(100vw - 2rem); /* Prevent overflow on mobile */
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 0.5rem 0.75rem 0 0.75rem;
  }

  .filter-toggle-wrapper {
    padding: 0 0.75rem;
  }

  .header-search {
    gap: 0.25rem;
  }

  .search-input {
    font-size: 0.85rem;
    padding: 0.5rem 0.7rem;
  }

  .search-icon-button,
  .clear-icon-button {
    font-size: 1rem;
    padding: 0.35rem 0.5rem;
    min-width: 36px;
    height: 36px;
  }

  .database-summary {
    font-size: 0.75rem;
  }

  .data-source-note {
    font-size: 0.75rem;
  }

  .header-nav-tabs {
    padding: 0.5rem 0.75rem;
  }

  .tab-menu-dropdown {
    right: 0.75rem;
    left: auto;
    max-width: calc(100vw - 1.5rem); /* Prevent overflow on small mobile */
  }
}
</style>
