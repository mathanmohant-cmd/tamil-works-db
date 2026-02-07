# Frontend Structure Guide

**Last Updated:** 2026-02-07

This document describes the feature-based architecture of the Vue.js frontend. **Read this before making any changes to frontend files.**

---

## Directory Structure

```
src/
├── App.vue                     [Root component - simple router-view wrapper]
├── main.js                     [Entry point - creates Vue app]
├── router.js                   [Central routing - all route definitions]
├── api.js                      [Axios HTTP client with auto API URL detection]
├── style.css                   [Global CSS styles]
│
├── layouts/                    [Shared layout wrappers]
│   └── AppLayout.vue           [Main layout: header + content + footer]
│
├── composables/                [Shared reactive state & utilities]
│   ├── useSearchState.js       [Search state management (singleton)]
│   ├── useFilterState.js       [Work/collection filter state]
│   ├── useUserRole.js          [User authentication state]
│   ├── useCollectionState.js   [Collection data management]
│   ├── useStats.js             [Database statistics]
│   ├── useTransliteration.js   [Transliteration utilities]
│   ├── useAI4BharatTransliteration.js
│   └── useAnchorScroll.js      [Smooth anchor scrolling]
│
├── shared/                     [Reusable components used across features]
│   ├── AppHeaderEnhanced.vue   [Header with search + user menu]
│   ├── AppFooter.vue           [Footer with links]
│   ├── CollectionTree.vue      [Hierarchical collection filter]
│   └── NestedCollectionItem.vue [Recursive tree node]
│
├── features/                   [Feature-based organization]
│   ├── search/                 [Word search feature]
│   │   ├── pages/
│   │   │   ├── SearchPage.vue
│   │   │   └── SearchResultsPage.vue
│   │   └── components/
│   │       ├── SearchControls.vue
│   │       └── SearchResults.vue
│   │
│   ├── works/                  [Works browser feature]
│   │   ├── pages/
│   │   │   ├── WorksBrowser.vue
│   │   │   └── VerseView.vue
│   │   └── components/
│   │       ├── WorksList.vue
│   │       ├── WorkDetail.vue
│   │       ├── SectionView.vue
│   │       └── SectionTreeNode.vue
│   │
│   ├── help/                   [Help & documentation]
│   │   └── pages/
│   │       ├── HelpPage.vue
│   │       ├── UnderstandingThisToolPage.vue
│   │       ├── WordSegmentationPage.vue
│   │       └── TransliterationGuidePage.vue
│   │
│   ├── about/                  [About & story pages]
│   │   └── pages/
│   │       ├── WelcomePage.vue
│   │       ├── Home.vue (Acknowledgment)
│   │       ├── TheStoryBehind.vue
│   │       ├── OurJourney.vue
│   │       ├── OurInspiration.vue
│   │       ├── AboutUsPage.vue
│   │       ├── ContactUsPage.vue
│   │       └── DisclaimerPage.vue
│   │
│   ├── admin/                  [Admin panel]
│   │   └── pages/
│   │       └── AdminPage.vue (consolidated with Admin.vue)
│   │
│   └── insights/               [Data insights]
│       └── pages/
│           └── InsightsPage.vue
│
└── assets/                     [Static assets]
    └── styles/
        └── help-pages.css
```

---

## Import Path Rules

### From Feature Pages (`features/*/pages/*.vue`)

| Import Type | Pattern | Example |
|-------------|---------|---------|
| Composables | `../../../composables/` | `import { useSearchState } from '../../../composables/useSearchState.js'` |
| API Client | `../../../api.js` | `import api from '../../../api.js'` |
| Shared Components | `../../../shared/` | `import CollectionTree from '../../../shared/CollectionTree.vue'` |
| Feature Components | `../components/` | `import SearchControls from '../components/SearchControls.vue'` |
| Other Features | `../../other-feature/` | `import VerseView from '../../works/pages/VerseView.vue'` |
| CSS Assets | `../../../assets/` | `@import '../../../assets/styles/help-pages.css'` |

### From Feature Components (`features/*/components/*.vue`)

| Import Type | Pattern | Example |
|-------------|---------|---------|
| Composables | `../../../composables/` | `import { useCollectionState } from '../../../composables/useCollectionState.js'` |
| API Client | `../../../api.js` | `import api from '../../../api.js'` |
| Shared Components | `../../../shared/` | `import CollectionTree from '../../../shared/CollectionTree.vue'` |
| Sibling Components | `./` | `import SectionTreeNode from './SectionTreeNode.vue'` |

### From Shared Components (`shared/*.vue`)

| Import Type | Pattern | Example |
|-------------|---------|---------|
| Composables | `../composables/` | `import { useUserRole } from '../composables/useUserRole.js'` |
| API Client | `../api.js` | `import api from '../api.js'` |
| Other Shared | `./` | `import NestedCollectionItem from './NestedCollectionItem.vue'` |

### From Layouts (`layouts/*.vue`)

| Import Type | Pattern | Example |
|-------------|---------|---------|
| Shared Components | `../shared/` | `import AppHeader from '../shared/AppHeaderEnhanced.vue'` |

### From Router (`router.js`)

| Import Type | Pattern | Example |
|-------------|---------|---------|
| Layouts | `./layouts/` | `import AppLayout from './layouts/AppLayout.vue'` |
| Feature Pages | `./features/*/pages/` | `import SearchPage from './features/search/pages/SearchPage.vue'` |
| Feature Components | `./features/*/components/` | `import WorksList from './features/works/components/WorksList.vue'` |
| Composables | `./composables/` | `import { useUserRole } from './composables/useUserRole.js'` |

---

## Key Architectural Decisions

### 1. Feature-Based Organization
- **Why:** Clear boundaries between features, easier to find code, scales well
- **Rule:** Each feature contains its own pages and components
- **Shared vs Feature-Specific:**
  - **Shared** (`/shared`): Used by multiple features or the layout (AppHeader, AppFooter, CollectionTree)
  - **Feature-Specific** (`/features/*/components`): Only used within that feature

### 2. Router-Based Navigation
- Single `router.js` file with all route definitions
- Route-level components in `features/*/pages/`
- Supporting components in `features/*/components/`

### 3. State Management via Composables
- No Vuex/Pinia - using Vue 3 Composition API composables
- Singleton pattern for shared state (e.g., `useSearchState`)
- LocalStorage persistence for filters (`useFilterState`)
- SessionStorage for user auth (`useUserRole`)

### 4. No Auto-Import Magic
- All imports must be explicit with full relative paths
- No path aliases configured (considered for future)
- This makes it clear where code comes from

---

## Common Tasks

### Adding a New Page to an Existing Feature

1. Create file in `features/{feature}/pages/NewPage.vue`
2. Import in `router.js`: `import NewPage from './features/{feature}/pages/NewPage.vue'`
3. Add route definition in the appropriate section
4. Use import pattern: `../../../` to reach root-level folders

### Adding a New Feature

1. Create folder structure:
   ```bash
   mkdir -p features/new-feature/pages
   mkdir -p features/new-feature/components
   ```
2. Add pages/components following existing patterns
3. Update `router.js` with new routes
4. Follow import path rules from the table above

### Adding a Shared Component

1. Create file in `shared/NewComponent.vue`
2. Import from features: `import NewComponent from '../../../shared/NewComponent.vue'`
3. Import from layouts: `import NewComponent from '../shared/NewComponent.vue'`

### Moving a Component

**IMPORTANT:** Always update import paths after moving files!

1. Move the file using `mv` or IDE refactor
2. Update **all** imports in the moved file (composables, api, shared, other features)
3. Search for imports of the moved file: `grep -r "from.*OldPath" src/`
4. Update all references to the new path
5. Test the application - check browser console for errors

---

## Common Pitfalls

### ❌ Wrong: Incorrect import depth
```javascript
// From features/search/pages/SearchPage.vue
import { useSearchState } from '../composables/useSearchState.js'  // WRONG! Missing one ../
```

### ✅ Correct: Proper import depth
```javascript
// From features/search/pages/SearchPage.vue
import { useSearchState } from '../../../composables/useSearchState.js'  // Correct!
```

### ❌ Wrong: Forgetting to update CSS imports
```vue
<!-- In features/help/pages/WordSegmentationPage.vue -->
<style scoped>
@import '../assets/styles/help-pages.css';  /* WRONG! Missing two ../ */
</style>
```

### ✅ Correct: Proper CSS import depth
```vue
<!-- In features/help/pages/WordSegmentationPage.vue -->
<style scoped>
@import '../../../assets/styles/help-pages.css';  /* Correct! */
</style>
```

### ❌ Wrong: Using components folder
```javascript
// DON'T create new files here - these folders don't exist anymore!
import Something from './components/Something.vue'
```

### ✅ Correct: Use feature-based structure
```javascript
// Create in features/{feature}/components/ or shared/
import Something from './features/search/components/Something.vue'
```

---

## Verification Checklist

After making structural changes, verify:

- [ ] `npm run dev` starts without errors
- [ ] No `Failed to resolve import` errors in console
- [ ] No `ENOENT: no such file or directory` errors
- [ ] All routes load correctly
- [ ] Search functionality works
- [ ] Works browser navigation works
- [ ] Admin panel loads
- [ ] Help pages load with correct styling

### Quick Check Commands
```bash
# Find any remaining wrong import paths (should return nothing)
grep -r "from '\.\./composables" src/features/
grep -r "from '\.\./api" src/features/
grep -r "@import '\.\./assets" src/features/

# Verify correct patterns exist
grep -r "from '\.\./\.\./\.\./composables" src/features/ | wc -l  # Should be > 0
grep -r "from '\.\./\.\./\.\./api" src/features/ | wc -l  # Should be > 0
```

---

## Historical Context

**Date:** 2026-02-07
**Change:** Major frontend reorganization from mixed structure to feature-based architecture

**Before:**
- Files scattered at root level (Home.vue, OurJourney.vue, VerseView.vue, etc.)
- Mixed `/pages` and `/components` folders
- Difficult to find feature-specific code

**After:**
- Clean feature-based structure with `/features` folder
- Shared components in `/shared`
- Clear separation between features, shared code, and layouts

**Files Deleted:** 9 unused Vue files
**Files Moved:** 30 Vue files
**Import Paths Updated:** 12+ files + router.js

**Benefits Achieved:**
- Clear feature boundaries
- Easier to find code by feature
- Scales well for adding new features
- Consistent import patterns throughout

---

## Future Considerations

### Path Aliases (Not Implemented Yet)
Could add to `vite.config.js` to simplify imports:
```javascript
resolve: {
  alias: {
    '@': '/src',
    '@shared': '/src/shared',
    '@composables': '/src/composables',
    '@features': '/src/features'
  }
}
```

Then imports become:
```javascript
import { useSearchState } from '@composables/useSearchState.js'
import CollectionTree from '@shared/CollectionTree.vue'
```

**Pros:** Shorter, cleaner imports
**Cons:** Adds abstraction, might confuse new developers
**Decision:** Keep explicit relative paths for now, revisit if team grows

---

## Questions?

If you're unsure about where to put a file or how to import it:

1. Check this document first
2. Look at similar existing files in the same feature
3. Follow the import path tables above
4. Test thoroughly after making changes

**Remember:** When in doubt, follow the existing patterns in the codebase!
