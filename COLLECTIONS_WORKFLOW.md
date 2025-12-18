# Collections Management Workflow

## Philosophy

**Two-Step Process:**
1. **Import works** - Parsers load literary texts with metadata
2. **Organize works** - Use management utility to assign to collections and set ordering

## Why This Approach?

✅ **Flexibility** - No hardcoded assumptions about work organization
✅ **Scholarly Freedom** - You decide canonical ordering, not the code
✅ **Transparency** - Explicit management of collections vs. hidden seed data
✅ **Maintainability** - Change organization without re-importing data

## Collection Hierarchy

```
Sangam Literature (சங்க இலக்கியம்)
  └─ Pathinenmelkanakku (பதினெண்மேல்கணக்கு) - 18 Major Works
      ├─ Ettuthokai (எட்டுத்தொகை) - 8 Anthologies
      │   ├─ Natrrinai
      │   ├─ Kurunthokai
      │   ├─ Ainkurunuru
      │   ├─ Pathitrupathu
      │   ├─ Paripaadal
      │   ├─ Kalithokai
      │   ├─ Aganaanuru
      │   └─ Puranaanuru
      └─ Pathupaattu (பத்துப்பாட்டு) - 10 Idylls
          ├─ Thirumurugaatruppadai
          ├─ Porunaraatruppadai
          ├─ Sirupanaatruppadai
          ├─ Perumpanaatruppadai
          ├─ Mullaippaattu
          ├─ Madurai kanchi
          ├─ Nedunalvaadai
          ├─ Kurinchippaattu
          ├─ Pattinappaalai
          └─ Malaipadukataam

Post-Sangam Literature
  ├─ Eighteen Minor Classics (பதினெண்கீழ்க்கணக்கு)
  │   └─ (You decide which works belong here)
  └─ Five Great Epics
      └─ (You decide which works belong here)

Traditional Canon (Custom)
  └─ (Manually curate your canonical ordering)
```

## Workflow

### Step 1: Import Works

Run parsers to load texts:

```bash
# Import works without any collection assignments
python scripts/thirukkural_bulk_import.py
python scripts/sangam_bulk_import.py
python scripts/silapathikaram_bulk_import.py
python scripts/kambaramayanam_bulk_import.py
```

**Result:** Works are loaded with metadata (chronology, author, period) but NO collection assignments.

### Step 2: Seed Collections

Load pre-defined collection structure:

```bash
psql $DATABASE_URL -f sql/seed_collections.sql
```

**Result:** Collections exist but are empty (no works assigned yet).

### Step 3: Manage Collections

Use the utility to organize works:

```bash
cd scripts
python manage_collections.py <command> [options]
```

## Management Utility Commands

### View Commands

```bash
# List all collections
python manage_collections.py list-collections

# List collections by type
python manage_collections.py list-collections period
python manage_collections.py list-collections canon

# List all works
python manage_collections.py list-works

# List unassigned works
python manage_collections.py list-works --unassigned

# Show collections for a specific work
python manage_collections.py list-work-collections 20

# Show works in a specific collection
python manage_collections.py list-collection-works 100
```

### Assignment Commands

```bash
# Assign work to collection (no position)
python manage_collections.py assign <work_id> <collection_id>

# Assign with specific position
python manage_collections.py assign <work_id> <collection_id> <position>

# Assign as primary collection
python manage_collections.py assign <work_id> <collection_id> <position> --primary

# Remove work from collection
python manage_collections.py remove <work_id> <collection_id>

# Set primary collection
python manage_collections.py set-primary <work_id> <collection_id>
```

### Reordering Commands

```bash
# Interactively reorder works in a collection
python manage_collections.py reorder <collection_id>
```

## Example Workflows

### Organizing Sangam Literature

```bash
# Step 1: View unassigned works
python manage_collections.py list-works --unassigned

# Step 2: Assign Natrrinai to Ettuthokai at position 1
python manage_collections.py assign 2 10 1 --primary

# Step 3: Assign to parent collection too
python manage_collections.py assign 2 5 1    # Pathinenmelkanakku
python manage_collections.py assign 2 1 1    # Sangam Literature

# Step 4: Assign to genre collection
python manage_collections.py assign 2 54 1   # Love Poetry

# Step 5: Verify
python manage_collections.py list-work-collections 2
```

### Building Traditional Canon

```bash
# Assign works to Traditional Canon with your preferred ordering
python manage_collections.py assign 2 100 1    # Natrrinai → position 1
python manage_collections.py assign 3 100 2    # Kurunthokai → position 2
python manage_collections.py assign 4 100 3    # Ainkurunuru → position 3
# ... continue for all works

# View the canonical order
python manage_collections.py list-collection-works 100

# Reorder if needed
python manage_collections.py reorder 100
```

### Organizing Post-Sangam Works

```bash
# Thirukkural to multiple collections
python manage_collections.py assign 20 2 1 --primary        # Post-Sangam (primary)
python manage_collections.py assign 20 20 1                 # Eighteen Minor Classics
python manage_collections.py assign 20 52 1                 # Ethical Literature
python manage_collections.py assign 20 100 20               # Traditional Canon position 20

# Silapathikaram
python manage_collections.py assign 21 2 2 --primary        # Post-Sangam (primary)
python manage_collections.py assign 21 21 1                 # Five Great Epics
python manage_collections.py assign 21 50 1                 # Epic Poetry genre
python manage_collections.py assign 21 100 21               # Traditional Canon position 21

# Verify
python manage_collections.py list-work-collections 20
python manage_collections.py list-work-collections 21
```

## Collection IDs Reference

### Periods
- 1 - Sangam Literature
- 2 - Post-Sangam Literature
- 3 - Medieval Literature
- 4 - Modern Literature

### Sangam Sub-Collections
- 5 - Pathinenmelkanakku (18 Major Works)
- 10 - Ettuthokai (8 Anthologies)
- 11 - Pathupaattu (10 Idylls)

### Post-Sangam Sub-Collections
- 20 - Eighteen Minor Classics
- 21 - Five Great Epics

### Medieval Sub-Collections
- 30 - Shaiva Literature
- 31 - Vaishnava Literature
- 32 - Jaina Literature
- 33 - Buddhist Literature
- 34 - Medieval Epics

### Genres (Cross-Period)
- 50 - Epic Poetry
- 51 - Devotional Literature
- 52 - Ethical Literature
- 53 - Grammar & Linguistics
- 54 - Love Poetry
- 55 - Heroic Poetry

### Custom/Special
- 100 - Traditional Canon (manually curated)
- 101 - Tolkappiyam Tradition

## Tips

### Finding Work IDs

```bash
# List all works with IDs
python manage_collections.py list-works

# Or query directly
psql $DATABASE_URL -c "SELECT work_id, work_name FROM works ORDER BY work_name;"
```

### Batch Assignment

Create a SQL script:

```sql
-- assign_sangam_works.sql
-- Assign all Sangam works to Pathinenmelkanakku collection

INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary) VALUES
-- Ettuthokai works
((SELECT work_id FROM works WHERE work_name = 'Natrrinai'), 10, 1, TRUE),
((SELECT work_id FROM works WHERE work_name = 'Kurunthokai'), 10, 2, TRUE),
-- ... etc
ON CONFLICT (work_id, collection_id) DO NOTHING;
```

Run it:
```bash
psql $DATABASE_URL -f scripts/assign_sangam_works.sql
```

### Checking Canonical Ordering

```bash
# View canonical order via API
curl http://localhost:8000/works?sort_by=canonical

# Or query directly
psql $DATABASE_URL -c "
SELECT w.work_name, wc.position_in_collection
FROM works w
JOIN work_collections wc ON w.work_id = wc.work_id
WHERE wc.collection_id = 100
ORDER BY wc.position_in_collection;
"
```

## Best Practices

### 1. Use Primary Collections Consistently
- Each work should have ONE primary collection
- Primary collection determines default display grouping
- Use `--primary` flag when assigning

### 2. Position Numbering
- Use sequential numbers (1, 2, 3...) for canonical ordering
- Leave gaps (10, 20, 30...) for future insertions
- NULL positions are acceptable for genre collections

### 3. Document Your Choices
- Keep notes on why you chose specific orderings
- Reference scholarly sources for canonical sequences
- Update `CHRONOLOGY_PROPOSAL.md` with your decisions

### 4. Hierarchical Assignments
- Assign to both parent and child collections
- Example: Natrrinai → Ettuthokai → Pathinenmelkanakku → Sangam Literature
- This enables queries at multiple granularities

### 5. Multiple Collection Memberships
- Don't hesitate to assign works to multiple collections
- Example: Thirukkural in Post-Sangam + Ethical + Traditional Canon
- Enables cross-cutting queries and browse patterns

## Troubleshooting

### Work not appearing in canonical order?
```bash
# Check if assigned to Traditional Canon (ID=100)
python manage_collections.py list-work-collections <work_id>

# Assign if missing
python manage_collections.py assign <work_id> 100 <position>
```

### Position conflicts?
```bash
# View current ordering
python manage_collections.py list-collection-works 100

# Reorder interactively
python manage_collections.py reorder 100
```

### Lost primary collection?
```bash
# Set primary collection
python manage_collections.py set-primary <work_id> <collection_id>
```

## Future Enhancements

Consider building:
- Web UI for collection management
- Import/export of collection configurations
- Version control for collection schemes
- Collection templates for common organizational patterns
- Bulk operations (assign all works matching criteria)

## Summary

✅ **Step 1:** Import works with parsers
✅ **Step 2:** Seed collections structure
✅ **Step 3:** Organize using `manage_collections.py`
✅ **Flexible:** Change organization anytime without re-importing
✅ **Transparent:** Explicit management, no hidden assumptions
