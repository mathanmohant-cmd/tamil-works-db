# Mobile Sticky Navigation Options

**Date:** 2026-01-02
**Context:** Future mobile UI enhancement - Sticky header/navigation for better UX on Samsung S23

---

## Current Behavior (As of 2026-01-02)

- **Header:** Scrolls away naturally when user scrolls down
- **Navigation tabs:** Scroll away with header
- **Search controls:** Scroll away with header
- **User must scroll back to top** to access navigation or search again

---

## Future Enhancement Options

### Option 1: Simple Hide on Scroll ✨ SIMPLEST

**Behavior:**
- Hide navigation tabs when `searchResults` exists AND user is on mobile
- Show tabs again when search is cleared
- Everything else scrolls normally

**Implementation:**
```vue
<nav
  class="main-nav"
  v-show="shouldShowNavigation"
>
  <!-- tabs -->
</nav>

<script>
const shouldShowNavigation = computed(() => {
  if (!isMobile.value) return true // Always show on desktop

  // On mobile, hide if viewing search results
  if (currentPage.value === 'search' && searchResults.value && !showWelcome.value) {
    return false
  }

  return true
})
</script>
```

**Pros:**
- ✅ Saves ~50px vertical space on mobile
- ✅ Very simple (just `v-show` conditional)
- ✅ Clean UX - results get more space

**Cons:**
- ❌ User must click "Clear" before navigating to other pages
- ❌ No access to navigation while viewing results

**Space saved:** ~50px on mobile

---

### Option 2: Sticky Header + Slide-Down Menu ⭐ RECOMMENDED

**Behavior:**
- **Header + Search:** Sticky at top (always visible)
- **Navigation tabs:** Scroll away naturally
- **☰ Menu button:** Appears in header (mobile only)
- **Tapping menu:** Slides navigation tabs down temporarily

**Visual:**
```
SCROLLED DOWN:
┌─────────────────────────────┐
│ Tamil Title             ☰   │ ← Sticky header
│ [Search box]                │ ← Sticky search
├─────────────────────────────┤
│ Search Results              │
│ ...                         │
└─────────────────────────────┘

TAP ☰ MENU:
┌─────────────────────────────┐
│ Tamil Title             ☰   │
│ [Search box]                │
│ ▼ Acknowledgment | Search...│ ← Tabs slide down
├─────────────────────────────┤
│ Search Results              │
└─────────────────────────────┘
```

**Implementation:**
```vue
<!-- Menu button (mobile only) -->
<button
  v-if="isMobile && currentPage === 'search' && searchResults"
  @click="toggleMobileMenu"
  class="mobile-menu-button"
>
  ☰
</button>

<!-- Navigation with slide animation -->
<nav
  class="main-nav"
  :class="{ 'mobile-hidden': isMobile && !mobileMenuOpen && searchResults }"
>
  <!-- tabs -->
</nav>

<style>
@media (max-width: 968px) {
  .app-header {
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .main-nav.mobile-hidden {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
  }

  .main-nav:not(.mobile-hidden) {
    max-height: 100px;
    transition: max-height 0.3s ease;
  }

  .mobile-menu-button {
    position: absolute;
    top: 1rem;
    right: 1rem;
    font-size: 1.5rem;
    padding: 0.5rem 0.75rem;
  }
}
</style>
```

**Pros:**
- ✅ Search always accessible (sticky)
- ✅ Navigation accessible via menu button
- ✅ Header stays visible for context
- ✅ Smooth slide animation
- ✅ Saves ~50px when tabs hidden

**Cons:**
- ❌ More complex implementation
- ❌ Adds new UI element (☰ button)
- ❌ Requires managing mobile menu state

**Space saved:** ~50px (when tabs hidden)

---

### Option 3: Bottom Tab Bar (Mobile App Style)

**Behavior:**
- Move navigation tabs to **bottom of screen** on mobile
- Tabs become sticky footer
- Always accessible, no scrolling needed

**Visual:**
```
┌─────────────────────────────┐
│ Header + Search (sticky)    │
├─────────────────────────────┤
│                             │
│ Search Results              │
│ (full vertical space)       │
│                             │
├─────────────────────────────┤
│ Home | Search | About | ... │ ← Sticky bottom
└─────────────────────────────┘
```

**Implementation:**
```css
@media (max-width: 968px) {
  .app-header {
    position: sticky;
    top: 0;
  }

  .main-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 100;
    background: var(--kurinji-primary);
    padding: 0.5rem;
    display: flex;
    justify-content: space-around;
  }

  .main-nav button {
    flex: 1;
    font-size: 0.75rem;
    padding: 0.5rem;
  }
}
```

**Pros:**
- ✅ Always accessible
- ✅ Common mobile pattern (Instagram, Twitter)
- ✅ No menu button needed
- ✅ Familiar UX

**Cons:**
- ❌ Bigger design change
- ❌ Takes up bottom space
- ❌ Conflicts with mobile keyboard
- ❌ Different from desktop layout

**Space saved:** None (but navigation always accessible)

---

### Option 4: Sticky Search Only (Minimal)

**Behavior:**
- Only search box + filters stay sticky
- Everything else (title, navigation) scrolls away
- Most minimal sticky implementation

**Visual:**
```
SCROLLED DOWN:
┌─────────────────────────────┐
│ [Search box] [Filters]  ☰   │ ← Only this sticky
├─────────────────────────────┤
│ Search Results              │
│ ...                         │
└─────────────────────────────┘
```

**Implementation:**
```vue
<header class="app-header">
  <div class="header-static">
    <h1>Tamil Title</h1>
    <nav>...</nav>
  </div>

  <div class="search-sticky">
    <!-- Search box + filters -->
  </div>
</header>

<style>
@media (max-width: 968px) {
  .search-sticky {
    position: sticky;
    top: 0;
    z-index: 100;
    background: var(--kurinji-primary);
  }
}
</style>
```

**Pros:**
- ✅ Search always accessible
- ✅ Minimal change
- ✅ Maximum vertical space for results

**Cons:**
- ❌ No navigation access while scrolled
- ❌ Loses header context (title)

**Space saved:** ~80px (title + nav both scroll away)

---

## Recommendation Summary

| Option | Complexity | Space Saved | UX Impact | Best For |
|--------|-----------|-------------|-----------|----------|
| **Option 1** (Hide) | Low | 50px | Good | Quick win |
| **Option 2** (Sticky + Menu) | Medium | 50px | Excellent | Long-term solution ⭐ |
| **Option 3** (Bottom tabs) | High | 0px | Great | Mobile-first redesign |
| **Option 4** (Sticky search) | Medium | 80px | Good | Search-focused UX |

---

## Implementation Priority

**Phase 1 (Current):** ✅ COMPLETED
- Label changes (saves ~125px horizontal space)
- Auto-scroll to filters
- Auto-scroll to results

**Phase 2 (Next):** Option 1 or 2
- If quick: Option 1 (Simple Hide)
- If thorough: Option 2 (Sticky Header + Menu)

**Phase 3 (Future):** Consider Option 3
- If planning full mobile redesign

---

## Testing Considerations

**Device:** Samsung S23 (393px × 851px)

**Test Cases for Any Option:**
1. Scroll behavior (smooth, no jank)
2. Navigation accessibility
3. Search accessibility
4. Keyboard behavior (doesn't overlap sticky elements)
5. Orientation change (portrait/landscape)
6. Tab transitions
7. Deep linking (direct to About page, etc.)

---

## Related Files

- `webapp/frontend/src/MainApp.vue` - Main app component
- `webapp/frontend/src/style.css` - Mobile styles (@media queries)
- `MOBILE_TESTING.md` - Mobile testing instructions
- `MOBILE_FILTER_OPTIMIZATION.md` - Recent filter optimization (Dec 2025)

---

**Last Updated:** 2026-01-02
**Status:** Documented for future implementation
**Recommended:** Option 2 (Sticky Header + Slide-Down Menu)
