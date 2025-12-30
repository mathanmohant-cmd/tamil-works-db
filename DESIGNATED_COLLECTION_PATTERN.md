# Designated Collection Pattern

## Overview

The designated collection pattern provides a canonical hierarchy for organizing Tamil literary works in the filter UI. This document captures the design decisions and implementation details.

## Design Decision History

### Initial Approach (Considered but Rejected)
- Create `app_settings` table to store `designated_filter_collection_id`
- Backend reads from database using `get_app_setting()` method
- **Rejected because**: Unnecessarily complex for a single, well-known value

### Final Approach (Implemented 2025-12-29)
- Use collection_id = 1 as a **well-known, hardcoded** designated collection
- Create this collection automatically in `sql/complete_setup.sql`
- Backend endpoint returns hardcoded `{"collection_id": 1}`
- **Benefits**: Simpler, self-documenting, no extra table needed

## Implementation Details

### 1. SQL Schema (sql/complete_setup.sql)

```sql
-- Insert designated filter collection (Tamil Literature root)
-- This collection serves as the root for the filter UI tree
-- User can build the hierarchy under this collection via Admin UI
INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order)
VALUES (1, 'Tamil Literature', 'தமிழ் இலக்கியம்', 'canon', 'Root collection for canonical Tamil Literature hierarchy - used by filter UI', NULL, 1)
ON CONFLICT (collection_id) DO NOTHING;

-- Reset sequence to prevent conflicts (collection_id is SERIAL)
SELECT setval('collections_collection_id_seq', (SELECT COALESCE(MAX(collection_id), 0) + 1 FROM collections), false);
```

**Location**: Lines 87-95 in `sql/complete_setup.sql`

**Why ON CONFLICT DO NOTHING?**
- Prevents errors if collection_id = 1 already exists
- Allows schema to be re-run safely
- Idempotent behavior

**Why reset sequence?**
- collection_id is SERIAL, meaning auto-incrementing
- We manually inserted ID=1, so sequence needs to start from 2+
- Prevents future collections from conflicting with ID=1

### 2. Backend Endpoint (webapp/backend/main.py)

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

**Location**: Lines 287-295 in `webapp/backend/main.py`

**Design Choice**: Hardcoded return value
- No database query needed (faster)
- Collection ID=1 is guaranteed by schema
- Simple and maintainable

### 3. Frontend Integration (webapp/frontend/src/MainApp.vue)

```javascript
// Load designated collection on mount
const designatedCollectionId = ref(null)

onMounted(async () => {
  // Fetch designated collection ID from backend
  const settingsResponse = await axios.get(`${API_BASE_URL}/settings/designated_filter_collection`)
  designatedCollectionId.value = settingsResponse.data.collection_id

  // ... pass to CollectionTree component
})
```

**Component Usage**:
```vue
<CollectionTree
  ref="collectionTreeRef"
  :selected-works="selectedWorks"
  :root-collection-id="designatedCollectionId"
  @update:selectedWorks="handleCollectionSelection"
/>
```

### 4. Collection Tree Component (webapp/frontend/src/components/CollectionTree.vue)

The component accepts `rootCollectionId` prop and filters the collection tree:

```javascript
const loadCollectionTree = async () => {
  let url = `${API_BASE_URL}/collections/tree`
  if (props.rootCollectionId) {
    url += `?root=${props.rootCollectionId}`  // Fetch only subtree under ID=1
  }
  const response = await axios.get(url)
  collectionTree.value = response.data

  // Auto-expand designated collection
  if (props.rootCollectionId && response.data.length > 0) {
    expandedNodes.value.add(response.data[0].collection_id)
  }
}
```

**Backend Support** (`webapp/backend/database.py`):
```python
def get_collection_tree(self, root_collection_id: int = None) -> List[Dict]:
    # ... fetch all collections and build tree ...

    # If root_collection_id specified, return only that subtree
    if root_collection_id and root_collection_id in collection_map:
        return [collection_map[root_collection_id]]

    return root_collections
```

## User Workflow

### Building the Tamil Literature Hierarchy

1. **Schema creates root collection automatically**
   - When `complete_setup.sql` runs, collection_id=1 is created
   - Name: "Tamil Literature" / "தமிழ் இலக்கியம்"
   - Type: "canon"
   - Parent: NULL (top-level)

2. **User builds hierarchy via Admin UI** (http://localhost:5173/admin)
   - Create child collections:
     - "Sangam Literature" (parent_id=1, sort_order=1)
     - "Eighteen Lesser Texts" (parent_id=1, sort_order=2)
     - "Five Great Epics" (parent_id=1, sort_order=3)
     - "Devotional Literature" (parent_id=1, sort_order=4)
   - Nest existing collections under appropriate parents:
     - Collection 321 (Thirumurai) → parent_id = Devotional Literature
     - Collection 322 (Naalayira Divya Prabandham) → parent_id = Devotional Literature
     - Collection 323 (Standalone Devotional) → parent_id = Devotional Literature
   - Add works to leaf collections via drag-and-drop
   - Set sort_order to maintain traditional ordering

3. **Filter UI displays hierarchy automatically**
   - Frontend fetches collection_id=1 from `/settings/designated_filter_collection`
   - CollectionTree component loads tree starting from ID=1
   - Users can expand/collapse collections and select works

## Why Manual Hierarchy Building?

**Considered**: Auto-generating collection hierarchy from metadata

**Chosen**: Manual building via Admin UI

**Rationale**:
- ✅ User has full control over structure
- ✅ Can adjust as literary scholarship evolves
- ✅ Follows established literary tradition accurately
- ✅ Leverages existing Admin drag-and-drop functionality
- ✅ No code changes needed to reorganize
- ✅ Different scholars may have different organizational preferences

## Collection ID Conventions

| Collection ID | Name | Purpose |
|---------------|------|---------|
| 1 | Tamil Literature (தமிழ் இலக்கியம்) | **Designated filter collection** - root for UI hierarchy |
| 321 | Thirumurai (திருமுறை) | 14 Shaivite devotional works |
| 322 | Naalayira Divya Prabandham | 24 Vaishnavite devotional works |
| 323 | Devotional Literature | Standalone devotional works |
| 2+ | User-created | Child collections under Tamil Literature |

## Files Modified

1. **sql/complete_setup.sql** (lines 87-95)
   - Added INSERT for collection_id=1
   - Added sequence reset

2. **webapp/backend/main.py** (lines 287-295)
   - Simplified endpoint to return hardcoded value
   - Removed dependency on config.py

3. **webapp/backend/config.py**
   - **DELETED** - no longer needed

4. **webapp/frontend/src/MainApp.vue**
   - Replaced AccordionFilter with CollectionTree
   - Added designatedCollectionId state variable
   - Loads designated collection on mount

5. **webapp/frontend/src/components/CollectionTree.vue**
   - Added rootCollectionId prop
   - Filters tree to show only designated subtree

6. **webapp/frontend/src/components/TreeNode.vue**
   - Added mobile-optimized styles (44px touch targets)

## Testing

### Verify designated collection exists:
```sql
SELECT * FROM collections WHERE collection_id = 1;
```

Expected result:
```
collection_id | collection_name   | collection_name_tamil | collection_type | parent_collection_id | sort_order
--------------+-------------------+----------------------+----------------+---------------------+-----------
1             | Tamil Literature  | தமிழ் இலக்கியம்      | canon          | NULL                | 1
```

### Verify endpoint returns correct value:
```bash
curl http://localhost:8000/settings/designated_filter_collection
```

Expected response:
```json
{"collection_id": 1}
```

### Verify frontend loads tree correctly:
1. Navigate to http://localhost:5173
2. Open browser DevTools Network tab
3. Look for request to `/collections/tree?root=1`
4. Filter panel should display "Tamil Literature" as root

## Future Enhancements

### Possible (but not needed now):
- **Multiple designated collections**: e.g., different hierarchies for different scholarly traditions
- **Collection visibility flags**: Hide certain collections from filter UI
- **Collection metadata**: Store additional info like description, image, external links
- **Collection templates**: Pre-defined hierarchies for quick setup

### Not recommended:
- **Auto-generated hierarchies**: Loses user control and flexibility
- **Database-driven collection ID**: Adds complexity without benefit
- **Multiple filter roots**: Confusing UX, single canonical hierarchy is clearer

## Lessons Learned

1. **Simpler is better**: Hardcoded well-known ID beats configuration table
2. **Schema-driven is reliable**: Create essential data in schema, not via app initialization
3. **Manual > Automatic**: User control trumps automatic generation for scholarly content
4. **ON CONFLICT DO NOTHING**: Makes SQL idempotent and safe to re-run
5. **Sequence management**: Always reset SERIAL sequences after manual inserts

## Related Documentation

- `CLAUDE.md` - Project overview and architecture (includes designated collection pattern)
- `sql/complete_setup.sql` - Schema definition with designated collection INSERT
- `webapp/backend/main.py` - Backend endpoint implementation
- Plan file: `C:\Users\t_mat\.claude\plans\velvet-chasing-glade.md` - Full implementation plan

---

**Last Updated**: 2025-12-29
**Implementation Status**: ✅ Complete
