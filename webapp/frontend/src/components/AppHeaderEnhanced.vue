<template>
  <div class="header-wrapper">
    <!-- Compact One-Line Header -->
    <header class="app-header">
      <div class="header-container">
        <!-- Logo (Placeholder - can be replaced with actual logo) -->
        <div class="header-logo" @click="goToSearch">
          <span class="logo-icon">📚</span>
          <span class="logo-text"></span>
        </div>

        <!-- Enhanced Search Box -->
        <div class="header-search" ref="searchContainer">
          <div class="search-box" :class="{ focused: searchFocused }">
            <input
              ref="searchInput"
              v-model="searchQuery"
              @focus="handleSearchFocus"
              @blur="handleSearchBlur"
              @keyup.enter="handleSearch"
              @keydown.esc="closeSearchPanel"
              type="search"
              placeholder="இலக்கிய சொல் தேடல்"
              class="search-input"
              autocomplete="off"
            />

            <button
              v-if="searchQuery"
              @click="clearSearchInput"
              class="clear-btn"
              title="Clear"
            >
              ×
            </button>

            <button
              class="search-icon-btn"
              @click="handleSearch"
              :disabled="!searchQuery.trim()"
              title="Search"
            >
              🔍
            </button>
          </div>
        </div>

        <!-- Menu Button -->
        <button
          ref="menuBtn"
          @click="toggleMenu"
          class="menu-btn"
          :class="{ active: menuExpanded }"
          title="Menu"
        >
          ☰
        </button>
      </div>

      <!-- Database Summary Below Search Box -->
      <div class="database-summary">
        <!-- Row 1: Labels -->
        <div class="summary-label label-center">படைப்புகள்</div>
        <div class="summary-label label-center">தகவல்</div>
        <div class="summary-label label-center">சொற்கள்</div>

        <!-- Row 2: Values -->
        <div class="summary-value value-center">
          <span v-if="stats">{{ stats.total_works }}</span>
          <span v-else>-</span>
        </div>
        <div class="summary-value value-center">
          <a href="http://tamilconcordance.in" target="_blank" rel="noopener noreferrer" class="concordance-link">
            http://tamilconcordance.in
          </a>
        </div>
        <div class="summary-value value-center">
          <span v-if="stats">{{ stats.distinct_words }}</span>
          <span v-else>-</span>
        </div>
      </div>
    </header>

    <!-- Full-Screen Search Panel -->
    <Teleport to="body">
      <Transition name="panel-fade">
        <div v-if="searchFocused" class="search-panel-fullscreen">
          <!-- Panel Header with Back Button and Search Box -->
          <div class="panel-header">
            <button @click="closeSearchPanel" class="back-btn" title="Close">
              <span class="back-arrow">←</span>
            </button>

            <div class="panel-search-box">
              <input
                ref="panelSearchInput"
                v-model="searchQuery"
                @keyup.enter="handleSearchAndClose"
                @keydown.esc="closeSearchPanel"
                type="search"
                placeholder="இலக்கிய சொல் தேடல்"
                class="search-input"
                autocomplete="off"
              />

              <button
                v-if="searchQuery"
                @click="clearSearchInput"
                class="clear-btn"
                title="Clear"
              >
                ×
              </button>

              <button
                @click="handleSearchAndClose"
                class="search-icon-btn"
                title="Search"
              >
                🔍
              </button>
            </div>
          </div>

          <!-- Scrollable Panel Content -->
          <div class="panel-content">

            <!-- Match Type & Word Position Options -->
            <section class="search-options-section">
              <div class="options-row">
                <!-- Match Type -->
                <div class="option-group">
                  <span class="option-label">Match:</span>
                  <label class="option-radio">
                    <input type="radio" v-model="matchType" value="partial" />
                    <span>Partial</span>
                  </label>
                  <label class="option-radio">
                    <input type="radio" v-model="matchType" value="exact" />
                    <span>Exact</span>
                  </label>
                </div>

                <!-- Word Position -->
                <div class="option-group" :class="{ 'option-disabled': matchType === 'exact' }">
                  <span class="option-label">Position:</span>
                  <label class="option-radio">
                    <input type="radio" v-model="wordPosition" value="beginning" :disabled="matchType === 'exact'" />
                    <span>Start</span>
                  </label>
                  <label class="option-radio">
                    <input type="radio" v-model="wordPosition" value="end" :disabled="matchType === 'exact'" />
                    <span>End</span>
                  </label>
                  <label class="option-radio">
                    <input type="radio" v-model="wordPosition" value="anywhere" :disabled="matchType === 'exact'" />
                    <span>Any</span>
                  </label>
                </div>
              </div>
            </section>

            <!-- Category Cards (Quick Filters) - MASKED FOR NOW -->
            <!--
            <section v-if="searchQuery.trim()" class="category-section">
              <h3 class="section-title">தொகுப்புகள் (Quick Filters)</h3>
              <div class="category-cards">
                <button
                  v-for="category in quickCategories"
                  :key="category.id"
                  @click="selectCategory(category)"
                  class="category-card"
                >
                  <span class="category-icon">{{ category.icon }}</span>
                  <span class="category-name">{{ category.name }}</span>
                  <span class="category-name-tamil">{{ category.nameTamil }}</span>
                </button>
              </div>
            </section>
            -->

            <!-- Collections Tree with Controls -->
            <section class="collections-section">
              <!-- Control Bar: Select All | Clear | [space] | Done | Chevron -->
              <div class="tree-controls">
                <div class="action-buttons-left">
                  <button @click="selectAllCollections" class="action-btn-inline">
                    Select All
                  </button>
                  <button @click="clearAllCollections" class="action-btn-inline">
                    Clear
                  </button>
                </div>

                <div class="action-buttons-right">
                  <button @click="handleSearchAndClose" class="done-btn-inline">
                    Done
                  </button>
                </div>
              </div>

              <!-- CollectionTree -->
              <Transition name="expand">
                <div v-if="collectionsExpanded" class="section-content">
                  <CollectionTree
                    ref="collectionTreeRef"
                    v-model:selected-works="selectedWorks"
                  />
                </div>
              </Transition>
            </section>

            <!-- Autocomplete Suggestions -->
            <section v-if="searchQuery.trim() && suggestions.length" class="suggestions-section">
              <h3 class="section-title">பரிந்துரைகள் (Suggestions)</h3>
              <ul class="suggestions-list">
                <li
                  v-for="suggestion in suggestions"
                  :key="suggestion.word"
                  @click="selectSuggestion(suggestion.word)"
                  class="suggestion-item"
                >
                  <span class="word-text" v-html="highlightMatch(suggestion.word)"></span>
                  <span class="word-count">{{ suggestion.count }} முறை</span>
                  <span class="arrow-icon">→</span>
                </li>
              </ul>
            </section>


          </div>
        </div>
      </Transition>

      <!-- Mobile Backdrop -->
      <Transition name="backdrop-fade">
        <div
          v-if="searchFocused && isMobile"
          class="search-backdrop"
          @click="closeSearchPanel"
        />
      </Transition>
    </Teleport>

    <!-- Menu Dropdown (Existing) -->
    <div v-if="menuExpanded" class="menu-backdrop" @click="closeMenu"></div>
    <div
      v-if="menuExpanded"
      class="menu-dropdown"
      :style="{ top: menuPosition.top, right: menuPosition.right }"
    >
      <router-link :to="{ name: 'Home' }" class="menu-item" @click="closeMenu">
        Acknowledgment
      </router-link>
      <router-link :to="{ name: 'Search' }" class="menu-item" @click="closeMenu">
        Search
      </router-link>
      <router-link
        v-if="isWorksBrowserVisible"
        :to="{ name: 'WorksList' }"
        class="menu-item"
        @click="closeMenu"
      >
        Browse Works
      </router-link>
      <router-link :to="{ name: 'About' }" class="menu-item" @click="closeMenu">
        About & Help
      </router-link>
      <router-link :to="{ name: 'Journey' }" class="menu-item" @click="closeMenu">
        The Story Behind
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSearchState } from '../composables/useSearchState.js'
import { useFilterState } from '../composables/useFilterState.js'
import { useStats } from '../composables/useStats.js'
import CollectionTree from './CollectionTree.vue'

const router = useRouter()
const route = useRoute()
const searchInput = ref(null)
const panelSearchInput = ref(null)
const searchContainer = ref(null)
const collectionTreeRef = ref(null)
const searchQuery = ref('')
const searchFocused = ref(false)
const collectionsExpanded = ref(true)
const isTreeExpanded = ref(false)
const menuExpanded = ref(false)
const menuBtn = ref(null)
const menuPosition = ref({ top: '58px', right: '1rem' })

// Mock data - replace with real data
const suggestions = ref([])
const quickCategories = ref([
  { id: 'sangam', icon: '🏛️', name: 'Sangam', nameTamil: 'சங்க இலக்கியம்' },
  { id: 'thirukkural', icon: '📖', name: 'Thirukkural', nameTamil: 'திருக்குறள்' },
  { id: 'devotional', icon: '🙏', name: 'Devotional', nameTamil: 'பக்தி இலக்கியம்' },
  { id: 'ethics', icon: '📚', name: 'Ethics', nameTamil: 'நீதிநூல்கள்' },
])
const exampleWords = ref(['அறம்', 'காதல்', 'நீதி', 'இன்பம்'])

const { clearSearch, matchType, wordPosition } = useSearchState()
const { selectedWorks, filterMode } = useFilterState()

const { stats, loadStats } = useStats()

// Load stats once per session
if (!stats.value) {
  loadStats()
}

const isMobile = computed(() => {
  if (typeof window === 'undefined') return false
  return window.innerWidth < 768
})

const isWorksBrowserVisible = computed(() => {
  const hostname = window.location.hostname
  return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '192.168.1.198'
})

// Sync with URL
watch(() => route.query.q, (newQuery) => {
  if (newQuery) {
    searchQuery.value = newQuery
  } else if (route.name !== 'Search') {
    searchQuery.value = ''
  }
})

// Initialize from URL
if (route.query.q) {
  searchQuery.value = route.query.q
}

function handleSearchFocus() {
  searchFocused.value = true
}

function handleSearchBlur(event) {
  // Don't use blur-to-close on mobile (no hover state)
  if (isMobile.value) {
    return
  }

  // Don't close if clicking inside panel (desktop only)
  setTimeout(() => {
    if (!document.querySelector('.search-panel-fullscreen:hover')) {
      searchFocused.value = false
    }
  }, 200)
}

function closeSearchPanel() {
  searchFocused.value = false
  searchInput.value?.blur()
}

function handleSearch() {
  if (searchQuery.value.trim()) {
    closeSearchPanel()
    router.push({
      name: 'Search',
      query: { q: searchQuery.value.trim() }
    })
  }
}

function handleSearchAndClose() {
  // Trigger search with current query and selected works
  if (searchQuery.value.trim()) {
    closeSearchPanel()

    // Set filter mode based on selection
    if (selectedWorks.value.length > 0) {
      filterMode.value = 'select'
    } else {
      filterMode.value = 'all'
    }

    // Force re-search by adding a timestamp to ensure SearchPage triggers performSearch
    router.push({
      name: 'Search',
      query: {
        q: searchQuery.value.trim(),
        t: Date.now() // Timestamp to force re-search
      }
    })
  } else {
    // If no search query, just close the panel
    closeSearchPanel()
  }
}

function clearSearchInput() {
  searchQuery.value = ''
  clearSearch()
  router.push({ name: 'Search' })
}

async function selectCategory(category) {
  console.log('Selected category:', category)

  // Map categories to collection IDs based on the database structure
  const categoryCollectionMap = {
    'sangam': null, // Will need to query works from பதினெண்மேல்கணக்கு collection
    'thirukkural': null, // Part of பதினெண்கீழ்க்கணக்கு
    'devotional': 323, // பக்தி இலக்கியம்
    'ethics': 325 // நீதிநூல்கள்
  }

  const collectionId = categoryCollectionMap[category.id]

  if (collectionId) {
    try {
      // Fetch works from this collection
      const response = await fetch(`http://localhost:8000/collections/${collectionId}/works`)
      const works = await response.json()

      // Update selectedWorks with the work IDs from this collection
      selectedWorks.value = works.map(w => w.work_id)
      console.log(`Selected ${works.length} works from category: ${category.name}`)
    } catch (error) {
      console.error('Error loading category works:', error)
    }
  }

  closeSearchPanel()
}

function selectSuggestion(word) {
  searchQuery.value = word
  handleSearch()
}

function tryExample(word) {
  searchQuery.value = word
  handleSearch()
}

function highlightMatch(text) {
  if (!searchQuery.value) return text
  const regex = new RegExp(`(${escapeRegex(searchQuery.value)})`, 'gi')
  return text.replace(regex, '<strong>$1</strong>')
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function clearAllCollections() {
  selectedWorks.value = []
  // Also clear the internal state of CollectionTree
  if (collectionTreeRef.value) {
    collectionTreeRef.value.clearSelections()
  }
}

function selectAllCollections() {
  // Call the CollectionTree's selectAll method
  if (collectionTreeRef.value) {
    collectionTreeRef.value.selectAll()
  }
}

function toggleExpandCollapse() {
  if (!collectionTreeRef.value) return

  if (isTreeExpanded.value) {
    // Collapse all
    collectionTreeRef.value.collapseAll()
    isTreeExpanded.value = false
  } else {
    // Expand all
    collectionTreeRef.value.expandAll()
    isTreeExpanded.value = true
  }
}

function toggleMenu() {
  menuExpanded.value = !menuExpanded.value

  if (menuExpanded.value && menuBtn.value) {
    // Calculate position: menu dropdown's top-right should align with button's bottom-right
    const rect = menuBtn.value.getBoundingClientRect()
    menuPosition.value = {
      top: `${rect.bottom + window.scrollY}px`,
      right: `${window.innerWidth - rect.right}px`
    }
  }
}

function closeMenu() {
  menuExpanded.value = false
}

function goToSearch() {
  router.push({ name: 'Search' })
}

// Close menu on route change
watch(() => route.path, () => {
  menuExpanded.value = false
})

// Focus panel search input when panel opens
watch(searchFocused, (newValue) => {
  if (newValue) {
    // Use nextTick to ensure the panel is rendered
    setTimeout(() => {
      panelSearchInput.value?.focus()
    }, 100)
  }
})
</script>

<style scoped>
/* Header Wrapper */
.header-wrapper {
  position: sticky;
  top: 0;
  z-index: 100;
  background: white;
}

/* Compact Header */
.app-header {
  background: #1a3a5a;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: .5rem;
}

/* Database Summary (Below Search Box) */
.database-summary {
  display: grid;
  grid-template-columns: auto auto auto;
  grid-template-rows: auto auto;
  align-items: center;
  justify-content: center;
  gap: 0 1rem;
  padding: 0.25rem 0;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.9);
  max-width: 900px;
  margin: 0 auto;
  line-height: 1;
  background: #1a3a5a;
}

/* Labels (Row 1) */
.summary-label {
  font-size: 0.75rem;
  font-weight: 400;
  opacity: 0.8;
  line-height: 1;
  padding: 0;
  margin: 0;
}

.label-left {
  text-align: left;
}

.label-center {
  text-align: center;
}

.label-right {
  text-align: right;
}

/* Values (Row 2) */
.summary-value {
  font-size: 0.85rem;
  font-weight: 600;
  line-height: 1;
  padding: 0;
  margin: 0;
}

.value-left {
  text-align: left;
}

.value-center {
  text-align: center;
}

.value-right {
  text-align: right;
}

.concordance-link {
  color: rgba(255, 255, 255, 0.95);
  text-decoration: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.4);
  font-size: 0.75rem;
  font-weight: 400;
}

.concordance-link:hover {
  color: white;
  border-bottom-color: white;
}

.header-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 2rem;
  max-width: 900px;
  margin: 0 auto;
  height: 50px; /* Compact height */
}

/* Logo */
.header-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.logo-icon {
  font-size: 1.5rem;
}

.logo-text {
  font-size: 1rem;
  white-space: nowrap;
}

/* Enhanced Search Box */
.header-search {
  flex: 1;
  max-width: 600px;
  margin: 0 auto;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  border: 2px solid transparent;
  border-radius: 24px;
  padding: 0.25rem 0.5rem 0.25rem 0.75rem;
  transition: all 150ms ease;
}

.search-box.focused {
  border-color: #60a5fa;
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.2);
}

.search-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  background: none;
  border: none;
  font-size: 1.1rem;
  color: #6b7280;
  cursor: pointer;
  transition: all 150ms ease;
  flex-shrink: 0;
}

.search-icon-btn:hover:not(:disabled) {
  color: #1e40af;
  transform: scale(1.1);
}

.search-icon-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 0.95rem;
  background: transparent;
  color: #111827;
  padding: 0.35rem 0;
  min-width: 0;
}

.search-input::placeholder {
  color: #9ca3af;
}

.search-input::-webkit-search-cancel-button {
  display: none;
}

.clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  background: #f3f4f6;
  border: none;
  border-radius: 50%;
  font-size: 1.3rem;
  color: #6b7280;
  cursor: pointer;
  transition: all 150ms ease;
  flex-shrink: 0;
}

.clear-btn:hover {
  background: #e5e7eb;
  color: #374151;
  transform: scale(1.1);
}

/* Menu Button */
.menu-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  color: white;
  font-size: 1.3rem;
  cursor: pointer;
  transition: all 150ms ease;
  flex-shrink: 0;
}

.menu-btn:hover,
.menu-btn.active {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

/* Full-Screen Search Panel */
.search-panel-fullscreen {
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  bottom: 0;
  width: 100%;
  max-width: 900px;
  background: white;
  z-index: 999;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.15);
}

/* Mobile: Full width */
@media (max-width: 900px) {
  .search-panel-fullscreen {
    left: 0;
    transform: none;
    max-width: none;
    box-shadow: none;
  }
}

/* Panel Header (Back Button + Search Box) */
.panel-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #1a3a5a 0%, #1e3a8a 100%);
  border-bottom: 2px solid #1e3a8a;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 150ms ease;
  flex-shrink: 0;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.back-arrow {
  display: block;
}

.panel-search-box {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: white;
  border: 2px solid transparent;
  border-radius: 20px;
  padding: 0.2rem 0.4rem 0.2rem 0.6rem;
  transition: all 150ms ease;
}

.panel-search-box .search-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  padding: 0;
  background: none;
  border: none;
  font-size: 1rem;
  color: #6b7280;
  cursor: pointer;
  transition: all 150ms ease;
  flex-shrink: 0;
}

.panel-search-box .search-icon-btn:hover {
  color: #1e40af;
  transform: scale(1.1);
}

.panel-search-box .search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 0.9rem;
  background: transparent;
  color: #111827;
  padding: 0.3rem 0;
  min-width: 0;
}

.panel-search-box .search-input::placeholder {
  color: #9ca3af;
}

.panel-search-box .clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  padding: 0;
  background: #f3f4f6;
  border: none;
  border-radius: 50%;
  font-size: 1.2rem;
  color: #6b7280;
  cursor: pointer;
  transition: all 150ms ease;
  flex-shrink: 0;
}

.panel-search-box .clear-btn:hover {
  background: #e5e7eb;
  color: #374151;
  transform: scale(1.1);
}

/* Content Area - No scroll, let sections handle their own scrolling */
.panel-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

/* Tree Controls Bar */
.tree-controls {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: white;
  border-bottom: 2px solid #e5e7eb;
}

.done-btn-inline {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #1a3a5a 0%, #1e3a8a 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms ease;
  box-shadow: 0 2px 4px rgba(30, 64, 175, 0.2);
  white-space: nowrap;
}

.done-btn-inline:hover {
  background: linear-gradient(135deg, #1a3a5a 0%, #1e2a5a 100%);
  box-shadow: 0 4px 8px rgba(30, 64, 175, 0.3);
  transform: translateY(-1px);
}

.done-btn-inline:active {
  transform: translateY(0);
}

.chevron-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  transition: all 150ms ease;
  flex-shrink: 0;
}

.chevron-btn:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

.chevron-btn .chevron {
  font-size: 0.9rem;
  color: #6b7280;
  transition: transform 150ms ease;
}

.chevron-btn .chevron.rotated {
  transform: rotate(-180deg);
}

.action-buttons-left {
  display: flex;
  gap: 0.5rem;
}

.action-buttons-right {
  display: flex;
  gap: 0.5rem;
  margin-left: auto;
}

.action-btn-inline {
  padding: 0.5rem 0.75rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 150ms ease;
  white-space: nowrap;
}

.action-btn-inline:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

/* Section Styling */
.search-options-section {
  flex-shrink: 0;
  border-bottom: 1px solid #e5e7eb;
}

.collections-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-bottom: 1px solid #e5e7eb;
}

.category-section,
.suggestions-section {
  border-bottom: 1px solid #e5e7eb;
}

/* Search Options Section */
.search-options-section {
  padding: 1rem;
  background: #f9fafb;
}

.options-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: center;
}

.option-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.option-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #374151;
  white-space: nowrap;
}

.option-radio {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
  font-size: 0.9rem;
  color: #374151;
  white-space: nowrap;
  transition: color 150ms ease;
}

.option-radio input[type="radio"] {
  cursor: pointer;
  width: 16px;
  height: 16px;
  accent-color: #1e40af;
}

.option-radio:hover {
  color: #1e40af;
}

.option-disabled {
  opacity: 0.5;
  pointer-events: none;
}

.section-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

/* Category Cards */
.category-section {
  padding: 1rem;
  background: #f9fafb;
}

.category-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.category-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.75rem 0.5rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 150ms ease;
  text-align: center;
}

.category-card:hover {
  border-color: #60a5fa;
  background: #eff6ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.category-icon {
  font-size: 1.8rem;
}

.category-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
}

.category-name-tamil {
  font-size: 0.75rem;
  color: #6b7280;
}

/* Collections Section */
.section-content {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
}

.collections-tree-placeholder {
  padding: 1.5rem;
  background: #f9fafb;
  border: 2px dashed #d1d5db;
  border-radius: 6px;
  text-align: center;
}

/* Suggestions List */
.suggestions-section {
  padding: 1rem;
}

.suggestions-list {
  list-style: none;
  padding: 0;
  margin: 0.75rem 0 0 0;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  cursor: pointer;
  transition: background 150ms ease;
  border-radius: 6px;
}

.suggestion-item:hover {
  background: #f9fafb;
}

.word-text {
  flex: 1;
  font-size: 1rem;
  color: #111827;
}

.word-text :deep(strong) {
  font-weight: 700;
  color: #1e40af;
}

.word-count {
  font-size: 0.85rem;
  color: #6b7280;
  white-space: nowrap;
}

.arrow-icon {
  color: #9ca3af;
  font-size: 1rem;
}

/* Empty State */
.empty-state {
  padding: 2rem 1rem;
  text-align: center;
}

.empty-message {
  font-size: 0.95rem;
  color: #6b7280;
  margin: 0 0 1.5rem 0;
}

.example-words {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.example-label {
  font-size: 0.9rem;
  color: #9ca3af;
  font-weight: 500;
}

.example-word-btn {
  padding: 0.4rem 0.8rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  color: #1e40af;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 150ms ease;
}

.example-word-btn:hover {
  background: #dbeafe;
  border-color: #60a5fa;
  transform: translateY(-1px);
}

/* Backdrop */
.search-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 998;
}

/* Menu Dropdown (Existing) */
.menu-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: transparent;
  z-index: 999;
}

.menu-dropdown {
  position: fixed;
  /* top and right set dynamically via :style */
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  z-index: 1000;
  animation: slideDown 0.2s ease-out;
}

.menu-item {
  display: block;
  padding: 0.75rem 1rem;
  color: #374151;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background 150ms ease;
  border-bottom: 1px solid #f3f4f6;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:hover {
  background: #f9fafb;
}

.menu-item.router-link-active {
  background: #eff6ff;
  color: #1e40af;
  font-weight: 600;
}

/* Animations */
.panel-fade-enter-active,
.panel-fade-leave-active {
  transition: opacity 200ms ease, transform 200ms ease;
}

.panel-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.panel-fade-leave-to {
  opacity: 0;
}

.backdrop-fade-enter-active,
.backdrop-fade-leave-active {
  transition: opacity 200ms ease;
}

.backdrop-fade-enter-from,
.backdrop-fade-leave-to {
  opacity: 0;
}

.expand-enter-active,
.expand-leave-active {
  transition: all 200ms ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 800px;
  opacity: 1;
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

/* Mobile Adjustments */
@media (max-width: 767px) {
  .header-container {
    padding: .4rem 0.5rem;
    gap: 0.5rem;
    height: 44px; /* Even more compact on mobile */
  }

  .logo-text {
    display: none; /* Hide text, show icon only on mobile */
  }

  .logo-icon {
    font-size: 1.3rem;
  }

  .search-box {
    padding: 0.2rem 0.4rem 0.2rem 0.6rem;
  }

  .search-input {
    font-size: 16px; /* Prevent iOS zoom */
  }

  .menu-btn {
    width: 36px;
    height: 36px;
    font-size: 1.2rem;
  }

  /* Database Summary on Mobile - Keep same layout, just adjust sizing */
  .database-summary {
    padding: 0.25rem 0;
    gap: 0 0.75rem;
    font-size: 0.75rem;
  }

  .summary-label {
    font-size: 0.7rem;
  }

  .summary-value {
    font-size: 0.8rem;
  }

  .concordance-link {
    font-size: 0.7rem;
  }

  /* Panel Header on Mobile */
  .panel-header {
    padding: 0.5rem;
    gap: 0.5rem;
  }

  .back-btn {
    width: 36px;
    height: 36px;
  }

  .panel-search-box {
    padding: 0.2rem 0.4rem 0.2rem 0.6rem;
  }

  .panel-search-box .search-input {
    font-size: 16px; /* Prevent iOS zoom */
  }

  .category-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem;
  }

  .category-card {
    padding: 0.6rem 0.4rem;
  }

  .category-icon {
    font-size: 1.5rem;
  }

  .suggestion-item {
    padding: 0.85rem 0.75rem;
    min-height: 48px; /* Touch-friendly */
  }

  /* Search Options on Mobile */
  .search-options-section {
    padding: 0.75rem;
  }

  .options-row {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .option-group {
    gap: 0.5rem;
  }

  .option-radio {
    font-size: 0.85rem;
    min-height: 44px; /* Touch-friendly */
    padding: 0.25rem 0;
  }

  .option-radio input[type="radio"] {
    width: 18px;
    height: 18px;
  }
}
</style>
