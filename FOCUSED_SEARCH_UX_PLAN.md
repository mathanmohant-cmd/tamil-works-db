# Tamil Literature Search - Focused UX Enhancement Plan
## Walmart-Inspired Search UI for Academic Research

**Last Updated:** 2026-01-12
**Goal:** Modern search experience adapted for academic Tamil literature research

---

## 🎯 Core Requirements (Your Feedback)

### ✅ What We're Taking from Walmart:
1. **Edge-to-edge search panel expansion** (mobile & desktop)
2. **Search box with integrated clear (×) and search (🔍) buttons**
3. **Logo + Search + Menu all in one header line** (across all devices)
4. **Autocomplete suggestions dropdown** for entered words
5. **Modern, clean UI aesthetic**

### ❌ What We're NOT Taking:
- ~~Trending/Popular searches~~ (not needed for academic use)
- ~~Retail-style category cards with images~~ (we have collections tree)
- ~~Shopping-oriented shortcuts~~

### 🎓 What We're Keeping/Improving:
- **Collections TreeView** (improve UI, keep functionality)
- **Full choice selection** (all collections from database)
- **Academic search focus** (word research, not product shopping)

---

## 📐 New Header Layout (All Devices)

### One-Line Header Design

```
┌─────────────────────────────────────────────────────────┐
│ [📚 Logo] [Search Tamil literature... × 🔍] [☰ Menu]  │
└─────────────────────────────────────────────────────────┘
```

### Layout Breakdown

#### **Mobile (375px):**
```
┌──────────────────────────────────────────────┐
│ [📚] [Search... × 🔍] [☰]                   │  ← 60px height
└──────────────────────────────────────────────┘
   40px   flexible        48px

- Logo: 40px icon/text
- Search: flex-grow (fills available space)
- Menu: 48px hamburger button
```

#### **Tablet (768px):**
```
┌────────────────────────────────────────────────────────┐
│ [📚 Tamil Lit] [Search Tamil literature... × 🔍] [☰ Menu] │
└────────────────────────────────────────────────────────┘
      120px              flexible               80px

- Logo: 120px (icon + text)
- Search: flex-grow
- Menu: 80px text button
```

#### **Desktop (1920px):**
```
┌──────────────────────────────────────────────────────────────────────┐
│ [📚 Tamil Literature DB] [Search Tamil literature... × 🔍] [☰ Menu] │
└──────────────────────────────────────────────────────────────────────┘
         200px                      800px max                  100px

- Logo: 200px (full branding)
- Search: max-width 800px, centered
- Menu: 100px text button
```

---

## 🔍 Enhanced Search Box Design

### Search Box Anatomy

```
┌──────────────────────────────────────────────┐
│ [🔍] Search Tamil words...          [×]     │
└──────────────────────────────────────────────┘
   24px    input (flex-grow)         32px

When typing:
┌──────────────────────────────────────────────┐
│ [🔍] அறம்                            [×]     │
└──────────────────────────────────────────────┘
```

### States:

1. **Empty (Default):**
   - Placeholder: "தேடல் (Search Tamil words)"
   - Search icon (🔍) on left
   - No clear button

2. **Focused (Empty):**
   - Border highlight (blue)
   - Dropdown appears (Collections TreeView)
   - Placeholder visible

3. **Typing:**
   - Search icon (🔍) on left
   - Text in input
   - Clear button (×) appears on right
   - Dropdown shows: Collections Tree + Autocomplete suggestions

4. **Filled (Not Focused):**
   - Text visible
   - Clear button (×) visible
   - No dropdown

---

## 🎨 Edge-to-Edge Search Dropdown

### Mobile Behavior (Full-Screen Takeover)

```
BEFORE CLICK:
┌────────────────────────┐
│ [📚] [Search...] [☰]  │
├────────────────────────┤
│                        │
│   Page Content...      │
│                        │
└────────────────────────┘

AFTER CLICK (Full Screen):
┌────────────────────────┐
│ [🔍] அற         [×] [Cancel] │ ← Search bar fixed at top
├────────────────────────┤
│ தொகுப்புகள் (Collections)│ ← Collapsible section
│ └─ 📚 Tamil Literature │
│    ├─ ✓ சங்க இலக்கியம் │ ← Tree with checkboxes
│    ├─ ☐ பக்தி இலக்கியம் │
│    └─ ☐ நீதிநூல்கள்    │
├────────────────────────┤
│ பரிந்துரைகள் (Suggestions)│ ← Auto-generated
│ • **அற**ம் (213)       │ ← Bold match, count
│ • **அற**ன் (45)        │
│ • **அற**து (89)        │
│ • **அற**கூற்று (12)    │
└────────────────────────┘
   (Scrollable content)
```

### Desktop Behavior (Positioned Dropdown)

```
┌──────────────────────────────────────────────┐
│ [📚 Logo] [Search: அற × 🔍] [☰ Menu]        │
├──────────────────────────────────────────────┤
│          ┌──────────────────────┐            │
│          │ தொகுப்புகள் ▼        │            │
│          │ └─ Tamil Literature  │            │
│          │    ├─ ✓ சங்க இலக்கியம்│            │
│          │    ├─ ☐ பக்தி இலக்கியம்│           │
│          ├─────────────────────┤            │
│          │ பரிந்துரைகள்         │            │
│          │ • **அற**ம் (213)    │            │
│          │ • **அற**ன் (45)     │            │
│          │ • **அற**து (89)     │            │
│          └─────────────────────┘            │
│                                              │
│   Page Content (still visible/scrollable)   │
└──────────────────────────────────────────────┘
```

---

## 🌳 Collections Tree UI Enhancement

### Current Issue:
TreeView is functional but not best UI (your feedback)

### Improved Design:

#### **Compact Tree with Better Visual Hierarchy**

```
┌────────────────────────────────────────┐
│ தொகுப்புகள் (Collections)  [Collapse ▲]│
├────────────────────────────────────────┤
│ Tamil Literature                    [3]│ ← Work count badge
│ ├─ 📖 Classical (சங்ககாலம்)        [18]│
│ │  ├─ ☑ Thirukkural                   │
│ │  ├─ ☑ Tolkappiyam                   │
│ │  └─ ☐ 18 Lesser Texts            [17]│
│ ├─ 🙏 Devotional (பக்தி)            [41]│
│ │  ├─ ☐ Thirumurai                 [14]│
│ │  ├─ ☐ Divya Prabandham          [24]│
│ │  └─ ☐ Other                       [3]│
│ └─ 📚 Ethics (நீதி)                 [21]│
│    └─ ☐ All Ethics Works          [21]│
├────────────────────────────────────────┤
│ [Clear All] [Select All]              │
└────────────────────────────────────────┘
```

### Key Improvements:

1. **Collapsible Header** - Can minimize entire section
2. **Work Count Badges** - `[18]` shows # of works in collection
3. **Icons** - Visual category indicators (📖 📚 🙏)
4. **Bilingual Labels** - English + Tamil in parentheses
5. **Indentation** - Clear visual hierarchy (0.5rem per level)
6. **Checkbox Alignment** - Perfect 20px × 20px, consistent spacing
7. **Action Buttons** - Clear All / Select All at bottom

---

## 🎨 Design System Refinement

### Colors (Academic Theme)

```css
:root {
  /* Primary - Blue for academic/scholarly feel */
  --primary: #1e40af;           /* Deep blue */
  --primary-hover: #1e3a8a;     /* Darker blue */
  --primary-light: #dbeafe;     /* Light blue bg */

  /* Text */
  --text-primary: #111827;      /* Almost black */
  --text-secondary: #6b7280;    /* Gray for meta */
  --text-tertiary: #9ca3af;     /* Light gray */

  /* Background */
  --bg-primary: #ffffff;        /* White */
  --bg-secondary: #f9fafb;      /* Off-white */
  --bg-hover: #f3f4f6;          /* Hover gray */

  /* Border */
  --border-light: #e5e7eb;
  --border-medium: #d1d5db;
  --border-focus: #3b82f6;      /* Blue focus ring */

  /* Shadow */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);

  /* Tamil-specific */
  --tamil-red: #b91c1c;         /* For highlighting (optional)
}
```

### Typography

```css
:root {
  /* Font Families */
  --font-tamil: 'Noto Sans Tamil', 'Lohit Tamil', sans-serif;
  --font-latin: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'SF Mono', 'Courier New', monospace;

  /* Font Sizes */
  --text-xs: 12px;
  --text-sm: 14px;
  --text-base: 16px;
  --text-lg: 18px;
  --text-xl: 20px;
  --text-2xl: 24px;

  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
}
```

### Spacing

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  /* Component-specific */
  --header-height: 60px;
  --search-height-mobile: 44px;
  --search-height-desktop: 40px;
  --dropdown-max-height: 600px;
  --touch-target: 48px;
}
```

---

## 🏗️ Component Architecture

### File Structure

```
src/
├── components/
│   ├── header/
│   │   ├── AppHeader.vue              ← New unified header
│   │   ├── HeaderLogo.vue             ← Logo component
│   │   ├── HeaderSearch.vue           ← Enhanced search box
│   │   └── HeaderMenu.vue             ← Menu button
│   ├── search/
│   │   ├── SearchDropdown.vue         ← Edge-to-edge dropdown
│   │   ├── CollectionsTree.vue        ← Improved tree (existing, enhance)
│   │   ├── AutocompleteSuggestions.vue ← New autocomplete list
│   │   └── SuggestionItem.vue         ← Individual suggestion row
│   └── ui/
│       ├── Button.vue
│       ├── Icon.vue
│       └── Checkbox.vue
├── composables/
│   ├── useSearchBox.js                ← Search box state
│   ├── useAutocomplete.js             ← Debounced autocomplete
│   └── useCollectionsTree.js          ← Tree state (existing)
└── assets/
    └── styles/
        ├── header.css                 ← Header styles
        ├── search-dropdown.css        ← Dropdown styles
        └── collections-tree.css       ← Enhanced tree styles
```

---

## 💻 Implementation Code

### 1. New Unified Header Component

```vue
<!-- src/components/header/AppHeader.vue -->
<template>
  <header class="app-header">
    <div class="header-container">
      <!-- Logo -->
      <HeaderLogo class="header-logo" />

      <!-- Search Box (Fills Available Space) -->
      <HeaderSearch class="header-search" />

      <!-- Menu Button -->
      <HeaderMenu class="header-menu" />
    </div>
  </header>
</template>

<script setup>
import HeaderLogo from './HeaderLogo.vue'
import HeaderSearch from './HeaderSearch.vue'
import HeaderMenu from './HeaderMenu.vue'
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: white;
  border-bottom: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
}

.header-container {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: var(--header-height);
  padding: 0 var(--space-4);
  max-width: 1920px;
  margin: 0 auto;
}

.header-logo {
  flex-shrink: 0;
}

.header-search {
  flex: 1;
  max-width: 800px; /* Desktop max width */
}

.header-menu {
  flex-shrink: 0;
}

/* Mobile adjustments */
@media (max-width: 767px) {
  .header-container {
    gap: var(--space-2);
    padding: 0 var(--space-2);
  }

  .header-search {
    max-width: none; /* Full width on mobile */
  }
}
</style>
```

### 2. Enhanced Search Box Component

```vue
<!-- src/components/header/HeaderSearch.vue -->
<template>
  <div class="search-container" ref="searchContainer">
    <!-- Search Input -->
    <div class="search-box" :class="{ focused: isFocused }">
      <button class="search-icon-btn" @click="performSearch" aria-label="Search">
        <SearchIcon />
      </button>

      <input
        ref="searchInput"
        v-model="query"
        @focus="handleFocus"
        @blur="handleBlur"
        @keydown.enter="performSearch"
        @keydown.esc="closeDropdown"
        type="search"
        placeholder="தேடல் (Search Tamil words)"
        class="search-input"
        autocomplete="off"
      />

      <button
        v-if="query"
        @click="clearSearch"
        class="clear-btn"
        aria-label="Clear search"
      >
        ×
      </button>
    </div>

    <!-- Dropdown (Edge-to-Edge) -->
    <Teleport to="body">
      <Transition name="dropdown-fade">
        <SearchDropdown
          v-if="showDropdown"
          :query="query"
          :suggestions="suggestions"
          @select="handleSelect"
          @close="closeDropdown"
        />
      </Transition>

      <!-- Mobile Backdrop -->
      <Transition name="backdrop-fade">
        <div
          v-if="showDropdown && isMobile"
          class="search-backdrop"
          @click="closeDropdown"
        />
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useSearchBox } from '@/composables/useSearchBox'
import { useAutocomplete } from '@/composables/useAutocomplete'
import SearchDropdown from '@/components/search/SearchDropdown.vue'
import SearchIcon from '@/components/ui/Icon.vue'

const searchInput = ref(null)
const searchContainer = ref(null)
const isFocused = ref(false)

const { query, performSearch, clearSearch } = useSearchBox()
const { suggestions, loading } = useAutocomplete(query)

const isMobile = computed(() => window.innerWidth < 768)
const showDropdown = computed(() => isFocused.value)

function handleFocus() {
  isFocused.value = true
}

function handleBlur(event) {
  // Don't close if clicking inside dropdown
  if (event.relatedTarget?.closest('.search-dropdown')) {
    return
  }
  setTimeout(() => {
    isFocused.value = false
  }, 200)
}

function closeDropdown() {
  isFocused.value = false
  searchInput.value?.blur()
}

function handleSelect(word) {
  query.value = word
  closeDropdown()
  performSearch()
}
</script>

<style scoped>
.search-container {
  position: relative;
  width: 100%;
}

.search-box {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  background: white;
  border: 2px solid var(--border-light);
  border-radius: 24px;
  padding: var(--space-2) var(--space-4);
  transition: all 150ms ease;
}

.search-box.focused {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px var(--primary-light);
}

.search-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color 150ms ease;
}

.search-icon-btn:hover {
  color: var(--primary);
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: var(--text-base);
  font-family: var(--font-tamil);
  background: transparent;
  color: var(--text-primary);
}

.search-input::placeholder {
  color: var(--text-tertiary);
}

/* Hide default search input clear button */
.search-input::-webkit-search-cancel-button {
  display: none;
}

.clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  background: var(--bg-hover);
  border: none;
  border-radius: 50%;
  font-size: 24px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 150ms ease;
}

.clear-btn:hover {
  background: var(--border-medium);
  color: var(--text-primary);
}

/* Mobile adjustments */
@media (max-width: 767px) {
  .search-box {
    padding: var(--space-1) var(--space-3);
  }

  .search-input {
    font-size: 16px; /* Prevent iOS zoom */
  }
}

/* Backdrop for mobile */
.search-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 998;
}

/* Animations */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 200ms ease-out, transform 200ms ease-out;
}

.dropdown-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.dropdown-fade-leave-to {
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
</style>
```

### 3. Edge-to-Edge Search Dropdown

```vue
<!-- src/components/search/SearchDropdown.vue -->
<template>
  <div
    class="search-dropdown"
    :class="{ mobile: isMobile }"
    @click.stop
  >
    <div class="dropdown-content">
      <!-- Collections Tree Section (Collapsible) -->
      <section class="collections-section">
        <button
          @click="collectionsExpanded = !collectionsExpanded"
          class="section-header"
        >
          <span class="section-title">
            தொகுப்புகள் (Collections)
          </span>
          <ChevronIcon :class="{ rotated: collectionsExpanded }" />
        </button>

        <Transition name="expand">
          <div v-if="collectionsExpanded" class="section-content">
            <CollectionsTree
              v-model:selected="selectedCollections"
              :compact="true"
            />
            <div class="section-actions">
              <button @click="clearCollections" class="text-btn">
                Clear All
              </button>
              <button @click="selectAllCollections" class="text-btn">
                Select All
              </button>
            </div>
          </div>
        </Transition>
      </section>

      <!-- Autocomplete Suggestions Section -->
      <section v-if="query && suggestions.length" class="suggestions-section">
        <div class="section-header">
          <span class="section-title">
            பரிந்துரைகள் (Suggestions)
          </span>
          <span class="section-count">{{ suggestions.length }}</span>
        </div>

        <div class="section-content">
          <AutocompleteSuggestions
            :suggestions="suggestions"
            :query="query"
            @select="$emit('select', $event)"
          />
        </div>
      </section>

      <!-- Empty State (when no query) -->
      <section v-if="!query" class="empty-state">
        <p class="empty-message">
          Type to search Tamil words across all literary works
        </p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import CollectionsTree from './CollectionsTree.vue'
import AutocompleteSuggestions from './AutocompleteSuggestions.vue'
import ChevronIcon from '@/components/ui/Icon.vue'

const props = defineProps({
  query: String,
  suggestions: Array
})

const emit = defineEmits(['select', 'close'])

const collectionsExpanded = ref(true)
const selectedCollections = ref([])

const isMobile = computed(() => window.innerWidth < 768)

function clearCollections() {
  selectedCollections.value = []
}

function selectAllCollections() {
  // Implementation: select all from tree
}
</script>

<style scoped>
/* Mobile: Fixed full-screen overlay */
.search-dropdown.mobile {
  position: fixed;
  top: var(--header-height);
  left: 0;
  right: 0;
  bottom: 0;
  background: white;
  z-index: 999;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* Desktop: Absolute positioned dropdown */
.search-dropdown:not(.mobile) {
  position: absolute;
  top: calc(var(--header-height) + 8px);
  left: 50%;
  transform: translateX(-50%);
  width: 800px;
  max-width: 90vw;
  max-height: var(--dropdown-max-height);
  background: white;
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  z-index: 999;
}

.dropdown-content {
  display: flex;
  flex-direction: column;
  max-height: inherit;
  overflow-y: auto;
}

/* Section Styling */
.collections-section,
.suggestions-section {
  border-bottom: 1px solid var(--border-light);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  background: var(--bg-secondary);
  border: none;
  width: 100%;
  cursor: pointer;
  transition: background 150ms ease;
}

.section-header:hover {
  background: var(--bg-hover);
}

.section-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.section-count {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  background: var(--bg-primary);
  padding: 2px 8px;
  border-radius: 12px;
}

.section-content {
  padding: var(--space-3) var(--space-4);
}

.section-actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px solid var(--border-light);
}

.text-btn {
  padding: var(--space-2) var(--space-3);
  background: none;
  border: 1px solid var(--border-medium);
  border-radius: 6px;
  font-size: var(--text-sm);
  color: var(--primary);
  cursor: pointer;
  transition: all 150ms ease;
}

.text-btn:hover {
  background: var(--primary-light);
  border-color: var(--primary);
}

/* Empty State */
.empty-state {
  padding: var(--space-8) var(--space-4);
  text-align: center;
}

.empty-message {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
}

/* Expand Animation */
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
  max-height: 600px;
  opacity: 1;
}

/* Chevron rotation */
.rotated {
  transform: rotate(180deg);
  transition: transform 200ms ease;
}
</style>
```

### 4. Autocomplete Suggestions Component

```vue
<!-- src/components/search/AutocompleteSuggestions.vue -->
<template>
  <ul class="suggestions-list" role="listbox">
    <li
      v-for="(suggestion, index) in suggestions"
      :key="suggestion.word_text"
      @click="$emit('select', suggestion.word_text)"
      class="suggestion-item"
      :class="{ active: index === activeIndex }"
      role="option"
    >
      <span class="word-text" v-html="highlightMatch(suggestion.word_text)"></span>
      <span class="word-meta">
        {{ suggestion.count }} முறை
      </span>
      <ArrowIcon class="arrow-icon" />
    </li>
  </ul>
</template>

<script setup>
import { computed } from 'vue'
import ArrowIcon from '@/components/ui/Icon.vue'

const props = defineProps({
  suggestions: Array,
  query: String,
  activeIndex: {
    type: Number,
    default: -1
  }
})

const emit = defineEmits(['select'])

function highlightMatch(text) {
  if (!props.query) return text

  const regex = new RegExp(`(${escapeRegex(props.query)})`, 'gi')
  return text.replace(regex, '<strong>$1</strong>')
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}
</script>

<style scoped>
.suggestions-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  transition: background 150ms ease;
  min-height: var(--touch-target);
}

.suggestion-item:hover,
.suggestion-item.active {
  background: var(--bg-hover);
}

.word-text {
  flex: 1;
  font-size: var(--text-base);
  font-family: var(--font-tamil);
  color: var(--text-primary);
}

.word-text :deep(strong) {
  font-weight: var(--font-bold);
  color: var(--primary);
}

.word-meta {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.arrow-icon {
  width: 16px;
  height: 16px;
  color: var(--text-tertiary);
}

/* Mobile: Larger touch targets */
@media (max-width: 767px) {
  .suggestion-item {
    padding: var(--space-4);
  }
}
</style>
```

---

## 📊 Implementation Phases

### **Phase 1: Header Unification (Week 1)** ⭐ START HERE

**Goal:** New header layout with Logo + Search + Menu in one line

**Tasks:**
1. Create `AppHeader.vue` with flex layout
2. Create placeholder `HeaderLogo.vue` (📚 icon for now)
3. Move existing search to `HeaderSearch.vue`
4. Create `HeaderMenu.vue` button
5. Make responsive (mobile/tablet/desktop)

**Testing:**
- [ ] All three elements in one line on mobile
- [ ] Logo + Search + Menu properly sized on tablet
- [ ] Centered search box on desktop (max 800px width)
- [ ] Header sticky at top on scroll

---

### **Phase 2: Search Box Enhancement (Week 2)**

**Goal:** Integrated clear (×) and search (🔍) buttons

**Tasks:**
1. Add search icon (🔍) on left of input
2. Add clear button (×) on right (appears when text entered)
3. Add focus states (blue border, shadow)
4. Style placeholder text (bilingual)
5. Handle click events (clear, search)

**Testing:**
- [ ] Search icon visible and clickable
- [ ] Clear button appears when typing
- [ ] Clear button removes text
- [ ] Enter key triggers search
- [ ] Focus ring visible and accessible

---

### **Phase 3: Edge-to-Edge Dropdown (Week 3)**

**Goal:** Full-screen mobile overlay, positioned dropdown on desktop

**Tasks:**
1. Create `SearchDropdown.vue` with responsive behavior
2. Mobile: Fixed position (top to bottom)
3. Desktop: Absolute position below search box
4. Add backdrop for mobile
5. Add entrance/exit animations (200ms)
6. Implement click-outside to close

**Testing:**
- [ ] Mobile: Full-screen overlay covers page
- [ ] Desktop: Dropdown positioned correctly below search
- [ ] Backdrop dims page on mobile
- [ ] Smooth fade + slide animation
- [ ] ESC key closes dropdown

---

### **Phase 4: Collections Tree Enhancement (Week 4)**

**Goal:** Improve existing tree UI without breaking functionality

**Tasks:**
1. Add collapsible header to tree section
2. Add work count badges `[18]` to each collection
3. Improve checkbox alignment (20px × 20px)
4. Add "Clear All" / "Select All" buttons
5. Add section separator lines
6. Optimize indentation for mobile (0.5rem)

**Testing:**
- [ ] Tree collapses/expands smoothly
- [ ] Work counts display correctly
- [ ] Checkboxes aligned perfectly
- [ ] "Clear All" clears all selections
- [ ] No horizontal scroll on mobile

---

### **Phase 5: Autocomplete Integration (Week 5)**

**Goal:** Show word suggestions below collections tree

**Tasks:**
1. Create `/search/autocomplete` API endpoint
2. Implement 200ms debounce
3. Create `AutocompleteSuggestions.vue` component
4. Bold matching text in suggestions
5. Show occurrence count (e.g., "213 முறை")
6. Add arrow icon (→) to each suggestion
7. Click suggestion fills search box and performs search

**Testing:**
- [ ] Type "அற" → See 10 suggestions
- [ ] Suggestions appear after 200ms
- [ ] Matching text is **bold**
- [ ] Click suggestion triggers search
- [ ] API response time < 300ms

---

### **Phase 6: Polish & Accessibility (Week 6)**

**Goal:** Keyboard navigation, screen readers, performance

**Tasks:**
1. Arrow Up/Down navigation through suggestions
2. Enter key selects highlighted suggestion
3. Add ARIA attributes (role, aria-label, etc.)
4. Screen reader announcements
5. Focus management (trap focus in dropdown)
6. Performance optimization (virtual scrolling if needed)

**Testing:**
- [ ] Full keyboard navigation works
- [ ] NVDA/JAWS screen reader compatible
- [ ] Focus indicators visible
- [ ] Tab navigation logical
- [ ] Lighthouse accessibility score > 90

---

## 🎨 Visual Design Mockups

### Mobile (375px) - Before & After

**BEFORE:**
```
┌────────────────────────┐
│ Tamil Literature DB    │
│ ─────────────────────  │
│                        │
│ Search: [_________] 🔍│
│                        │
│ ☰ Menu                 │
│ ─────────────────────  │
│                        │
│ Page Content...        │
└────────────────────────┘
```

**AFTER:**
```
┌────────────────────────┐
│ 📚 [Search... × 🔍] ☰ │ ← One-line header
├────────────────────────┤
│                        │
│ Page Content...        │
│                        │
└────────────────────────┘

[User clicks search box]
┌────────────────────────┐
│ 🔍 [அற        ×] Cancel│
├────────────────────────┤
│ தொகுப்புகள் ▼          │ ← Collapsible
│ └─ ✓ Classical [18]   │
│ └─ ☐ Devotional [41]  │
├────────────────────────┤
│ பரிந்துரைகள்           │
│ • **அற**ம் (213)      │
│ • **அற**ன் (45)       │
│ • **அற**து (89)       │
└────────────────────────┘
  (Full screen overlay)
```

### Desktop (1920px) - Before & After

**BEFORE:**
```
┌──────────────────────────────────────────────┐
│ Tamil Literature Database                    │
├──────────────────────────────────────────────┤
│ Search: [__________________] [🔍 Search]    │
│                                              │
│ Filters | Results                            │
└──────────────────────────────────────────────┘
```

**AFTER:**
```
┌──────────────────────────────────────────────────────────┐
│ [📚 Tamil Literature DB] [Search: அற × 🔍] [☰ Menu]     │
├──────────────────────────────────────────────────────────┤
│                   ┌─────────────────────┐                │
│                   │ தொகுப்புகள் ▼       │                │
│                   │ └─ Classical [18]   │                │
│                   ├─────────────────────┤                │
│                   │ பரிந்துரைகள்        │                │
│                   │ • **அற**ம் (213)   │                │
│                   └─────────────────────┘                │
│                                                          │
│ Page Content (visible and scrollable)                   │
└──────────────────────────────────────────────────────────┘
```

---

## ✅ Success Criteria

### Must Have Before Launch:
- [ ] Logo + Search + Menu in one line (all devices)
- [ ] Search box with integrated × and 🔍 buttons
- [ ] Edge-to-edge dropdown (mobile full-screen, desktop positioned)
- [ ] Collections tree visible and functional in dropdown
- [ ] Autocomplete suggestions working (10 suggestions, 200ms debounce)
- [ ] Bold matching text in suggestions
- [ ] Click suggestion performs search
- [ ] Responsive across mobile/tablet/desktop
- [ ] No horizontal scroll on any device

### Should Have (Post-Launch):
- [ ] Keyboard navigation (arrow keys, Enter, ESC)
- [ ] Screen reader compatible
- [ ] Work count badges on collections
- [ ] "Clear All" / "Select All" buttons
- [ ] Smooth animations (200ms)
- [ ] Collapsible collections section

---

## 🚀 Quick Start Commands

### Start Development:
```bash
# Backend
cd webapp/backend
python main.py

# Frontend
cd webapp/frontend
npm run dev
```

### Create New Components:
```bash
# Create header components
touch src/components/header/AppHeader.vue
touch src/components/header/HeaderLogo.vue
touch src/components/header/HeaderSearch.vue
touch src/components/header/HeaderMenu.vue

# Create search dropdown components
touch src/components/search/SearchDropdown.vue
touch src/components/search/AutocompleteSuggestions.vue
touch src/components/search/SuggestionItem.vue

# Create composables
touch src/composables/useSearchBox.js
touch src/composables/useAutocomplete.js

# Create styles
touch src/assets/styles/header.css
touch src/assets/styles/search-dropdown.css
```

---

## 📚 Next Steps

1. **Review this document** with team
2. **Create logo** (even simple 📚 icon + text for now)
3. **Start Phase 1** (Header unification)
4. **Test on real devices** (mobile + desktop)
5. **Iterate based on user feedback**

---

## 🎯 Key Takeaways (Your Requirements)

✅ **Edge-to-edge search panel** - Full-screen mobile, positioned desktop
✅ **Integrated search & clear** - × and 🔍 in search box
✅ **Logo + Search + Menu** - All in one header line
✅ **Collections tree** - Improved UI, full functionality
✅ **Autocomplete** - Word suggestions as you type
✅ **No trending/popular** - Focus on academic search
✅ **Responsive** - Works across all devices

Ready to start implementation? Begin with **Phase 1: Header Unification** ⭐
