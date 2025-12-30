# Plan Decisions: Designated Collection for Filter UI

**Date**: 2025-12-29
**Status**: ✅ Implemented
**Plan File**: `C:\Users\t_mat\.claude\plans\velvet-chasing-glade.md`

## Summary

Implemented a simplified approach for designating a collection to serve as the root for the filter UI hierarchy, allowing users to manually build a canonical Tamil Literature collection.

## Key Design Decisions

### Decision 1: Manual vs Auto-Generated Hierarchy

**Question**: Should the Tamil Literature collection hierarchy be auto-generated or manually built?

**Options Considered**:
1. **Auto-generate** from metadata - parse work metadata and programmatically build hierarchy
2. **Manual building** via Admin UI - user creates hierarchy using drag-and-drop

**Decision**: ✅ Manual building via Admin UI

**Rationale**:
- ✅ User has full control over structure
- ✅ Can adjust as literary scholarship evolves
- ✅ Follows established literary tradition accurately
- ✅ Leverages existing Admin drag-and-drop functionality
- ✅ No code changes needed to reorganize
- ✅ Different scholars may have different organizational preferences

### Decision 2: How to Store Designated Collection ID

**Question**: How should we store and retrieve the designated collection ID?

**Options Considered**:

1. **Environment variable** (FILTER_COLLECTION_ID)
   - ❌ Not version controlled
   - ❌ Requires deployment coordination
   - ❌ Different across environments

2. **Config file** (webapp/backend/config.py)
   - ❌ Separate file to maintain
   - ❌ Must update code to change collection
   - ❌ Not schema-driven

3. **Database table** (app_settings)
   - ❌ Extra table for single value
   - ❌ Additional query overhead
   - ❌ More complex than needed

4. **Hardcoded well-known ID** (collection_id = 1) ✅ CHOSEN
   - ✅ Simpler - no extra table
   - ✅ Self-documenting via collection name/description
   - ✅ Schema-driven - created in complete_setup.sql
   - ✅ Version controlled
   - ✅ No database query needed
   - ✅ Guaranteed to exist

**Decision**: ✅ Hardcoded collection_id = 1

**User Feedback**:
> "wont creating an entry in collection table be enough. do we need app settings tables. seems unncessary"

**Outcome**: Simplified implementation - no app_settings table needed

### Decision 3: Frontend Filter Component

**Question**: Which component should display the collection filter?

**Options Considered**:
1. **AccordionFilter.vue** (existing) - Flattens hierarchy, skips pure containers
2. **CollectionTree.vue** (existing but unused) - Full hierarchical tree with expand/collapse

**Decision**: ✅ Replace AccordionFilter with CollectionTree

**Rationale**:
- ✅ CollectionTree preserves full hierarchy
- ✅ Mobile-optimized with touch targets
- ✅ Better UX for deep nesting
- ✅ Already exists in codebase
- ✅ Supports expand/collapse functionality

### Decision 4: Admin UI Enhancements

**Question**: Should we enhance Admin UI to better support multi-level hierarchy building?

**Options Considered**:
1. **Multi-level tree view** - Replace 2-level view with full recursive tree
2. **Bulk work assignment** - Add multiple works to collection at once
3. **Collection templates** - Pre-defined hierarchies for quick setup

**Decision**: ⏸️ Optional - Not required for MVP

**Rationale**:
- Current Admin UI already supports:
  - ✅ Drag-and-drop reordering
  - ✅ Create/edit collections with parent_collection_id
  - ✅ Add/remove works
- Enhancements are nice-to-have, not essential
- User can build hierarchy with existing tools

## Implementation Approach

### Phase 1: SQL Schema (✅ Complete)

**File**: `sql/complete_setup.sql`

```sql
-- Insert designated filter collection (Tamil Literature root)
INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order)
VALUES (1, 'Tamil Literature', 'தமிழ் இலக்கியம்', 'canon', 'Root collection for canonical Tamil Literature hierarchy - used by filter UI', NULL, 1)
ON CONFLICT (collection_id) DO NOTHING;

-- Reset sequence to prevent conflicts
SELECT setval('collections_collection_id_seq', (SELECT COALESCE(MAX(collection_id), 0) + 1 FROM collections), false);
```

**Key Decisions**:
- ✅ Use `ON CONFLICT DO NOTHING` for idempotency
- ✅ Reset sequence after manual insert to avoid ID conflicts
- ✅ Include descriptive text in `description` field

### Phase 2: Backend Endpoint (✅ Complete)

**File**: `webapp/backend/main.py`

```python
@app.get("/settings/designated_filter_collection")
def get_designated_filter_collection():
    """
    Get the designated collection ID for the filter UI

    Returns collection_id = 1 (Tamil Literature root collection)
    This collection is created by the schema and serves as the root for the filter hierarchy
    """
    return {"collection_id": 1}
```

**Key Decisions**:
- ✅ Hardcoded return value (no database query)
- ✅ Simplified from original config.py approach
- ✅ Deleted config.py file (no longer needed)

### Phase 3: Frontend Integration (✅ Complete - Previous Session)

**File**: `webapp/frontend/src/MainApp.vue`

**Changes**:
1. Replaced AccordionFilter with CollectionTree component
2. Added `designatedCollectionId` state variable
3. Load designated collection on mount from backend endpoint
4. Pass `rootCollectionId` prop to CollectionTree

**File**: `webapp/frontend/src/components/CollectionTree.vue`

**Changes**:
1. Added `rootCollectionId` prop
2. Modified `loadCollectionTree()` to support `?root=N` parameter
3. Auto-expand designated collection when loaded

**File**: `webapp/frontend/src/components/TreeNode.vue`

**Changes**:
1. Added mobile-optimized styles (44px touch targets)
2. Reduced indentation on mobile (0.75rem)
3. Larger checkboxes (22px) for touch

### Phase 4: Backend Support (✅ Complete - Previous Session)

**File**: `webapp/backend/main.py`

**Changes**:
1. Updated `/collections/tree` to accept optional `root` query parameter
2. Returns only subtree when `root` specified

**File**: `webapp/backend/database.py`

**Changes**:
1. Updated `get_collection_tree()` to support `root_collection_id` parameter
2. Returns filtered subtree when root specified

## Files Modified

### New Files Created:
1. ✅ `DESIGNATED_COLLECTION_PATTERN.md` - Full documentation of pattern
2. ✅ `PLAN_DECISIONS_2025-12-29.md` - This file

### Files Modified:
1. ✅ `sql/complete_setup.sql` - Added designated collection INSERT
2. ✅ `webapp/backend/main.py` - Simplified settings endpoint
3. ✅ `webapp/frontend/src/MainApp.vue` - Replaced AccordionFilter with CollectionTree
4. ✅ `webapp/frontend/src/components/CollectionTree.vue` - Added rootCollectionId support
5. ✅ `webapp/frontend/src/components/TreeNode.vue` - Mobile optimizations
6. ✅ `webapp/backend/database.py` - Updated get_collection_tree()
7. ✅ `CLAUDE.md` - Added designated collection documentation
8. ✅ `COLLECTION_IDS.md` - Added collection_id = 1 reference

### Files Deleted:
1. ✅ `webapp/backend/config.py` - No longer needed (simplified approach)

## Testing Checklist

- [ ] Run `setup_railway_db.py` to create collection_id = 1
- [ ] Verify collection exists: `SELECT * FROM collections WHERE collection_id = 1;`
- [ ] Test backend endpoint: `curl http://localhost:8000/settings/designated_filter_collection`
- [ ] Build hierarchy via Admin UI:
  - [ ] Create child collections under collection_id = 1
  - [ ] Edit collections 321, 322, 323 to set parent_collection_id
  - [ ] Add works to leaf collections
  - [ ] Set sort_order for traditional ordering
- [ ] Test frontend filter:
  - [ ] Verify CollectionTree loads designated collection
  - [ ] Test expand/collapse functionality
  - [ ] Test work selection (parent selects all descendants)
  - [ ] Test on mobile (44px touch targets, reduced indentation)

## Benefits Achieved

✅ **Simpler**: No app_settings table - just well-known collection ID
✅ **Schema-driven**: Collection created automatically during setup
✅ **Self-documenting**: Collection name/description explain purpose
✅ **Version controlled**: Changes tracked in SQL schema
✅ **User control**: Hierarchy built manually via Admin UI
✅ **Traditional order**: Follows established Tamil literature organization
✅ **Mobile optimized**: Touch-friendly UI with proper spacing
✅ **Leverages existing code**: Uses CollectionTree/TreeNode components
✅ **No data migration**: Import scripts continue working as-is

## Next Steps for User

1. **Run database migration**
   ```bash
   python scripts/setup_railway_db.py
   ```

2. **Verify collection_id = 1 exists**
   ```sql
   SELECT * FROM collections WHERE collection_id = 1;
   ```

3. **Build hierarchy via Admin UI** (http://localhost:5173/admin)
   - Create child collections (Sangam, Devotional, etc.)
   - Set parent_collection_id for existing collections (321, 322, 323)
   - Add works using drag-and-drop
   - Set sort_order for traditional ordering

4. **Test filter UI** (http://localhost:5173)
   - Verify Tamil Literature appears as root
   - Test expand/collapse
   - Test work selection
   - Test on mobile device

## References

- **Full Implementation Plan**: `C:\Users\t_mat\.claude\plans\velvet-chasing-glade.md`
- **Pattern Documentation**: `DESIGNATED_COLLECTION_PATTERN.md`
- **Collection ID Reference**: `COLLECTION_IDS.md`
- **Project Documentation**: `CLAUDE.md`

---

**Implementation Date**: 2025-12-29
**Implemented By**: Claude Code (Sonnet 4.5)
**User Confirmation**: ✅ Approved simplified approach (no app_settings table)
