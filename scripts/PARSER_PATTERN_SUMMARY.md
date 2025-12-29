# Devotional Literature Parser Pattern

## Standard Pattern for All Parsers

Each devotional literature parser follows this self-contained pattern:

### ✅ What Each Parser DOES:

1. **Creates its OWN collection** (not parent collections)
2. **Sets default section type** to `"Chapter/பகுதி"` (not "Collection/தொகுப்பு")
3. **Links works to collection** via `work_collections` table
4. **Sets primary_collection_id** in works table (for backward compatibility)
5. **Uses 2-phase bulk COPY** for performance

### ❌ What Each Parser DOES NOT DO:

1. **Does NOT create Thirumurai collection (321)** - will be created by master script
2. **Does NOT create other parent collections** - only creates its own
3. **Does NOT set parent_collection_id** in metadata (no hierarchy until master script)

---

## Collection ID Assignments

| File(s) | Parser Script | Collection ID | Collection Name |
|---------|--------------|---------------|-----------------|
| 1-7 | `devaram_bulk_import.py` | 3211 | Devaram (தேவாரம்) |
| 8.1 | `thiruvasagam_bulk_import.py` | 3218 | Thiruvasagam (திருவாசகம்) |
| 8.2 | `thirukovayar_bulk_import.py` | 3219 | Thirukovayar |
| 9 | `thiruvisaippa_bulk_import.py` | 3220 | Thiruvisaippa |
| 10 | `thirumanthiram_bulk_import.py` | 3221 | Thirumanthiram |
| 11 | `saiva_prabandha_malai_bulk_import.py` | 3222 | Saiva Prabandha Malai |
| 12 | `periya_puranam_bulk_import.py` | 3223 | Periya Puranam |
| 13-16 | `naalayira_divya_prabandham_bulk_import.py` | 322 | Naalayira Divya Prabandham |
| 17 | `thiruppugazh_bulk_import.py` | 323 | Thiruppugazh |
| 18 | `thembavani_bulk_import.py` | 324 | Thembavani |
| 19 | `seerapuranam_bulk_import.py` | 325 | Seerapuranam |

**Parent Collection (created by master script):**
- Collection 321: Thirumurai (திருமுறை) - Parent of 3211-3223

---

## Implementation Checklist

For each new parser, ensure:

### 1. Collection Creation
```python
def ensure_collection_exists(self):
    """Ensure the [Work] collection exists"""
    self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = XXXX")
    result = self.cursor.fetchone()

    if not result:
        print("  Creating [Work] collection (XXXX)...")
        self.cursor.execute("""
            INSERT INTO collections (collection_id, collection_name, collection_name_tamil,
                                   collection_type, description, sort_order)
            VALUES (XXXX, '[Work Name]', '[தமிழ் பெயர்]', 'devotional',
                    'Description', XXXX)
        """)
        self.conn.commit()
```

### 2. Default Section Type
```python
def _get_or_create_section_id(self, work_id):
    self.sections.append({
        'section_id': section_id,
        'work_id': work_id,
        'parent_section_id': None,
        'level_type': 'Chapter',           # ✅ Not "Collection"
        'level_type_tamil': 'பகுதி',       # ✅ Not "தொகுப்பு"
        'section_number': 1,
        'section_name': None,
        'section_name_tamil': None,
        'sort_order': 1,
        'metadata': {}
    })
```

### 3. Work Metadata
```python
work_metadata = {
    'tradition': 'Shaivite',  # or 'Vaishnavite', 'Christian', 'Islamic'
    'collection_id': XXXX,     # Own collection ID
    'collection_name': '[Work Name]',
    'collection_name_tamil': '[தமிழ் பெயர்]',
    # DO NOT include parent_collection_id or Thirumurai references
    # ...other metadata...
}

work_dict = {
    # ...
    'primary_collection_id': XXXX,  # Own collection ID
    'metadata': work_metadata
}
```

### 4. Link to Collection
```python
def bulk_insert_work_collections(self):
    """Link all works to [Work] collection"""
    buffer = io.StringIO()
    for idx, work in enumerate(self.works, 1):
        fields = [
            str(work['work_id']),
            'XXXX',  # collection_id
            str(idx),  # position_in_collection
            't',  # is_primary (true)
            ''  # notes (NULL)
        ]
        buffer.write('\t'.join(fields) + '\n')

    buffer.seek(0)
    self.cursor.copy_from(
        buffer, 'work_collections',
        columns=['work_id', 'collection_id', 'position_in_collection', 'is_primary', 'notes'],
        null=''
    )
```

### 5. Import Order
```python
def import_data(self):
    try:
        self.bulk_insert_works()
        self.bulk_insert_work_collections()  # ✅ Must call this
        self.bulk_insert_sections()
        self.bulk_insert_verses()
        self.bulk_insert_lines()
        self.bulk_insert_words()
        self.conn.commit()
```

---

## Deletion Pattern

Each parser's collection can be deleted independently:

```bash
# Delete Devaram (7 works + collection)
python scripts/delete_work.py --collection-id 3211

# Delete Thiruvasagam (1 work + collection)
python scripts/delete_work.py --collection-id 3218
```

The `delete_work.py` script handles both patterns:
- `work_collections` table (proper way)
- `primary_collection_id` (backward compatibility)

---

## Applied To

### ✅ Completed
- `devaram_bulk_import.py` (Collection 3211)
- `thiruvasagam_bulk_import.py` (Collection 3218)

### 🔜 To Apply
- All remaining devotional literature parsers

---

## Master Script Responsibility

The `import_devotional_literature.py` master script will:

1. Create Thirumurai parent collection (321)
2. Run all individual parsers
3. Update collection hierarchy (set parent_collection_id on sub-collections)
4. Optionally create work_collections entries linking to parent collection

This keeps individual parsers self-contained and independently runnable.
