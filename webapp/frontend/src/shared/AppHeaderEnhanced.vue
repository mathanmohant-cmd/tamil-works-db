<template>
  <div class="header-wrapper">
    <!-- Compact One-Line Header -->
    <header class="app-header">
      <div class="header-container">
        <!-- Logo -->
        <div class="header-logo" @click="goToHome">
          <!--<img src="/project_icon.png" alt="Tamil Literature Search" class="logo-icon-img" />-->
          <span class="logo-icon">📚</span>
          <span class="logo-text"></span>
        </div>

        <!-- Enhanced Search Box -->
        <div class="header-search" ref="searchContainer">
          <div class="search-box" :class="{ focused: searchFocused }">
            <input
              ref="searchInput"
              v-model="englishInput"
              @focus="handleSearchFocus"
              @blur="handleSearchBlur"
              @keyup.enter="handleSearch"
              @keydown.esc="closeSearchPanel"
              type="search"
              :placeholder="transliterationEnabled ? 'Type in English... (e.g., aram)' : 'இலக்கிய சொல் தேடல்'"
              class="search-input"
              autocomplete="off"
            />

            <div v-if="transliterationEnabled && searchQuery" class="tamil-preview">
              {{ searchQuery }}
            </div>

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

          <button
            @click="toggleTransliteration"
            class="transliteration-toggle-btn"
            :class="{ active: transliterationEnabled }"
            :title="transliterationEnabled ? 'Transliteration ON (A→அ)' : 'Transliteration OFF'"
          >
            <span class="transliteration-icon">
              <span class="en-letter">A</span>
              <span class="arrow">→</span>
              <span class="ta-letter">அ</span>
            </span>
          </button>
        </div>

        <!-- Menu Button (Mobile Only) -->
        <button
          ref="menuBtn"
          @click="toggleMenu"
          class="menu-btn mobile-only"
          :class="{ active: menuExpanded }"
          title="Menu"
        >
          ☰
        </button>
      </div>

      <!-- Horizontal Navigation Tabs (Desktop Only) -->
      <nav class="desktop-nav-tabs">
        <router-link :to="{ name: 'Home' }" class="nav-tab">Home</router-link>
        <router-link v-if="isWorksBrowserVisible" :to="{ name: 'WorksList' }" class="nav-tab">Browse Works</router-link>
        <router-link :to="{ name: 'Acknowledgment' }" class="nav-tab">Acknowledgment</router-link>

        <!-- Help and Docs Dropdown -->
        <div class="profile-tab-dropdown" ref="helpDropdown">
          <button
            @click="toggleHelpMenu"
            @blur="handleHelpBlur"
            class="nav-tab profile-tab-button"
            :class="{ 'profile-active': helpMenuOpen }"
            title="Help and Docs"
          >
            <span>Help and Docs</span>
            <span class="dropdown-arrow">▼</span>
          </button>

          <!-- Help Dropdown Menu -->
          <div v-if="helpMenuOpen" class="profile-tab-menu">
            <router-link :to="{ name: 'QuickStart' }" @click="helpMenuOpen = false" class="profile-menu-item">
              <span class="menu-item-icon">📖</span>
              <span>Quick Start</span>
            </router-link>
            <router-link :to="{ name: 'UnderstandingThisTool' }" @click="helpMenuOpen = false" class="profile-menu-item">
              <span class="menu-item-icon">💡</span>
              <span>Understanding This Tool</span>
            </router-link>
            <router-link :to="{ name: 'WordSegmentation' }" @click="helpMenuOpen = false" class="profile-menu-item">
              <span class="menu-item-icon">&#x1F4DD;</span>
              <span>Word Segmentation</span>
            </router-link>
            <router-link :to="{ name: 'TransliterationGuide' }" @click="helpMenuOpen = false" class="profile-menu-item">
              <span class="menu-item-icon">🔤</span>
              <span>Transliteration Guide</span>
            </router-link>
          </div>
        </div>

        <!-- The Story Behind Dropdown -->
        <div class="profile-tab-dropdown" ref="storyDropdown">
          <button
            @click="toggleStoryMenu"
            @blur="handleStoryBlur"
            class="nav-tab profile-tab-button"
            :class="{ 'profile-active': storyMenuOpen }"
            title="The Story Behind"
          >
            <span>The Story Behind</span>
            <span class="dropdown-arrow">▼</span>
          </button>

          <!-- Story Dropdown Menu -->
          <div v-if="storyMenuOpen" class="profile-tab-menu">
            <router-link :to="{ name: 'Journey' }" @click="storyMenuOpen = false" class="profile-menu-item">
              <span class="menu-item-icon">🚀</span>
              <span>The Journey</span>
            </router-link>
            <router-link :to="{ name: 'Inspiration' }" @click="storyMenuOpen = false" class="profile-menu-item">
              <span class="menu-item-icon">✨</span>
              <span>Guiding Exemplars</span>
            </router-link>
          </div>
        </div>

        <!-- Login Button (Guest) or Profile Dropdown (Admin) -->
        <div v-if="isGuest" class="profile-tab-dropdown">
          <button
            @click="showLoginModal = true"
            class="nav-tab"
            title="Login"
          >
            <span>Login</span>
          </button>
        </div>
        <div v-else class="profile-tab-dropdown" ref="profileDropdown">
          <button
            @click="toggleProfileMenu"
            @blur="handleProfileBlur"
            class="nav-tab profile-tab-button"
            :class="{ 'profile-active': profileMenuOpen }"
            title="My Profile"
          >
            <span class="profile-icon">👤</span>
            <span class="profile-name">{{ currentUser }}</span>
            <span class="dropdown-arrow">▼</span>
          </button>

          <!-- Profile Dropdown Menu -->
          <div v-if="profileMenuOpen" class="profile-tab-menu">
            <div class="profile-menu-header">
              <div class="profile-user-info">
                <div class="profile-username">{{ currentUser }}</div>
                <div class="profile-role">Administrator</div>
              </div>
            </div>
            <div class="profile-menu-divider"></div>
            <router-link v-if="currentUser === 'admin'" :to="{ name: 'Admin' }" @click="profileMenuOpen = false" class="profile-menu-item">
              <span class="menu-item-icon">⚙️</span>
              <span>Admin</span>
            </router-link>
            <button @click="handleLogout" class="profile-menu-item logout-item">
              <span class="menu-item-icon">🚪</span>
              <span>Logout</span>
            </button>
          </div>
        </div>
      </nav>

      <!-- Database Summary Below Search Box (Hidden) -->
      <!--
      <div class="database-summary">
        <div class="summary-value label-left">
        </div>
        <div class="summary-value label-center">
          <span v-if="stats">{{ stats.total_works }}</span>
          <span v-else>-</span> தமிழ் இலக்கிய படைப்புகள்
        </div>
        <div class="summary-value label-right">
        </div>
      </div>
      <div class="database-summary">
        <div class="summary-value value-left">
          <span v-if="stats">{{ stats.total_verses }} செய்யுள்கள்</span>
          <span v-else>-</span>
        </div>
        <div class="summary-label label-center">
        </div>
        <div class="summary-value value-right">
          <span v-if="stats">{{ stats.distinct_words }} சொற்கள்</span>
          <span v-else>-</span>
        </div>
      </div>
      -->
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
                v-model="englishInput"
                @keyup.enter="handleSearchAndClose"
                @keydown.esc="closeSearchPanel"
                type="search"
                :placeholder="transliterationEnabled ? 'Type in English... (e.g., aram)' : 'இலக்கிய சொல் தேடல்'"
                class="search-input"
                autocomplete="off"
              />

              <div v-if="transliterationEnabled && searchQuery" class="tamil-preview">
                {{ searchQuery }}
              </div>

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

            <button
              @click="toggleTransliteration"
              class="transliteration-toggle-btn"
              :class="{ active: transliterationEnabled }"
              :title="transliterationEnabled ? 'Transliteration ON (A→அ)' : 'Transliteration OFF'"
            >
              <span class="transliteration-icon">
                <span class="en-letter">A</span>
                <span class="arrow">→</span>
                <span class="ta-letter">அ</span>
              </span>
            </button>
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
              <!-- CollectionTree handles its own controls -->
              <Transition name="expand">
                <div v-if="collectionsExpanded" class="section-content">
                  <CollectionTree
                    ref="collectionTreeRef"
                    v-model:selected-works="selectedWorks"
                    @applyFilter="handleSearchAndClose"
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

    <!-- Menu Dropdown (Mobile) -->
    <div v-if="menuExpanded" class="menu-backdrop" @click="closeMenu"></div>
    <div
      v-if="menuExpanded"
      class="menu-dropdown"
      :style="{ top: menuPosition.top, right: menuPosition.right }"
    >
      <router-link :to="{ name: 'Home' }" class="menu-item" @click="closeMenu">
        Home
      </router-link>
      <router-link
        v-if="isWorksBrowserVisible"
        :to="{ name: 'WorksList' }"
        class="menu-item"
        @click="closeMenu"
      >
        Browse Works
      </router-link>
      <router-link :to="{ name: 'Acknowledgment' }" class="menu-item" @click="closeMenu">
        Acknowledgment
      </router-link>

      <!-- Help Menu Group -->
      <div class="menu-item-group">
        <div class="menu-group-label" @click="toggleHelpSubmenu">
          <span>Help and Docs</span>
          <span class="submenu-arrow">{{ helpSubmenuExpanded ? '▼' : '▶' }}</span>
        </div>
        <div v-if="helpSubmenuExpanded" class="submenu-items">
          <router-link :to="{ name: 'QuickStart' }" class="menu-subitem" @click="closeMenu">
            Quick Start
          </router-link>
          <router-link :to="{ name: 'UnderstandingThisTool' }" class="menu-subitem" @click="closeMenu">
            Understanding This Tool
          </router-link>
          <router-link :to="{ name: 'WordSegmentation' }" class="menu-subitem" @click="closeMenu">
            Word Segmentation
          </router-link>
          <router-link :to="{ name: 'TransliterationGuide' }" class="menu-subitem" @click="closeMenu">
            Transliteration Guide
          </router-link>
        </div>
      </div>

      <!-- The Story Behind Menu Group -->
      <div class="menu-item-group">
        <div class="menu-group-label" @click="toggleStorySubmenu">
          <span>The Story Behind</span>
          <span class="submenu-arrow">{{ storySubmenuExpanded ? '▼' : '▶' }}</span>
        </div>
        <div v-if="storySubmenuExpanded" class="submenu-items">
          <router-link :to="{ name: 'Journey' }" class="menu-subitem" @click="closeMenu">
            The Journey
          </router-link>
          <router-link :to="{ name: 'Inspiration' }" class="menu-subitem" @click="closeMenu">
            Guiding Exemplars
          </router-link>
        </div>
      </div>

      <!-- Login Button (Guest) or Profile Menu (Admin) - Mobile -->
      <div v-if="isGuest" class="menu-item-group">
        <button @click="handleMobileLogin" class="menu-item">
          <span>Login</span>
        </button>
      </div>
      <div v-else class="menu-item-group profile-menu-group">
        <div class="menu-group-label profile-label" @click="toggleProfileSubmenu">
          <div class="profile-label-content">
            <span class="profile-icon">👤</span>
            <span>{{ currentUser }}</span>
          </div>
          <span class="submenu-arrow">{{ profileSubmenuExpanded ? '▼' : '▶' }}</span>
        </div>
        <div v-if="profileSubmenuExpanded" class="submenu-items">
          <div class="profile-info-mobile">
            <div class="profile-username-mobile">{{ currentUser }}</div>
            <div class="profile-role-mobile">Administrator</div>
          </div>
          <router-link v-if="currentUser === 'admin'" :to="{ name: 'Admin' }" @click="closeMenu" class="menu-subitem">
            <span class="menu-item-icon">⚙️</span>
            <span>Admin</span>
          </router-link>
          <button @click="handleLogout" class="menu-subitem logout-mobile">
            <span class="menu-item-icon">🚪</span>
            <span>Logout</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Login Modal (Teleport to body) -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="showLoginModal" class="login-modal-overlay" @click="closeLoginModal">
          <div class="login-modal" @click.stop>
            <button @click="closeLoginModal" class="modal-close-btn" title="Close">×</button>
            <h2>Admin Login</h2>
            <p class="login-subtitle">Manage collections and contents</p>

            <form @submit.prevent="handleLogin" class="login-form">
              <div class="form-group">
                <input
                  v-model="loginUsername"
                  type="text"
                  placeholder="Username"
                  required
                  autocomplete="username"
                />
              </div>
              <div class="form-group">
                <input
                  v-model="loginPassword"
                  type="password"
                  placeholder="Password"
                  required
                  autocomplete="current-password"
                />
              </div>
              <div v-if="loginError" class="error-message">{{ loginError }}</div>
              <button type="submit" class="btn-login" :disabled="loginLoading">
                {{ loginLoading ? 'Logging in...' : 'Login' }}
              </button>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSearchState } from '../composables/useSearchState.js'
import { useUserRole } from '../composables/useUserRole.js'
import { useFilterState } from '../composables/useFilterState.js'
import { useStats } from '../composables/useStats.js'
import { useTransliteration } from '../composables/useTransliteration.js'
import CollectionTree from './CollectionTree.vue'

const router = useRouter()
const route = useRoute()
const searchInput = ref(null)
const panelSearchInput = ref(null)
const searchContainer = ref(null)
const collectionTreeRef = ref(null)
const searchQuery = ref('')
const englishInput = ref('') // For transliteration
const searchFocused = ref(false)
const collectionsExpanded = ref(true)
const isTreeExpanded = ref(false)
const menuExpanded = ref(false)
const helpSubmenuExpanded = ref(false)
const storySubmenuExpanded = ref(false)
const profileSubmenuExpanded = ref(false)
const profileMenuOpen = ref(false)
const helpMenuOpen = ref(false)
const storyMenuOpen = ref(false)
const showLoginModal = ref(false)
const loginUsername = ref('')
const loginPassword = ref('')
const loginError = ref(null)
const loginLoading = ref(false)
const menuBtn = ref(null)
const profileDropdown = ref(null)
const helpDropdown = ref(null)
const storyDropdown = ref(null)
const menuPosition = ref({ top: '58px', right: '1rem' })

// Transliteration
const { transliterationEnabled, transliterate, toggleTransliteration } = useTransliteration()

// Mock data - replace with real data
const suggestions = ref([])
const quickCategories = ref([
  { id: 'sangam', icon: '🏛️', name: 'Sangam', nameTamil: 'சங்க இலக்கியம்' },
  { id: 'thirukkural', icon: '📖', name: 'Thirukkural', nameTamil: 'திருக்குறள்' },
  { id: 'devotional', icon: '🙏', name: 'Devotional', nameTamil: 'பக்தி இலக்கியம்' },
  { id: 'ethics', icon: '📚', name: 'Ethics', nameTamil: 'நீதிநூல்கள்' },
])
const exampleWords = ref(['அறம்', 'காதல்', 'நீதி', 'இன்பம்'])

const { clearSearch, matchType, wordPosition, sortBy } = useSearchState()
const { selectedWorks, filterMode, hasFiltersChanged } = useFilterState()

const { stats, loadStats } = useStats()

// Load stats once per session
if (!stats.value) {
  loadStats()
}

const isMobile = computed(() => {
  if (typeof window === 'undefined') return false
  return window.innerWidth < 768
})

// User role management
const { currentUser, isGuest, canBrowseWorks, logout } = useUserRole()

const isWorksBrowserVisible = computed(() => canBrowseWorks.value)

const handleLogout = () => {
  profileMenuOpen.value = false
  closeMenu()
  logout()
  router.push({ name: 'Home' })
}

const toggleProfileMenu = () => {
  profileMenuOpen.value = !profileMenuOpen.value
  helpMenuOpen.value = false
  storyMenuOpen.value = false
}

const handleProfileBlur = (event) => {
  // Delay closing to allow click events on menu items
  setTimeout(() => {
    if (!profileDropdown.value?.contains(document.activeElement)) {
      profileMenuOpen.value = false
    }
  }, 200)
}

const toggleHelpMenu = () => {
  helpMenuOpen.value = !helpMenuOpen.value
  profileMenuOpen.value = false
  storyMenuOpen.value = false
}

const handleHelpBlur = (event) => {
  setTimeout(() => {
    if (!helpDropdown.value?.contains(document.activeElement)) {
      helpMenuOpen.value = false
    }
  }, 200)
}

const toggleStoryMenu = () => {
  storyMenuOpen.value = !storyMenuOpen.value
  profileMenuOpen.value = false
  helpMenuOpen.value = false
}

const handleStoryBlur = (event) => {
  setTimeout(() => {
    if (!storyDropdown.value?.contains(document.activeElement)) {
      storyMenuOpen.value = false
    }
  }, 200)
}

const closeLoginModal = () => {
  showLoginModal.value = false
  loginUsername.value = ''
  loginPassword.value = ''
  loginError.value = null
  loginLoading.value = false
}

const handleLogin = async () => {
  loginError.value = null
  loginLoading.value = true

  const { login } = useUserRole()
  const result = await login(loginUsername.value, loginPassword.value)

  if (result.success) {
    closeLoginModal()
    router.push({ name: 'Home' })
  } else {
    loginError.value = result.error
    loginLoading.value = false
  }
}

const handleMobileLogin = () => {
  closeMenu()
  showLoginModal.value = true
}

const isCollectionTreeLoading = computed(() => {
  return collectionTreeRef.value?.loading || false
})

// Sync with URL
watch(() => route.query.q, (newQuery) => {
  if (newQuery) {
    searchQuery.value = newQuery
    englishInput.value = newQuery
  } else if (route.name !== 'QuickStart') {
    searchQuery.value = ''
    englishInput.value = ''
  }
})

// Initialize from URL
if (route.query.q) {
  searchQuery.value = route.query.q
  englishInput.value = route.query.q
}

// Watch englishInput and transliterate to Tamil
watch(englishInput, (newValue) => {
  if (transliterationEnabled.value && newValue) {
    searchQuery.value = transliterate(newValue)
  } else if (!transliterationEnabled.value) {
    // When disabled, sync englishInput to searchQuery
    searchQuery.value = newValue
  }
})

// When transliteration is toggled, update the search query
watch(transliterationEnabled, (enabled) => {
  if (enabled && englishInput.value) {
    searchQuery.value = transliterate(englishInput.value)
  } else if (!enabled && englishInput.value) {
    searchQuery.value = englishInput.value
  }
})

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

    // Set filter mode based on selection
    if (selectedWorks.value.length > 0) {
      filterMode.value = 'select'
    } else {
      filterMode.value = 'all'
    }

    // Navigate to search results with filter params
    router.push({
      name: 'SearchResults',
      query: {
        q: searchQuery.value.trim(),
        type: matchType.value,
        pos: wordPosition.value,
        sort: sortBy.value
      }
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

    // Build query params
    const queryParams = {
      q: searchQuery.value.trim(),
      type: matchType.value,
      pos: wordPosition.value,
      sort: sortBy.value
    }

    // If on SearchResults page and filters changed, add timestamp to force refresh
    if (route.name === 'SearchResults' && hasFiltersChanged.value) {
      queryParams._t = Date.now()
    }

    // Navigate to search results with filter params
    router.push({
      name: 'SearchResults',
      query: queryParams
    })
  } else {
    // If no search query, just close the panel
    closeSearchPanel()
  }
}

function clearSearchInput() {
  searchQuery.value = ''
  englishInput.value = ''
  clearSearch()
  router.push({ name: 'QuickStart' })
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
  helpSubmenuExpanded.value = false
  storySubmenuExpanded.value = false
  profileSubmenuExpanded.value = false
}

function toggleHelpSubmenu() {
  helpSubmenuExpanded.value = !helpSubmenuExpanded.value
}

function toggleStorySubmenu() {
  storySubmenuExpanded.value = !storySubmenuExpanded.value
}

function toggleProfileSubmenu() {
  profileSubmenuExpanded.value = !profileSubmenuExpanded.value
}

function goToHome() {
  router.push({ name: 'Home' })
}

// Close menu on route change
watch(() => route.path, () => {
  menuExpanded.value = false
  helpSubmenuExpanded.value = false
  storySubmenuExpanded.value = false
  profileSubmenuExpanded.value = false
  profileMenuOpen.value = false
  helpMenuOpen.value = false
  storyMenuOpen.value = false
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

// Listen for event to open search panel from other components
window.addEventListener('open-search-panel', () => {
  searchFocused.value = true
})
</script>

<style scoped>
/* Header Wrapper */
.header-wrapper {
  position: sticky;
  top: 0;
  z-index: 100;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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

.logo-icon-img {
  width: 32px;
  height: 32px;
  object-fit: contain;
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  border: 2px solid transparent;
  border-radius: 24px;
  padding: 0.25rem 0.5rem 0.25rem 0.75rem;
  transition: all 150ms ease;
  position: relative;
}

.search-box.focused {
  border-color: #60a5fa;
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.2);
}

.tamil-preview {
  position: absolute;
  right: 60px;
  font-size: 1rem;
  color: #1e40af;
  font-weight: 600;
  pointer-events: none;
  background: white;
  padding: 0 0.5rem;
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

.transliteration-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  padding: 0;
  background: #f3f4f6;
  border: 2px solid #d1d5db;
  border-radius: 50%;
  cursor: pointer;
  transition: all 150ms ease;
  flex-shrink: 0;
}

.transliteration-icon {
  display: flex;
  align-items: center;
  gap: 1px;
  font-size: 0.65rem;
  font-weight: 700;
}

.en-letter {
  color: #9ca3af;
  transition: all 150ms ease;
}

.arrow {
  color: #d1d5db;
  font-size: 0.65rem;
}

.ta-letter {
  color: #9ca3af;
  font-size: 0.75rem;
  transition: all 150ms ease;
}

.transliteration-toggle-btn:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
  transform: scale(1.1);
}

.transliteration-toggle-btn.active {
  background: #dbeafe;
  border-color: #60a5fa;
}

.transliteration-toggle-btn.active .en-letter {
  color: #1e40af;
}

.transliteration-toggle-btn.active .arrow {
  color: #60a5fa;
}

.transliteration-toggle-btn.active .ta-letter {
  color: #1e40af;
  font-weight: 800;
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

/* My Profile Tab Dropdown (Desktop) */
.profile-tab-dropdown {
  position: relative;
}

.profile-tab-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
}

.profile-tab-button:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.profile-tab-button.profile-active {
  color: white;
  border-bottom-color: #60a5fa;
  background: rgba(255, 255, 255, 0.05);
}

.profile-icon {
  font-size: 1rem;
}

.profile-name {
  font-weight: 600;
}

.dropdown-arrow {
  font-size: 0.6rem;
  opacity: 0.7;
}

.profile-tab-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  min-width: 220px;
  z-index: 1000;
  animation: slideDown 0.2s ease-out;
}

.profile-menu-header {
  padding: 1rem;
}

.profile-user-info {
  text-align: left;
}

.profile-username {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
}

.profile-role {
  font-size: 0.8rem;
  color: #7f8c8d;
  margin-top: 0.2rem;
}

.profile-menu-divider {
  height: 1px;
  background: #eee;
  margin: 0;
}

.profile-menu-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  width: 100%;
  padding: 0.8rem 1rem;
  background: none;
  border: none;
  color: #495057;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
  text-align: left;
}

.profile-menu-item:hover {
  background: #f8f9fa;
}

.profile-menu-item.logout-item {
  color: #e74c3c;
  border-radius: 0 0 8px 8px;
}

.profile-menu-item.logout-item:hover {
  background: #fee;
}

.menu-item-icon {
  font-size: 1rem;
}

/* My Profile in Mobile Menu */
.profile-menu-group {
  border-top: 1px solid #ddd;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
}

.profile-label {
  background: #f8f9fa !important;
  font-weight: 600;
}

.profile-label-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.profile-info-mobile {
  padding: 0.75rem 1rem;
  background: #f8f9fa;
  margin: 0 0.5rem 0.25rem 0.5rem;
  border-radius: 4px;
}

.profile-username-mobile {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

.profile-role-mobile {
  font-size: 0.75rem;
  color: #7f8c8d;
  margin-top: 0.2rem;
}

.logout-mobile {
  color: #e74c3c !important;
  background: none;
  border: none;
  width: 100%;
  text-align: left;
  justify-content: flex-start;
}

/* Desktop Navigation Tabs */
.desktop-nav-tabs {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 0.5rem 2rem;
  background: #1a3a5a;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-tab {
  padding: 0.75rem 1.25rem;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  border-bottom: 3px solid transparent;
  transition: all 0.2s ease;
  white-space: nowrap;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
}

.nav-tab:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.nav-tab.router-link-exact-active {
  color: white;
  border-bottom-color: #60a5fa;
  background: rgba(255, 255, 255, 0.05);
  font-weight: 600;
}

/* Show/Hide based on screen size */
.mobile-only {
  display: none;
}

.desktop-nav-tabs {
  display: flex;
}

@media (min-width: 769px) {
  .mobile-only {
    display: none;
  }
  .desktop-nav-tabs {
    display: flex;
  }
}

@media (max-width: 768px) {
  .mobile-only {
    display: flex;
  }
  .desktop-nav-tabs {
    display: none;
  }
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
  position: relative;
}

.panel-search-box .tamil-preview {
  position: absolute;
  right: 50px;
  font-size: 0.95rem;
  color: #1e40af;
  font-weight: 600;
  pointer-events: none;
  background: white;
  padding: 0 0.5rem;
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
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:hover {
  background: #f9fafb;
}

.menu-item.router-link-exact-active {
  background: #eff6ff;
  color: #1e40af;
  font-weight: 600;
}

/* Menu Item Group (with submenu) */
.menu-item-group {
  border-bottom: 1px solid #f3f4f6;
}

.menu-group-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  color: #374151;
  font-size: 0.9rem;
  font-weight: 600;
  background: #f9fafb;
  cursor: pointer;
  transition: background 150ms ease;
  user-select: none;
}

.menu-group-label:hover {
  background: #f3f4f6;
}

.submenu-arrow {
  font-size: 0.7rem;
  color: #6b7280;
  transition: transform 0.2s;
}

.submenu-items {
  animation: slideDown 0.2s ease-out;
}

.menu-subitem {
  display: block;
  padding: 0.7rem 1rem 0.7rem 2rem;
  color: #374151;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 500;
  transition: background 150ms ease;
  border-bottom: 1px solid #f9fafb;
}

.menu-subitem:last-child {
  border-bottom: none;
}

.menu-subitem:hover {
  background: #f3f4f6;
}

.menu-subitem.router-link-exact-active {
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

/* Login Modal */
.login-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.login-modal {
  background: white;
  border-radius: 12px;
  padding: 2.5rem;
  max-width: 450px;
  width: 90%;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  position: relative;
}

.modal-close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 2rem;
  color: #6c757d;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.modal-close-btn:hover {
  background: #f1f3f5;
  color: #495057;
}

.login-modal h2 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.8rem;
}

.login-subtitle {
  color: #7f8c8d;
  margin: 0 0 2rem 0;
  font-size: 1rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  text-align: left;
}

.form-group input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.95rem;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.1);
}

.error-message {
  color: #e74c3c;
  font-size: 0.85rem;
  text-align: center;
  padding: 0.5rem;
  background: #ffe5e5;
  border-radius: 4px;
}

.btn-login {
  background: #4a90e2;
  color: white;
  border: none;
  padding: 0.9rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  margin-top: 0.5rem;
}

.btn-login:hover:not(:disabled) {
  background: #357abd;
}

.btn-login:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

/* Modal Fade Animation */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .login-modal,
.modal-fade-leave-active .login-modal {
  transition: transform 0.3s ease;
}

.modal-fade-enter-from .login-modal {
  transform: translateY(-20px);
}

.modal-fade-leave-to .login-modal {
  transform: translateY(20px);
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

  .logo-icon-img {
    width: 28px;
    height: 28px;
  }

  .header-search {
    flex: 1;
    max-width: 100%;
    margin: 0 0.5rem;
  }

  .search-box {
    padding: 0.2rem 0.3rem 0.2rem 0.5rem;
    gap: 0.3rem;
  }

  .search-input {
    font-size: 16px; /* Prevent iOS zoom */
    min-width: 80px;
    max-width: 180px
  }

  .tamil-preview {
    font-size: 0.9rem;
    right: 50px;
  }

  .transliteration-toggle-btn {
    width: 36px;
    height: 36px;
    flex-shrink: 0;
  }

  .transliteration-icon {
    font-size: 0.6rem;
    gap: 0.5px;
  }

  .ta-letter {
    font-size: 0.7rem;
  }

  .header-search {
    gap: 0.3rem;
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

  .panel-search-box .tamil-preview {
    font-size: 0.85rem;
    right: 40px;
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
