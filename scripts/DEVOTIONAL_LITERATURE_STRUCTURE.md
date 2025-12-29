# Devotional Literature File Structure Reference

This document contains the detailed structure of all 21 Devotional Literature files based on the CSV metadata and file analysis.

**Source:** `Tamilconcordance.in - Sheet2.csv` in `Tamil-Source-TamilConcordence\6_பக்தி இலக்கியம்`

---

## THIRUMURAI COLLECTION (திருமுறை) - Files 1-12
**Collection ID:** 321
**Total Works:** ~40 works
**Tradition:** Shaivite

### Files 1-7: DEVARAM (தேவாரம்)

#### File 1: முதலாம் திருமுறை
- **Work:** சம்பந்தர் தேவாரம் (1-1469)
- **Author:** திருஞானசம்பந்தர் (Thirugnanasambandar)
- **Period:** 7th century CE
- **Structure:**
  ```
  திருஞானசம்பந்தர் ^ சம்பந்தர் தேவாரம் (1 - 1469)

  1. Section name : பண் - musical_mode

  #verse_number
  line 1
  line 2
  ...
  மேல்
  ```
- **Hierarchy:** Pathigam (பதிகம்) → Verses
- **Section Metadata:** பண் (musical mode)
- **Verse Type:** பாடல் (devotional hymn)

#### File 2: இரண்டாம் திருமுறை
- **Work:** சம்பந்தர் தேவாரம் (1470-2800)
- **Author:** திருஞானசம்பந்தர்
- **Same structure as File 1**

#### File 3: மூன்றாம் திருமுறை
- **Work:** சம்பந்தர் தேவாரம் (2801-4169)
- **Author:** திருஞானசம்பந்தர்
- **Same structure as File 1**

#### File 4: நான்காம் திருமுறை
- **Work:** அப்பர் தேவாரம் (1-1070)
- **Author:** திருநாவுக்கரசர் (அப்பர்) - Thirunavukkarasar (Appar)
- **Period:** 7th century CE
- **Same structure as File 1**

#### File 5: ஐந்தாம் திருமுறை
- **Work:** அப்பர் தேவாரம் (1071-2085)
- **Sub-work:** திருக்குறுந்தொகை
- **Author:** திருநாவுக்கரசர்
- **Same structure as File 1**

#### File 6: ஆறாம் திருமுறை
- **Work:** அப்பர் தேவாரம் (2086-3066)
- **Sub-work:** திருத்தாண்டகம்
- **Author:** திருநாவுக்கரசர்
- **Same structure as File 1**

#### File 7: ஏழாம் திருமுறை
- **Work:** சுந்தரர் தேவாரம் (1-101)
- **Author:** சுந்தரர் (Sundarar)
- **Period:** 8th century CE
- **Same structure as File 1**

**Parser Status:** ✅ `devaram_bulk_import.py` COMPLETED

---

### File 8.1: எட்டாம் திருமுறை - திருவாசகம்

- **Work:** திருவாசகம் (Thiruvasagam)
- **Author:** மாணிக்கவாசகர் (Manikkavasagar)
- **Period:** 9th century CE
- **Place:** திருவாதவூர்
- **Structure:**
  ```
  மாணிக்கவாசகர் ^ திருவாசகம்

  @pathigam_number pathigam_name

  continuous lines (no # verse markers)
  line numbers appear on right at multiples of 5

  மேல்
  ```
- **Hierarchy:** Pathigam (பதிகம்) → ONE continuous verse per pathigam
- **Verse Type:** பாடல்
- **Notable Sections:** திருவெம்பாவை, திருப்பள்ளியெழுச்சி
- **Total Pathigams:** 51

**Parser Status:** ✅ `thiruvasagam_bulk_import.py` COMPLETED

---

### File 8.2: எட்டாம் திருமுறை - திருக்கோவையார்

- **Work:** திருக்கோவையார் (Thirukovayar)
- **Author:** மாணிக்கவாசகர்
- **Hierarchy:** இயல் (Iyal) → அதிகாரம் (Adhikaram) → Verses
- **Verse Metadata:** துறை (thurai - poetic theme)
- **Structure:** Different from Thiruvasagam, more like Thirukkural structure

**Parser Status:** ⏳ PENDING

---

### File 9: ஒன்பதாம் திருமுறை - திருவிசைப்பா

**Multiple authors:**
1. திருமாளிகைத் தேவர் (Thirumalaidevar) - Pathigams
2. சேந்தனார் (Sendanar) - Pathigams + திருப்பல்லாண்டு
3. கருவூர்த் தேவர் (Karuvur Devar) - Pathigams
4. பூந்துருத்தி நம்பி காடநம்பி (Poonduruthi Nambi) - Pathigams
5. கண்டராதித்தர் (Kandaradhittar) - Pathigams
6. வேணாட்டடிகள் (Venadadigal) - Pathigams
7. திருவாலியமுதனார் (Thiruvaliyamudanar) - Pathigams
8. புருடோத்தம நம்பி (Purudothama Nambi) - Pathigams
9. சேதிராயர் (Sethirayar) - Pathigams

- **Hierarchy:** Pathigam (பதிகம்) → Verses
- **Section Metadata:** பண் (musical mode)
- **Structure:** Similar to Devaram (Files 1-7)

**Parser Status:** ⏳ PENDING

---

### File 10: பத்தாம் திருமுறை - திருமந்திரம்

- **Work:** திருமந்திரம் (Thirumanthiram)
- **Author:** திருமூலர் (Thirumoolar)
- **Period:** 2nd-6th century CE (disputed)
- **Verse Count:** 3,000 verses
- **Structure:**
  ```
  திருமூலர் ^ திருமந்திரம்

  @tantra_number பாயிரம் or tantra_name

  #verse_number
  lines...

  மேல்
  ```
- **Hierarchy:** தந்திரம் (Tantra - 9 tantras) → Verses
- **Genre:** Philosophical-devotional (yoga, tantra, philosophy, ethics)
- **Meter:** Venba
- **Musical Tradition:** No (more philosophical than musical)

**Parser Status:** ⏳ PENDING

---

### File 11: பதினொன்றாம் திருமுறை - சைவப் பிரபந்த மாலை

**29 works by various authors:**

**By காரைக்கால் அம்மையார் (Karaikkal Ammaiyar):**
1. மூத்த திருப்பதிகம்
2. திரு இரட்டை மணிமாலை
3. அற்புதத்திருவந்தாதி

**By other saints:** (26 more works - see CSV for full list)
- திரு ஆலவாய் உடையார், நக்கீரதேவ நாயனார், கபில தேவ நாயனார், பட்டினத்து அடிகள், நம்பியாண்டார் நம்பி, etc.

- **Hierarchy:** Varies by work (most don't have sub-sections)
- **Verse Types:** பாசுரம், வெண்பா, various poetic forms
- **Section Metadata:** பண் (some works), பா வகை, பா உறுப்பு, நிகழ்வு

**Parser Status:** ⏳ PENDING (Most complex - 29 different works)

---

### File 12: பன்னிரண்டாம் திருமுறை - பெரியபுராணம்

- **Work:** பெரியபுராணம் (Periya Puranam)
- **Author:** சேக்கிழார் (Sekkizhar)
- **Period:** 12th century CE
- **Genre:** Hagiography (வரலாற்றுக் காப்பியம்)
- **Subject:** Lives of 63 Nayanmars (Shaivite saints)
- **Verse Count:** 4,286 verses
- **Hierarchy:** சருக்கம் (Sarukkam/Chapter) → சிறப்பு or புராணம் (Sirappu/Puranam) → Verses
- **Meter:** Viruttam
- **Structure:** 13 chapters covering different Nayanmars

**Parser Status:** ⏳ PENDING

---

## NAALAYIRA DIVYA PRABANDHAM (நாலாயிரத் திவ்விய பிரபந்தம்) - Files 13-16
**Collection ID:** 322
**Total Works:** 24 works by 12 Alvars
**Total Verses:** ~4,000 (நாலாயிரம் = 4000)
**Tradition:** Vaishnavite

### File 13: முதல் ஆயிரம் (First Aayiram - verses 1-947)

**10 works:**

1. **திருப்பல்லாண்டு** (1-12 = 12 verses)
   - Author: பெரியாழ்வார் (Periyalvar)

2. **திருமொழி** (13-473 = 461 verses)
   - Author: பெரியாழ்வார்

3. **திருப்பாவை** (474-503 = 30 verses)
   - Author: ஆண்டாள் (Andal) - Only female Alvar
   - Most famous work, recited during Margazhi month

4. **நாச்சியார் திருமொழி** (504-646 = 143 verses)
   - Author: ஆண்டாள்

5. **பெருமாள் திருமொழி** (647-751 = 105 verses)
   - Author: குலசேகர ஆழ்வார் (Kulasekara Alvar)

6. **திருச்சந்த விருத்தம்** (752-871 = 120 verses)
   - Author: திருமழிசை ஆழ்வார் (Thirumalisai Alvar)

7. **திருமாலை** (872-916 = 45 verses)
   - Author: தொண்டரடிப்பொடி ஆழ்வார் (Thondaradippodi Alvar)

8. **திருப்பள்ளியெழுச்சி** (917-926 = 10 verses)
   - Author: தொண்டரடிப்பொடி ஆழ்வார்

9. **அமலனாதிபிரான்** (927-936 = 10 verses)
   - Author: திருப்பாணாழ்வார் (Thiruppan Alvar)

10. **கண்ணிநுண்சிறுத்தாம்பு** (937-947 = 11 verses)
    - Author: மதுரகவி ஆழ்வார் (Madhurakavi Alvar)

**Structure:**
```
1. முதலாம் ஆயிரம்
@author_name ^ work_name

#verse_number
lines...

மேல் or blank line

@next_author ^ next_work
```

**Parser Status:** ⏳ PENDING

---

### File 14: இரண்டாம் ஆயிரம் (Second Aayiram - verses 948-2081)

**3 works by திருமங்கை ஆழ்வார் (Thirumangai Alvar):**

1. **பெரிய திருமொழி** (948-2031 = 1,084 verses)
2. **திருக்குறுந்தாண்டகம்** (2032-2051 = 20 verses)
3. **திருநெடுந்தாண்டகம்** (2052-2081 = 30 verses)

**Parser Status:** ⏳ PENDING

---

### File 15: மூன்றாம் ஆயிரம் (Third Aayiram - verses 2082-2898)

**10 works:**

1. **முதல் திருவந்தாதி** (2082-2181 = 100 verses)
   - Author: பொய்கை ஆழ்வார் (Poigai Alvar) - First Alvar

2. **இரண்டாம் திருவந்தாதி** (2182-2281 = 100 verses)
   - Author: பூதத்தாழ்வார் (Bhoothathalvar)

3. **மூன்றாம் திருவந்தாதி** (2282-2381 = 100 verses)
   - Author: பேயாழ்வார் (Pey Alvar)

4. **நான்முகன் திருவந்தாதி** (2382-2477 = 96 verses)
   - Author: திருமழிசை ஆழ்வார்

5. **திருவிருத்தம்** (2478-2577 = 100 verses)
   - Author: நம்மாழ்வார் (Nammalvar) - Chief Alvar

6. **திருவாசிரியம்** (2578-2584 = 7 verses)
   - Author: நம்மாழ்வார்

7. **பெரிய திருவந்தாதி** (2585-2671 = 87 verses)
   - Author: நம்மாழ்வார்

8. **திருவெழுக்கூற்றிருக்கை** (2672 = 1 verse)
   - Author: திருமங்கை ஆழ்வார்

9. **சிறிய திருமடல்** (2673-2712 = 40 verses)
   - Author: திருமங்கை ஆழ்வார்

10. **பெரிய திருமடல்** (2713-2790 = 78 verses)
    - Author: திருமங்கை ஆழ்வார்

11. **இராமானுச நூற்றந்தாதி** (2791-2898 = 108 verses)
    - Author: திருவரங்கத்து அமுதனார் (Thirvarangatthu Amudhanar)

**Parser Status:** ⏳ PENDING

---

### File 16: நான்காம் ஆயிரம் (Fourth Aayiram - verses 2899-4000)

**1 work:**

**திருவாய்மொழி** (2899-4000 = 1,102 verses)
- **Author:** நம்மாழ்வார் (Nammalvar)
- **Status:** Magnum opus of Nammalvar, "Tamil Veda"
- **Structure:** 10 centums (100 verses each + 2 extra)
- **Meter:** Viruttam
- **Theological Depth:** Highest - foundation of Sri Vaishnava theology
- **Covers:** ~40 Divya Desams (sacred Vishnu temples)

**Parser Status:** ⏳ PENDING

---

## STANDALONE DEVOTIONAL WORKS - Files 17-21

### File 17: திருப்புகழ்

- **Work:** திருப்புகழ் (Thiruppugazh)
- **Author:** அருணகிரிநாதர் (Arunagirinathar)
- **Period:** 15th century CE
- **Deity:** முருகன் (Murugan)
- **Tradition:** Murugan worship
- **Structure:**
  ```
  அருணகிரிநாதர் ^ திருப்புகழ்

  @collection_number முதல்_தொகுதி

  #verse_number
  lines...

  மேல்
  ```
- **Hierarchy:** தொகுதி (Collection/Volume) → Verses

**Parser Status:** ⏳ PENDING

---

### File 18: தேம்பாவணி

- **Work:** தேம்பாவணி (Thembavani)
- **Author:** வீரமாமுனிவர் (Veeramaamunivar / Constanzo Giuseppe Beschi)
- **Period:** 18th century CE (1726)
- **Tradition:** Christian devotional literature
- **Subject:** Life of St. Joseph
- **Verse Count:** 3,615 verses
- **Hierarchy:** படலம் (Padalam/Canto) → Verses
- **Genre:** Epic poem

**Parser Status:** ⏳ PENDING

---

### File 19: சீறாப்புராணம்

- **Work:** சீறாப்புராணம் (Seerapuranam)
- **Author:** உமறுப் புலவர் (Umarupulavar)
- **Period:** 16th century CE
- **Tradition:** Islamic literature
- **Subject:** Life of Prophet Muhammad
- **Hierarchy:** காண்டம் (Kandam) → படலம் (Padalam) → Verses
- **Genre:** Epic poem

**Parser Status:** ⏳ PENDING

---

### Files 20-21: திருவருட்பா (Two Editions)

- **Work:** திருவருட்பா (Thiruvarutpa)
- **Author:** வள்ளலார் (Vallalar / Ramalinga Swamigal)
- **Period:** 19th century CE (1823-1874)
- **Movement:** Universal brotherhood, vegetarianism
- **Hierarchy:** திருமுறை (Thirumurai) → பதிகம் (Pathigam) → Verses

**Two editions:**
1. **File 20:** ஊரன் அடிகள் பதிப்பு (Uran Adigal Edition)
2. **File 21:** பாலகிருஷ்ணபிள்ளை பதிப்பு (Balakrishna Pillai Edition)

**Parser Status:** ⏳ PENDING

---

## FILE STRUCTURE PATTERNS SUMMARY

### Pattern 1: Devaram-style (Files 1-7, 9)
```
Author ^ Work (verse range)
Section. Section_name : பண் - pann_name
#verse_number
lines
மேல்
```

### Pattern 2: Thiruvasagam-style (File 8.1)
```
Author ^ Work
@pathigam_number pathigam_name
continuous lines (no # markers)
மேல்
```

### Pattern 3: Thirumanthiram-style (File 10)
```
Author ^ Work
@tantra_number tantra_name
#verse_number
lines
மேல்
```

### Pattern 4: Naalayira Divya Prabandham (Files 13-16)
```
File title
@Author ^ Work
#verse_number or continuous
```

### Pattern 5: Hierarchical (Files 8.2, 12, 19)
```
Author ^ Work
Kandam/Sarukkam markers
Padalam/Sirappu markers
#verse_number
lines
```

---

## METADATA FIELDS (JSONB)

### Work-Level Metadata
```json
{
  "tradition": "Shaivite|Vaishnavite|Christian|Islamic|Murugan worship",
  "collection_id": 321|322,
  "collection_name": "Thirumurai|Naalayira Divya Prabandham",
  "sub_collection": "Devaram|...",
  "thirumurai_number": 1-12,
  "saint": "tamil_name",
  "saint_transliteration": "english_name",
  "time_period": "century CE",
  "deity_focus": "Shiva|Vishnu|Murugan|Christ|Prophet",
  "musical_tradition": true|false,
  "performance_context": "temple worship|...",
  "liturgical_use": true|false
}
```

### Section-Level Metadata
```json
{
  "section_type": "pathigam|tantra|sarukkam|...",
  "pann": "musical_mode",
  "temple": "deity_location",
  "thematic_focus": ["theme1", "theme2"]
}
```

### Verse-Level Metadata
```json
{
  "saint": "author_name",
  "deity": "deity_name",
  "meter": "venba|viruttam|...",
  "themes": ["theme1", "theme2"],
  "divya_desam": "temple_name"
}
```

---

## NEXT STEPS

1. Test completed parsers:
   - `devaram_bulk_import.py`
   - `thiruvasagam_bulk_import.py`

2. Create remaining parsers (11 more)

3. Create master import script

4. Verify data integrity

---

**Last Updated:** 2025-12-28
**Reference CSV:** `Tamilconcordance.in - Sheet2.csv`
