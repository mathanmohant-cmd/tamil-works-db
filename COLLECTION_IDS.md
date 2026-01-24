# Collection ID Scheme

This document defines the collection IDs used across all devotional literature parsers.

## Designated Filter Collection (Special)

- **1**: தமிழ் இலக்கியம் (Tamil Literature) - **ROOT COLLECTION FOR FILTER UI**
  - Created automatically by `sql/complete_setup.sql`
  - Serves as the designated collection for the filter hierarchy
  - All other collections can be nested under this root
  - Backend endpoint `/settings/designated_filter_collection` returns `{"collection_id": 1}`
  - **See**: `DESIGNATED_COLLECTION_PATTERN.md` for full documentation

## Main Collections

- **321**: திருமுறை (Thirumurai) - Main collection for all 12 Thirumurai books
- **322**: நாலாயிரத் திவ்விய பிரபந்தம் (Naalayira Divya Prabandham) - Main Vaishnavite collection
- **323**: பக்தி இலக்கியம் (Devotional Literature) - Standalone devotional works from various traditions
- **324**: ஐஞ்சிறுகாப்பியங்கள் (Five Jain Minor Epics) - Five Buddhist and Jain epics from 3rd-10th century CE
- **325**: நீதிநூல்கள் (Ethical Literature) - 21 ethical literature works spanning 3rd-20th century CE
- **326**: சிற்றிலக்கியங்கள் (Minor Literary Works) - 20 works spanning 11 genres from 12th-19th centuries CE
- **327**: சித்தர் பாடல்கள் (Siddhar Padalgal) - 36 mystical and spiritual poetry works by Tamil Siddhars from 7th-19th century CE
- **328**: இருபதாம் நூற்றாண்டு தமிழ் இலக்கியம் (Modern Tamil Literature) - 4 thematic groups of Bharathiyar's poetry from 1882-1921 CE

## Thirumurai Sub-Collections (Files 1-12)

### Individual Thirumurai Collections (1-7: Devaram)
- **32111**: முதலாம் திருமுறை (First Thirumurai) - Sambandar, File 1
- **32112**: இரண்டாம் திருமுறை (Second Thirumurai) - Sambandar, File 2
- **32113**: மூன்றாம் திருமுறை (Third Thirumurai) - Sambandar, File 3
- **32114**: நான்காம் திருமுறை (Fourth Thirumurai) - Appar, File 4
- **32115**: ஐந்தாம் திருமுறை (Fifth Thirumurai) - Appar, File 5
- **32116**: ஆறாம் திருமுறை (Sixth Thirumurai) - Appar, File 6
- **32117**: ஏழாம் திருமுறை (Seventh Thirumurai) - Sundarar, File 7

### 8th Thirumurai
- **3218**: எட்டாம் திருமுறை (Eighth Thirumurai) - Files 8.1 & 8.2
  - Works: திருவாசகம் (Thiruvasagam) + திருக்கோவையார் (Thirukovayar)

### 9th Thirumurai
- **3219**: ஒன்பதாம் திருமுறை (Ninth Thirumurai) - File 9
  - Sub-collection **32191**: திருவிசைப்பா (Thiruvisaippa) - Works 1-9
  - Work 10 (திருப்பல்லாண்டு) belongs directly to 3219

### 10th-12th Thirumurai
- **32110**: பத்தாம் திருமுறை (Tenth Thirumurai) - File 10, Thirumanthiram
- **32118**: பதினொன்றாம் திருமுறை (Eleventh Thirumurai) - File 11, Saiva Prabandha Malai (40 works)
- **32119**: பன்னிரண்டாம் திருமுறை (Twelfth Thirumurai) - File 12, Periya Puranam

## Devaram Author Sub-Collections

Parent collection: **3211** (தேவாரம் - Devaram)

- **321111**: சம்பந்தர் தேவாரம் (Sambandar Devaram) - Thirumurai 1-3
- **321112**: அப்பர் தேவாரம் (Appar Devaram) - Thirumurai 4-6
- **321113**: சுந்தரர் தேவாரம் (Sundarar Devaram) - Thirumurai 7

## Naalayira Divya Prabandham Sub-Collections (Files 13-16)

Parent collection: **322** (நாலாயிரத் திவ்விய பிரபந்தம்)

- **3221**: முதல் ஆயிரம் (First Thousand) - File 13, 10 works
- **3222**: இரண்டாம் ஆயிரம் (Second Thousand) - File 14, 3 works
- **3223**: மூன்றாம் ஆயிரம் (Third Thousand) - File 15, 11 works
- **3224**: நான்காம் ஆயிரம் (Fourth Thousand) - File 16, 1 work

## Collection Hierarchy

Each Devaram work is linked to THREE collections:
1. Individual Thirumurai collection (32111-32117) - PRIMARY
2. Author sub-collection (321111-321113) - SECONDARY
3. Main Devaram collection (3211) - TERTIARY

Thiruvisaippa works 1-9 are linked to TWO collections:
1. Thiruvisaippa sub-collection (32191) - PRIMARY
2. 9th Thirumurai (3219) - SECONDARY

Work 10 (திருப்பல்லாண்டு) is linked to ONE collection:
1. 9th Thirumurai (3219) - PRIMARY

## Key Principles

1. **No hardcoded collection IDs** - All parsers query collection IDs dynamically after creating them
2. **Dynamic position_in_collection** - All parsers query max position and increment for each work
3. **Hierarchical deletion** - Child collections must be deleted before parent collections
4. **Matching import/delete pairs** - Every import script has a corresponding delete script

## Import/Delete Script Pairs

| Import Script | Delete Script | Collections Created |
|--------------|---------------|---------------------|
| `devaram_bulk_import.py` | `delete_devaram.py` | 3211, 32111-32117, 321111-321113 |
| `thiruvasagam_bulk_import.py` | `delete_thiruvasagam.py` | 3218 (shared with thirukovayar) |
| `thirukovayar_bulk_import.py` | `delete_thirukovayar.py` | 3218 (shared with thiruvasagam) |
| `thiruvisaippa_bulk_import.py` | `delete_thiruvisaippa.py` | 3219, 32191 |
| `thirumanthiram_bulk_import.py` | `delete_thirumanthiram.py` | 32110 |
| `saiva_prabandha_malai_bulk_import.py` | `delete_saiva_prabandha_malai.py` | 32118 |
| `periya_puranam_bulk_import.py` | `delete_periya_puranam.py` | 32119 |
| `naalayira_divya_prabandham_bulk_import.py` | `delete_naalayira_divya_prabandham.py` | 322, 3221-3224 |
| `thiruppugazh_bulk_import.py` | `delete_thiruppugazh.py` | 323 (shared) |
| `thembavani_bulk_import.py` | `delete_thembavani.py` | 323 (shared) |
| `seerapuranam_bulk_import.py` | `delete_seerapuranam.py` | 323 (shared) |
| `thiruvarutpa_balakrishnapillai_bulk_import.py` | `delete_thiruvarutpa_balakrishnapillai.py` | 323 (shared) |
| `thiruvarutpa_uran_bulk_import.py` | `delete_thiruvarutpa_uran.py` | 323 (shared) |
| `sitrilakkiyangal_bulk_import.py` | `delete_sitrilakkiyangal.py` | 326 |
| `neethinoolkal_bulk_import.py` | `delete_neethinoolkal.py` | 325 |
| `siddhar_padalgal_bulk_import.py` | `delete_siddhar_padalgal.py` | 327 |
| `bharathiyar_bulk_import.py` | `delete_bharathiyar.py` | 328 |

## Standalone Devotional Literature (Collection 323)

**Collection 323** (பக்தி இலக்கியம் - Devotional Literature) is a **shared collection** for standalone devotional works that don't belong to Thirumurai or Naalayira Divya Prabandham.

### Works in Collection 323:
1. **Thiruppugazh** (திருப்புகழ்) - Arunagirinathar, Murugan devotion, 15th century CE
2. **Thembavani** (தேம்பாவணி) - Veeramaamunivar, Christian devotion, 18th century CE
3. **Seerapuranam** (சீறாப்புராணம்) - Umaru Pulavar, Islamic devotion, 19th century CE
4. **Thiruvarutpa - Balakrishnapillai Edition** (திருவருட்பா - பாலகிருஷ்ணபிள்ளை பதிப்பு) - Ramalinga Swamigal
5. **Thiruvarutpa - Uran Adigal Edition** (திருவருட்பா - ஊரன் அடிகள் பதிப்பு) - Ramalinga Swamigal

### Collection 323 Management:
- **Creation**: Each parser checks if collection 323 exists; creates it if missing
- **Linking**: Each work is linked to collection 323 with dynamic position assignment
- **Deletion**: Each delete script checks if collection 323 is empty after work deletion
  - If empty: Collection 323 is automatically deleted
  - If not empty: Collection 323 is retained for remaining works

## Minor Literary Works (Collection 326)

**Collection 326** (சிற்றிலக்கியங்கள் - Minor Literary Works) contains 20 diverse literary works spanning 12th-19th century CE.

### Genre Distribution:
- **கலம்பகம் (Kalambagam)**: 4 works (காசிக் கலம்பகம், கச்சிக் கலம்பகம், மதுரைக் கலம்பகம், நந்திக் கலம்பகம்)
- **பரணி (Parani)**: 2 works (கலிங்கத்துப்பரணி, தக்கயாகப்பரணி)
- **தூது (Messenger poems)**: 2 works (தமிழ்விடு தூது, அழகர் கிள்ளை விடுதூது)
- **கோவை (Kovai)**: 2 works (தஞ்சைவாணன் கோவை, பாண்டிக்கோவை)
- **குறவஞ்சி (Kuravanji)**: 2 works (திருக்குற்றாலக் குறவஞ்சி, பெத்லகேம் குறவஞ்சி)
- **Other genres**: அந்தாதி, சதகம், வெண்பா, சிந்து, பிள்ளைத்தமிழ், பள்ளு, உலா, புராணம்

### Prominent Authors:
- **குமரகுருபரர் (Kumarakuruparar)**: 3 works (காசிக் கலம்பகம், மதுரை மீனாட்சியம்மை பிள்ளைத் தமிழ், மதுரைக் கலம்பகம்)
- **ஒட்டக்கூத்தர் (Ottakkuttar)**: 2 works (தக்கயாகப்பரணி, மூவருலா)
- **11 other identified authors**, 4 anonymous works

### Collection 326 Details:
- **Total:** 20 works, 7,385 verses, 25,395 lines, 169,192 words
- **Structure Patterns:**
  - Simple pattern (5 works): Only #N verse markers
  - Dual_at pattern (14 works): @N section + #N verse markers
  - Dual_star pattern (1 work): *N. section + #N verse markers with 2-level hierarchy
- **Unified Parser:** Single script (`sitrilakkiyangal_bulk_import.py`) handles all 20 works using 2-phase bulk COPY pattern

## Ethical Literature (Collection 325)

**Collection 325** (நீதிநூல்கள் - Ethical Literature) contains 21 ethical literature works spanning 3rd-20th century CE.

### Works in Collection 325:
1. **Aathichudi** (ஆத்திசூடி) - Auvaiyar II, 12th century CE, 110 verses
2. **Konrai Venthan** (கொன்றைவேந்தன்) - Auvaiyar II, 12th century CE, 92 verses
3. **Moodhurai (Vaakkundaam)** (மூதுரை - வாக்குண்டாம்) - Auvaiyar II, 12th century CE, 31 verses
4. **Nalvazhi** (நல்வழி) - Auvaiyar II, 12th century CE, 41 verses
5. **Vetri Vetkai (Narunthokai)** (வெற்றி வேற்கை - நறுந்தொகை) - Unknown, 3rd-6th century CE, 85 verses
6. **Ulaga Neethi** (உலக நீதி) - Unknown, 6th-10th century CE, 14 verses
7. **Neethineeri Vilakkam** (நீதிநெறி விளக்கம்) - Unknown, 6th-10th century CE, 102 verses
8. **Araneri Chaaram** (அறநெறிச்சாரம்) - Unknown, 6th-10th century CE, 226 verses
9. **Neethi Nool** (நீதி நூல்) - Munusep Vedhanayagam Pillai, 19th century CE, 602 verses
10. **Nanneri** (நன்னெறி) - Siva Prakasar, 17th-18th century CE, 41 verses
11. **Neethi Chudamani** (நீதி சூடாமணி) - Unknown, 10th-15th century CE, 136 verses
12. **Somesar** (சோமேசர்) - Unknown, 10th-15th century CE, 134 verses
13. **Viveka Chinthamani** (விவேக சிந்தாமணி) - Unknown, 10th-15th century CE, 136 verses
14. **Aathichudi Venpa** (ஆத்திசூடி வெண்பா) - Unknown, 12th-17th century CE, 109 verses
15. **Neethi Venpa** (நீதி வெண்பா) - Unknown, 12th-17th century CE, 101 verses
16. **Nanmadhi Venpa** (நன்மதி வெண்பா) - Unknown, 12th-17th century CE, 109 verses
17. **Arungalach Cheppu** (அருங்கலச்செப்பு) - Unknown, 10th-15th century CE, 182 verses
18. **Mudhumozhimael Vaippu** (முதுமொழிமேல் வைப்பு) - Unknown, 10th-15th century CE, 198 verses
19. **Pudhiya Aathichudi** (புதிய ஆத்திசூடி) - Bharathiyar, 20th century CE, 111 verses
20. **Ilaiyaar Aathichudi** (இளையார் ஆத்திசூடி) - Unknown, 15th-19th century CE, 89 verses
21. **Thirukkural Kumaresa Venpa** (திருக்குறள் குமரேச வெண்பா) - Kumaresa Guruparar, 18th-19th century CE, 1,331 verses

### Collection 325 Details:
- **Total:** 21 works, 3,980 verses, 14,300 lines, 73,363 words
- **Special Handling:** File 21 (Thirukkural Kumaresa Venpa) has 134 sections with verses renumbered per section
- **Authors:** Includes works by Auvaiyar, Siva Prakasar, Bharathiyar, Kumaresa Guruparar, and others
- **Unified Parser:** Single script (`neethinoolkal_bulk_import.py`) handles all 21 works using 2-phase bulk COPY pattern

## Siddhar Padalgal (Collection 327)

**Collection 327** (சித்தர் பாடல்கள் - Siddhar Padalgal) contains 36 mystical and spiritual poetry works by Tamil Siddhars from 7th-19th century CE.

### Overview:
The Siddhars were enlightened yogis and mystics who composed philosophical and spiritual poetry in Tamil. Their songs cover topics like:
- **ஞானம் (Gnanam/Knowledge)**: Spiritual wisdom and enlightenment
- **யோக நிலை (Yoga Nilai)**: States of yogic practice
- **பூஜாவிதி (Poojaavidhi)**: Methods of worship
- **கலித்தாழிசை**: Poetic meters and forms

### Prominent Siddhars in Collection:
- **Agathiyar (அகத்தியர்)**: Legendary Siddhar, 7th-9th century CE (attributed)
- **Sivavaakiyar (சிவவாக்கியர்)**: Renowned for radical spiritual philosophy, 10th-12th century CE
- **Thirumoolar (திருமூலர்)**: Author of Thirumanthiram, 8th-9th century CE
- **Pattinatthu Siddhar (பட்டினத்துச் சித்தர்)**: Also known as Thiruvenkadar, 11th-12th century CE
- **Karuvurar (கருவூரார்)**: Famous Siddhar, 9th-10th century CE
- **32 other Siddhars**: Including Paambaatti (Snake-Charmer Siddhar), Kaagapusundar, and others

### Collection 327 Details:
- **Total:** 36 works, 2,886 verses, 9,731 lines, 55,922 words
- **Structure Patterns:**
  - Works with sections: Hierarchical organization (e.g., ஞானம் - 1, ஞானம் - 2)
  - Works without sections: Simple flat structure with default "Main Text" section
  - Metadata markers: Some works have `*N-N` verse-section cross-references (49 verses)
- **Metadata Storage:**
  - `sections.metadata` JSONB: Section type, category (knowledge/yoga/worship/poetic_form), numbered sections
  - `verses.metadata` JSONB: Section-verse references (`*1-1`, `*2-3`) for cross-linking
- **Unified Parser:** Single script (`siddhar_padalgal_bulk_import.py`) handles all 36 works using 2-phase bulk COPY pattern

## Modern Tamil Literature (Collection 328)

**Collection 328** (இருபதாம் நூற்றாண்டு தமிழ் இலக்கியம் - Modern Tamil Literature) contains 4 thematic groups of Subramania Bharathiyar's poetry from 1882-1921 CE.

### Overview:
Subramania Bharathiyar (சுப்பிரமணிய பாரதியார்) was a pioneering Tamil poet, freedom fighter, and social reformer. His poetry covers:
- **National Songs (தேசீய கீதங்கள்)**: Patriotic poetry for Indian independence
- **Social Reform (சமூக சீர்திருத்தம்)**: Women's liberation, education, equality
- **Devotional Poetry (பக்தி பாடல்கள்)**: Krishna songs, Vedantic hymns
- **Epic & Narrative (காப்பியம்)**: Panchali's Oath, autobiographical verse
- **Modern Free Verse (வசன கவிதை)**: Experimental poetry form

### Works in Collection 328:
1. **National & Social Reform Poetry** (தேசிய மற்றும் சமூகச் சீர்திருத்தக் கவிதைகள்) - Files 1, 4, 5, 11
   - தேசீய கீதங்கள் (National Songs)
   - பல்வகைப் பாடல்கள் (Miscellaneous Poems)
   - தனிப் பாடல்கள் (Individual Poems)
   - பிற்சேர்க்கை (Appendix - New Poems)

2. **Devotional & Spiritual Poetry** (பக்தி மற்றும் ஆன்மிகக் கவிதைகள்) - Files 2, 3, 7
   - தோத்திரப் பாடல்கள் (Devotional Songs)
   - வேதாந்தப் பாடல்கள் - ஞானப் பாடல்கள் (Vedantic Songs)
   - கண்ணன் பாட்டு (Krishna Songs)

3. **Epic & Narrative Poetry** (காப்பியக் கவிதைகள்) - Files 6, 8, 9
   - சுயசரிதை (Autobiography)
   - பாஞ்சாலி சபதம் (Panchali's Oath - Mahabharata epic)
   - குயில் பாட்டு (Song of the Koel - narrative)

4. **Modern Free Verse Poetry** (நவீன வசனக் கவிதை) - File 10
   - வசன கவிதை (Free Verse - experimental modern form)

### Collection 328 Details:
- **Total:** 4 works, ~500-1000 verses (estimated), ~15,000-25,000 words
- **Structure:** 3-level hierarchy (File → Subsection → Poem → Verses)
- **Special Features:**
  - Musical notation: ராகம் (raga), தாளம் (talam) stored in JSONB
  - Song structure: பல்லவி (pallavi/refrain), சரணங்கள் (charanam/stanzas)
  - Verse #0: Special pallavi verses (refrain)
  - Free verse: Variable line counts (not fixed 4-line stanzas)
- **Metadata Storage:**
  - `sections.metadata` JSONB: Musical notation (raagam, thaalam), song type, meter, translation notes
  - `verses.metadata` JSONB: Verse type (pallavi/charanam/anupallavi), special_number for #0
- **Unified Parser:** Single script (`bharathiyar_bulk_import.py`) handles all 11 source files using 2-phase bulk COPY pattern

## Notes

- **Collection 3218** (8th Thirumurai) is shared by two works (Thiruvasagam + Thirukovayar), so neither delete script removes the collection
- **Collection 323** (பக்தி இலக்கியம்) is shared by 5 standalone devotional works; delete scripts remove it only when empty
- **Collection 324** (சிற்றிலக்கியங்கள்) contains 20 minor literary works spanning 11 genres; delete script removes collection when empty
- **Collection 325** (நீதிநூல்கள்) contains 21 ethical literature works; delete script removes collection when empty
- **Collection 327** (சித்தர் பாடல்கள்) contains 36 Siddhar mystical poetry works; delete script removes collection when empty
- **Collection 328** (இருபதாம் நூற்றாண்டு தமிழ் இலக்கியம்) contains 4 Bharathiyar poetry works; delete script removes collection when empty
- Devaram has the most complex structure with 3-level collection hierarchy
- All collection IDs use dynamic queries, not hardcoded values in work metadata or bulk insert methods
- Standalone devotional works (collection 323) span multiple religious traditions: Shaivite, Christian, Islamic, and Siddha
