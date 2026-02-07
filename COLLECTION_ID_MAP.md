# Collection ID Mapping - Import Scripts Reference

This file maps all collection IDs to the import scripts that create them. Use this as a reference when writing delete scripts or debugging collection issues.

## Quick Reference Table

| Collection ID | Collection Name (Tamil) | Collection Name (English) | Import Script | Parent |
|--------------|------------------------|---------------------------|---------------|--------|
| 1 | தமிழ் இலக்கியம் | Tamil Literature | `sql/complete_setup.sql` | - |
| 11 | தமிழ் இலக்கண நூல்கள் | Tamil Grammar Works | `tolkappiyam_bulk_import.py` | 1 |
| 51 | பதினெண்மேல்கணக்கு | Eighteen Major Works (Sangam) | `sangam_bulk_import.py` | 1 |
| 201 | பதினெண்கீழ்க்கணக்கு | Eighteen Lesser Texts | `eighteen_lesser_texts_bulk_import.py` | 1 |
| 251 | ஐம்பெரும்காப்பியங்கள் | Five Great Epics | `five_great_epics_bulk_import.py` | 1 |
| 321 | திருமுறை | Thirumurai (Main) | `devaram_bulk_import.py` | 323 |
| 322 | நாலாயிரத் திவ்விய பிரபந்தம் | Naalayira Divya Prabandham | `naalayira_divya_prabandham_bulk_import.py` | 323 |
| 323 | பக்தி இலக்கியம் | Devotional Literature | Multiple (shared collection) | 1 |
| 324 | ஐஞ்சிறுகாப்பியங்கள் | Five Minor Epics (Jain/Buddhist) | `five_minor_epics_bulk_import.py` | 1 |
| 325 | நீதிநூல்கள் | Ethical Literature | `neethinoolkal_bulk_import.py` | 1 |
| 326 | சிற்றிலக்கியங்கள் | Minor Literary Works | `sitrilakkiyangal_bulk_import.py` | 1 |
| 327 | சித்தர் பாடல்கள் | Siddhar Padalgal | `siddhar_padalgal_bulk_import.py` | 1 |
| 328 | பாரதியார் படைப்புகள் | Bharathiyar Works | `bharathiyar_bulk_import.py` | 1 |
| 500 | காப்பியங்கள் | Epics (General) | `kambaramayanam_bulk_import.py` | 1 |
| 3211 | தேவாரம் | Devaram (Author collections) | `devaram_bulk_import.py` | - |
| 3218 | எட்டாம் திருமுறை | Eighth Thirumurai | `thiruvasagam_bulk_import.py` | 321 |
| 3219 | ஒன்பதாம் திருமுறை | Ninth Thirumurai | `thiruvisaippa_bulk_import.py` | 321 |
| 3221 | முதல் ஆயிரம் | First Thousand | `naalayira_divya_prabandham_bulk_import.py` | 322 |
| 3222 | இரண்டாம் ஆயிரம் | Second Thousand | `naalayira_divya_prabandham_bulk_import.py` | 322 |
| 3223 | மூன்றாம் ஆயிரம் | Third Thousand | `naalayira_divya_prabandham_bulk_import.py` | 322 |
| 3224 | நான்காம் ஆயிரம் | Fourth Thousand | `naalayira_divya_prabandham_bulk_import.py` | 322 |
| 32110 | பத்தாம் திருமுறை | Tenth Thirumurai | `thirumanthiram_bulk_import.py` | 321 |
| 32111 | முதலாம் திருமுறை | First Thirumurai (Sambandar) | `devaram_bulk_import.py` | 321 |
| 32112 | இரண்டாம் திருமுறை | Second Thirumurai (Sambandar) | `devaram_bulk_import.py` | 321 |
| 32113 | மூன்றாம் திருமுறை | Third Thirumurai (Sambandar) | `devaram_bulk_import.py` | 321 |
| 32114 | நான்காம் திருமுறை | Fourth Thirumurai (Appar) | `devaram_bulk_import.py` | 321 |
| 32115 | ஐந்தாம் திருமுறை | Fifth Thirumurai (Appar) | `devaram_bulk_import.py` | 321 |
| 32116 | ஆறாம் திருமுறை | Sixth Thirumurai (Appar) | `devaram_bulk_import.py` | 321 |
| 32117 | ஏழாம் திருமுறை | Seventh Thirumurai (Sundarar) | `devaram_bulk_import.py` | 321 |
| 32118 | பதினொன்றாம் திருமுறை | Eleventh Thirumurai | `saiva_prabandha_malai_bulk_import.py` | 321 |
| 32119 | பன்னிரண்டாம் திருமுறை | Twelfth Thirumurai | `periya_puranam_bulk_import.py` | 321 |
| 32191 | திருவிசைப்பா | Thiruvisaippa (Sub-collection) | `thiruvisaippa_bulk_import.py` | 3219 |
| 321111 | சம்பந்தர் தேவாரம் | Sambandar Devaram | `devaram_bulk_import.py` | 3211 |
| 321112 | அப்பர் தேவாரம் | Appar Devaram | `devaram_bulk_import.py` | 3211 |
| 321113 | சுந்தரர் தேவாரம் | Sundarar Devaram | `devaram_bulk_import.py` | 3211 |

---

## Master Import Scripts (Multiple Collections)

### 1. Eighteen Lesser Texts (பதினெண்கீழ்க்கணக்கு)
**Script**: `eighteen_lesser_texts_bulk_import.py`
**Delete Script**: `delete_eighteen_lesser_texts.py`

**Collections Created**:
- **201**: Eighteen Lesser Texts (பதினெண்கீழ்க்கணக்கு)

**Works**: 18 works total (currently only 6 imported)
- Individual work scripts: `thirukkural_bulk_import.py`, `naladiyar_bulk_import.py`, etc.

---

### 2. Five Great Epics (ஐம்பெரும்காப்பியங்கள்)
**Script**: `five_great_epics_bulk_import.py`
**Delete Script**: `delete_five_great_epics.py`

**Collections Created**:
- **251**: Five Great Epics (ஐம்பெரும்காப்பியங்கள்)

**Works**: 5 epics
- Silapathikaram, Manimegalai, Seevaka Sinthamani, Valayapathi, Kundalakesi

---

### 3. Five Minor Epics (ஐஞ்சிறுகாப்பியங்கள்)
**Script**: `five_minor_epics_bulk_import.py`
**Delete Script**: `delete_five_minor_epics.py`

**Collections Created**:
- **324**: Five Minor Epics (ஐஞ்சிறுகாப்பியங்கள்)

**Works**: 5 Jain/Buddhist epics
- Udayana Kumara Kaviyam, Nagakumara Kaviyam, Yasodara Kaviyam, Choolamani, Nilakesi

---

### 4. Sangam Literature (பதினெண்மேல்கணக்கு)
**Script**: `sangam_bulk_import.py`
**Delete Script**: `delete_sangam.py`

**Collections Created**:
- **51**: Eighteen Major Works (பதினெண்மேல்கணக்கு)

**Works**: 18 Sangam anthologies

---

### 5. Devaram (தேவாரம்)
**Script**: `devaram_bulk_import.py`
**Delete Script**: `delete_devaram.py`

**Collections Created**:
- **321**: Thirumurai (திருமுறை) - Main collection
- **3211**: Devaram (தேவாரம்) - Author grouping parent
- **32111**: First Thirumurai (முதலாம் திருமுறை) - Sambandar
- **32112**: Second Thirumurai (இரண்டாம் திருமுறை) - Sambandar
- **32113**: Third Thirumurai (மூன்றாம் திருமுறை) - Sambandar
- **32114**: Fourth Thirumurai (நான்காம் திருமுறை) - Appar
- **32115**: Fifth Thirumurai (ஐந்தாம் திருமுறை) - Appar
- **32116**: Sixth Thirumurai (ஆறாம் திருமுறை) - Appar
- **32117**: Seventh Thirumurai (ஏழாம் திருமுறை) - Sundarar
- **321111**: Sambandar Devaram (சம்பந்தர் தேவாரம்) - Author collection
- **321112**: Appar Devaram (அப்பர் தேவாரம்) - Author collection
- **321113**: Sundarar Devaram (சுந்தரர் தேவாரம்) - Author collection

**Works**: 7 Devaram works (Thirumurai 1-7)

---

### 6. Naalayira Divya Prabandham (நாலாயிரத் திவ்விய பிரபந்தம்)
**Script**: `naalayira_divya_prabandham_bulk_import.py`
**Delete Script**: `delete_naalayira_divya_prabandham.py`

**Collections Created**:
- **322**: Naalayira Divya Prabandham (நாலாயிரத் திவ்விய பிரபந்தம்) - Main collection
- **3221**: First Thousand (முதல் ஆயிரம்)
- **3222**: Second Thousand (இரண்டாம் ஆயிரம்)
- **3223**: Third Thousand (மூன்றாம் ஆயிரம்)
- **3224**: Fourth Thousand (நான்காம் ஆயிரம்)

**Works**: 24 Vaishnavite works

---

### 7. Ethical Literature (நீதிநூல்கள்)
**Script**: `neethinoolkal_bulk_import.py`
**Delete Script**: `delete_neethinoolkal.py`

**Collections Created**:
- **325**: Ethical Literature (நீதிநூல்கள்)

**Works**: 21 ethical works spanning 3rd-20th century CE

---

### 8. Minor Literary Works (சிற்றிலக்கியங்கள்)
**Script**: `sitrilakkiyangal_bulk_import.py`
**Delete Script**: `delete_sitrilakkiyangal.py`

**Collections Created**:
- **326**: Minor Literary Works (சிற்றிலக்கியங்கள்)

**Works**: 20 works spanning 11 genres (12th-19th century CE)

---

### 9. Siddhar Padalgal (சித்தர் பாடல்கள்)
**Script**: `siddhar_padalgal_bulk_import.py`
**Delete Script**: `delete_siddhar_padalgal.py`

**Collections Created**:
- **327**: Siddhar Padalgal (சித்தர் பாடல்கள்)

**Works**: 36 mystical poetry works by Tamil Siddhars (7th-19th century CE)

---

### 10. Bharathiyar Works (பாரதியார் படைப்புகள்)
**Script**: `bharathiyar_bulk_import.py`
**Delete Script**: `delete_bharathiyar.py`

**Collections Created**:
- **328**: Bharathiyar Works (பாரதியார் படைப்புகள்)

**Works**: 4 thematic groups of Bharathiyar's poetry (1882-1921 CE)

---

## Individual Work Import Scripts

### Thirumurai Individual Works

#### Eighth Thirumurai (எட்டாம் திருமுறை)
**Collections Created**:
- **3218**: Eighth Thirumurai (எட்டாம் திருமுறை) - Shared by 2 works

**Scripts**:
- `thiruvasagam_bulk_import.py` - Creates collection 3218
- `thirukovayar_bulk_import.py` - Uses existing collection 3218

**Delete Scripts**:
- `delete_thiruvasagam.py` - Does NOT delete collection 3218 (shared)
- `delete_thirukovayar.py` - Does NOT delete collection 3218 (shared)

---

#### Ninth Thirumurai (ஒன்பதாம் திருமுறை)
**Collections Created**:
- **3219**: Ninth Thirumurai (ஒன்பதாம் திருமுறை)
- **32191**: Thiruvisaippa (திருவிசைப்பா) - Sub-collection

**Script**: `thiruvisaippa_bulk_import.py`
**Delete Script**: `delete_thiruvisaippa.py`

---

#### Tenth Thirumurai (பத்தாம் திருமுறை)
**Collections Created**:
- **32110**: Tenth Thirumurai (பத்தாம் திருமுறை)

**Script**: `thirumanthiram_bulk_import.py`
**Delete Script**: `delete_thirumanthiram.py`

---

#### Eleventh Thirumurai (பதினொன்றாம் திருமுறை)
**Collections Created**:
- **32118**: Eleventh Thirumurai (பதினொன்றாம் திருமுறை)

**Script**: `saiva_prabandha_malai_bulk_import.py`
**Delete Script**: `delete_saiva_prabandha_malai.py`

---

#### Twelfth Thirumurai (பன்னிரண்டாம் திருமுறை)
**Collections Created**:
- **32119**: Twelfth Thirumurai (பன்னிரண்டாம் திருமுறை)

**Script**: `periya_puranam_bulk_import.py`
**Delete Script**: `delete_periya_puranam.py`

---

### Standalone Devotional Works (Collection 323)

**Collection 323** (பக்தி இலக்கியம் - Devotional Literature) is a **shared collection** for standalone devotional works. Each script checks if it exists and creates it if missing.

**Scripts that add to Collection 323**:
1. `thiruppugazh_bulk_import.py` - Thiruppugazh (திருப்புகழ்)
2. `thembavani_bulk_import.py` - Thembavani (தேம்பாவணி)
3. `seerapuranam_bulk_import.py` - Seerapuranam (சீறாப்புராணம்)
4. `thiruvarutpa_balakrishnapillai_bulk_import.py` - Thiruvarutpa (Balakrishnapillai Edition)
5. `thiruvarutpa_uran_bulk_import.py` - Thiruvarutpa (Uran Adigal Edition)

**Delete Scripts**:
- Each delete script removes its work from collection 323
- Collection 323 is only deleted when the last work is removed

---

### Other Individual Works

#### Tolkāppiyam (தொல்காப்பியம்)
**Collections Created**:
- **11**: Tamil Grammar Works (தமிழ் இலக்கண நூல்கள்)

**Script**: `tolkappiyam_bulk_import.py`
**Delete Script**: `delete_tolkappiyam.py`

---

#### Kambaramayanam (கம்பராமாயணம்)
**Collections Created**:
- **500**: Epics (காப்பியங்கள்)

**Script**: `kambaramayanam_bulk_import.py`
**Delete Script**: `delete_kambaramayanam.py`

---

## Collection Hierarchy Summary

```
1 (Tamil Literature)
├── 11 (Tamil Grammar Works)
├── 51 (Sangam - Eighteen Major Works)
├── 201 (Eighteen Lesser Texts)
├── 251 (Five Great Epics)
├── 323 (Devotional Literature)
│   ├── 321 (Thirumurai)
│   │   ├── 3218 (8th Thirumurai)
│   │   ├── 3219 (9th Thirumurai)
│   │   │   └── 32191 (Thiruvisaippa)
│   │   ├── 32110 (10th Thirumurai)
│   │   ├── 32111-32117 (1st-7th Thirumurai)
│   │   ├── 32118 (11th Thirumurai)
│   │   └── 32119 (12th Thirumurai)
│   └── 322 (Naalayira Divya Prabandham)
│       ├── 3221 (First Thousand)
│       ├── 3222 (Second Thousand)
│       ├── 3223 (Third Thousand)
│       └── 3224 (Fourth Thousand)
├── 324 (Five Minor Epics)
├── 325 (Ethical Literature)
├── 326 (Minor Literary Works)
├── 327 (Siddhar Padalgal)
├── 328 (Bharathiyar Works)
└── 500 (Epics - General)

3211 (Devaram - Author Collections)
├── 321111 (Sambandar Devaram)
├── 321112 (Appar Devaram)
└── 321113 (Sundarar Devaram)
```

---

## Important Notes

1. **Collection 1**: Root collection created by `sql/complete_setup.sql`, not by any import script
2. **Collection 323**: Shared by 5 standalone devotional works; only deleted when empty
3. **Collection 3218**: Shared by Thiruvasagam + Thirukovayar; never deleted by individual delete scripts
4. **Collection 3211**: Devaram author collections (separate hierarchy from Thirumurai)
5. **Dynamic IDs**: All scripts query for collection existence and create if missing - no hardcoded assumptions

---

## Checklist for New Import Scripts

When creating a new import script:
- [ ] Choose collection ID from available range
- [ ] Check if collection exists before creating
- [ ] Set correct `parent_collection_id`
- [ ] Add mapping to this file
- [ ] Create matching delete script with correct collection ID
- [ ] Update `COLLECTION_IDS.md` if needed
- [ ] Test both import and delete scripts

---

## Common Collection ID Ranges

- **1-99**: System/root collections
- **11-50**: Grammar and foundational texts
- **51-99**: Classical literature (Sangam)
- **201-299**: Post-Sangam classical texts
- **251-299**: Epic literature
- **321-329**: Devotional literature (main collections)
- **500-599**: Epic/narrative literature (general)
- **3211-3299**: Thirumurai sub-collections (2nd level)
- **32110-32999**: Thirumurai sub-collections (3rd level)
- **321111-329999**: Thirumurai author/grouping collections (4th level)
