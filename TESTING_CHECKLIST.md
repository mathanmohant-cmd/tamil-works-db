# Testing Checklist for Tamil Words Database

This document outlines critical test scenarios that must be verified before any release or major change.

## Search and Sort Functionality

### 1. Collection Order Sorting (CRITICAL)
**Why this matters:** This is the most complex sorting mode and historically prone to bugs.

**Test Steps:**
1. Navigate to the search page
2. Search for a common word like "சொல்" or "அறம்"
3. Select "Collection Order" as the sort option
4. Choose "Sangam Literature" from the collection dropdown
5. Click on one of the found words to expand and see line occurrences

**Expected Result:**
- Lines should display in the exact order defined in the collection's `position_in_collection` field
- For Sangam Literature collection:
  - தொல்காப்பியம் (Tolkappiyam) - position 1 - should appear FIRST
  - நற்றிணை (Natrinai) - position 2
  - குறுந்தொகை (Kurunthokai) - position 3
  - ஐங்குறுநூறு (Ainkurunuru) - position 4
  - And so on...

**Common Bug Pattern:**
- ❌ Frontend merges results incorrectly (e.g., `[...existingResults, ...newResults]`)
- ❌ This destroys backend's sort order
- ✅ Must use ONLY the new results: `results: response.data.results`

### 2. Alphabetical Sorting
**Test Steps:**
1. Search for a word
2. Select "Alphabetical" sort
3. Expand a found word

**Expected Result:**
- Lines sorted by Tamil alphabetical order of work names
- அகநானூறு before கம்பராமாயணம் before சிலப்பதிகாரம்

### 3. Canonical Sorting
**Test Steps:**
1. Search for a word
2. Select "Traditional Canon" sort
3. Expand a found word

**Expected Result:**
- Lines sorted by `canonical_order` field from works table
- Classical works before medieval works before modern works

### 4. Chronological Sorting
**Test Steps:**
1. Search for a word
2. Select "Chronological" sort
3. Expand a found word

**Expected Result:**
- Lines sorted by estimated composition dates
- Older works before newer works

## Admin Panel - Collection Management

### 5. Drag-and-Drop Reordering
**Test Steps:**
1. Login to admin panel
2. Navigate to Collections tab
3. Select a collection with multiple works
4. Drag a work from one position to another

**Expected Result:**
- Visual feedback during drag (drag handle changes appearance)
- Work position updates immediately after drop
- Position numbers recalculate correctly
- Backend API called to persist new position
- No duplicate positions

### 6. Collection CRUD Operations
**Test Steps:**
1. Create a new collection
2. Add works to it
3. Reorder works
4. Update collection metadata
5. Delete the collection

**Expected Result:**
- All operations persist correctly
- UI updates reflect database state
- No orphaned records

## Export Functionality

### 7. Export Words to CSV
**Test Steps:**
1. Search for a word
2. Click "Export Words" button
3. Open the CSV file

**Expected Result:**
- All unique words listed
- Usage counts accurate
- Tamil characters display correctly
- File name includes search query and timestamp

### 8. Export Lines to CSV
**Test Steps:**
1. Search for a word
2. Expand a found word
3. Click "Export Lines" button
4. Open the CSV file

**Expected Result:**
- All line occurrences listed
- Full context included (work, verse, line)
- Sort order matches the UI display
- Tamil characters display correctly

## Performance Tests

### 9. Large Result Sets
**Test Steps:**
1. Search for a very common word (appears 500+ times)
2. Expand the word
3. Verify pagination works
4. Click "Load More" multiple times

**Expected Result:**
- Initial load fetches only metadata (limit=0)
- Expanding loads 100 occurrences
- "Load More" loads next 100
- No performance degradation
- Correct sort order maintained across pages

## Regression Tests (Known Bug History)

### Bug #1: Collection Sort Not Working (2025-12-18)
**Root Cause:** TWO bugs working together:
1. Frontend merged `[...existingResults, ...response.data.results]` destroying backend sort order (App.vue:~704)
2. Frontend re-sorted results alphabetically by Tamil work name in `getSortedWordOccurrences` (App.vue:~1172)

**Regression Test:**
1. Search for "சொல்" with Collection Order (Sangam Literature)
2. Expand the word
3. Verify தொல்காப்பியம் appears FIRST (not ஐங்குறுநூறு or குறுந்தொகை)
4. Export the lines and verify the CSV has தொல்காப்பியம் first

**Prevention:**
- See code comments in `App.vue:700-709` (data fetching)
- See code comments in `App.vue:1170-1176` (display function)

### Bug #2: Fallback Sort Using English Instead of Tamil
**Root Cause:** ORDER BY clause used `work_name` instead of `work_name_tamil`

**Regression Test:**
1. Search with Collection Order but for works not in the collection
2. Verify fallback sorts by Tamil names, not English

**Prevention:** All ORDER BY clauses in `database.py` use `work_name_tamil`

---

## How to Use This Checklist

**Before committing major changes:**
1. Run through relevant test scenarios
2. Document any new bugs discovered
3. Add new test cases for any new features

**Before deploying to production:**
1. Run ALL test scenarios
2. Verify on both desktop and mobile
3. Test with different browsers (Chrome, Firefox, Safari)
4. Check Tamil text rendering

**When fixing a bug:**
1. Add a regression test to this document
2. Document the root cause
3. Explain the prevention strategy
