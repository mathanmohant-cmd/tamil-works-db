# Tamil Literature Chronology Proposal

## Overview
This document defines the chronological ordering and date ranges for Tamil literary works in the database. These dates represent scholarly consensus where possible, with documented variations.

## Database Fields

### works table additions:
- `traditional_sort_order` (INTEGER) - Traditional sequence in Tamil literary canon
- `chronology_start_year` (INTEGER) - Approximate start year (negative = BCE)
- `chronology_end_year` (INTEGER) - Approximate end year (negative = BCE)
- `chronology_confidence` (VARCHAR) - Confidence level: 'high', 'medium', 'low', 'disputed'
- `chronology_notes` (TEXT) - Scholarly variations and notes

## Chronological Ordering (Consensus Timeline)

### 1. Tolkāppiyam (தொல்காப்பியம்)
- **Traditional Order:** 1
- **Period:** 500 BCE - 200 BCE
- **Confidence:** Medium (disputed, some scholars date to 200 CE)
- **Notes:** Ancient grammar text. Dated between 3rd century BCE to 5th century CE by different scholars. Consensus: pre-Sangam or early Sangam.

### 2-9. Ettuthokai (எட்டுத்தொகை) - Eight Anthologies
Classic Sangam poetry anthologies (200 BCE - 200 CE)

#### 2. Natrrinai (நற்றிணை)
- **Traditional Order:** 2
- **Period:** 100 BCE - 100 CE
- **Confidence:** High
- **Notes:** Considered among the earliest Sangam works

#### 3. Kurunthokai (குறுந்தொகை)
- **Traditional Order:** 3
- **Period:** 100 BCE - 100 CE
- **Confidence:** High

#### 4. Ainkurunuru (ஐங்குறுநூறு)
- **Traditional Order:** 4
- **Period:** 100 BCE - 200 CE
- **Confidence:** High

#### 5. Pathitrupathu (பதிற்றுப்பத்து)
- **Traditional Order:** 5
- **Period:** 100 CE - 200 CE
- **Confidence:** High
- **Notes:** Features Chera kings, slightly later than other anthologies

#### 6. Paripaadal (பரிபாடல்)
- **Traditional Order:** 6
- **Period:** 100 CE - 200 CE
- **Confidence:** High
- **Notes:** Religious hymns to Murugan and Thirumal

#### 7. Kalithokai (கலித்தொகை)
- **Traditional Order:** 7
- **Period:** 100 CE - 250 CE
- **Confidence:** Medium
- **Notes:** Some scholars date to later Sangam period

#### 8. Aganaanuru (அகநானூறு)
- **Traditional Order:** 8
- **Period:** 100 BCE - 200 CE
- **Confidence:** High

#### 9. Puranaanuru (புறநானூறு)
- **Traditional Order:** 9
- **Period:** 100 BCE - 200 CE
- **Confidence:** High
- **Notes:** Historical references help date some poems precisely

### 10-19. Pathupaattu (பத்துப்பாட்டு) - Ten Idylls
Long poems, slightly later than Ettuthokai (100 CE - 250 CE)

#### 10. Thirumurugaatruppadai (திருமுருகாற்றுப்படை)
- **Traditional Order:** 10
- **Period:** 150 CE - 250 CE
- **Confidence:** High

#### 11. Porunaraatruppadai (பொருநராற்றுப்படை)
- **Traditional Order:** 11
- **Period:** 150 CE - 250 CE
- **Confidence:** High

#### 12. Sirupanaatruppadai (சிறுபாணாற்றுப்படை)
- **Traditional Order:** 12
- **Period:** 150 CE - 250 CE
- **Confidence:** High

#### 13. Perumpanaatruppadai (பெரும்பாணாற்றுப்படை)
- **Traditional Order:** 13
- **Period:** 150 CE - 250 CE
- **Confidence:** High

#### 14. Mullaippaattu (முல்லைப்பாட்டு)
- **Traditional Order:** 14
- **Period:** 150 CE - 250 CE
- **Confidence:** High

#### 15. Madurai Kanchi (மதுரைக்காஞ்சி)
- **Traditional Order:** 15
- **Period:** 150 CE - 250 CE
- **Confidence:** High

#### 16. Nedunalvaadai (நெடுநல்வாடை)
- **Traditional Order:** 16
- **Period:** 150 CE - 250 CE
- **Confidence:** High

#### 17. Kurinchippaattu (குறிஞ்சிப்பாட்டு)
- **Traditional Order:** 17
- **Period:** 150 CE - 250 CE
- **Confidence:** High

#### 18. Pattinappaalai (பட்டினப்பாலை)
- **Traditional Order:** 18
- **Period:** 150 CE - 250 CE
- **Confidence:** High

#### 19. Malaipadukataam (மலைபடுகடாம்)
- **Traditional Order:** 19
- **Period:** 150 CE - 250 CE
- **Confidence:** High

### 20. Thirukkural (திருக்குறள்)
- **Traditional Order:** 20
- **Period:** 300 CE - 500 CE
- **Confidence:** Medium (disputed, ranging 200 BCE - 800 CE)
- **Notes:** Most scholars place it in 4th-6th century CE. Represents post-Sangam ethical literature.

### 21. Silapathikaram (சிலப்பதிகாரம்)
- **Traditional Order:** 21
- **Period:** 400 CE - 600 CE
- **Confidence:** High
- **Notes:** Epic by Iḷaṅkō Aṭikaḷ. References to Gajabahu of Sri Lanka help dating.

### 22. Kambaramayanam (கம்பராமாயணம்)
- **Traditional Order:** 22
- **Period:** 1100 CE - 1200 CE
- **Confidence:** High
- **Notes:** Medieval epic by Kambar during Chola period.

## Scholarly Variations and Debates

### Major Chronological Debates:

1. **Tolkāppiyam Dating**
   - Conservative: 500 BCE - 200 BCE (grammar predates literature)
   - Liberal: 200 CE - 500 CE (systematization after Sangam)
   - Database uses: 500 BCE - 200 BCE (traditional view)

2. **Thirukkural Dating**
   - Range: 200 BCE - 800 CE across different scholars
   - Kamil Zvelebil: 450-500 CE
   - Traditional Tamil scholars: earlier (200 BCE - 100 CE)
   - Database uses: 300 CE - 500 CE (moderate consensus)

3. **Sangam Period Range**
   - Conservative: 300 BCE - 300 CE
   - Most accepted: 100 BCE - 250 CE
   - Database uses: 100 BCE - 250 CE for most works

## References

1. Zvelebil, Kamil (1973). *The Smile of Murugan: On Tamil Literature of South India*
2. Hart, George L. (1975). *The Poems of Ancient Tamil: Their Milieu and Their Sanskrit Counterparts*
3. Ramanujan, A.K. (1985). *Poems of Love and War*
4. Subrahmanian, N. (1966). *Sangam Polity*

## Disclaimer for Users

**Important:** The chronological dates in this database represent scholarly consensus where available, but Tamil literary dating remains an active area of research and debate. Different scholars propose varying chronologies based on:

- Linguistic analysis
- Historical references in texts
- Archaeological evidence
- Cross-references with other South Asian literature
- Paleographic evidence

Users should consult primary sources and academic literature for detailed chronological discussions. The dates provided here are approximate ranges intended to assist in general chronological sorting and should not be considered definitive.

## Implementation Notes

- Years are stored as integers (negative = BCE, positive = CE)
- Example: 100 BCE = -100, 200 CE = 200
- For sorting: ORDER BY chronology_start_year ASC (oldest first)
- Midpoint calculation: (chronology_start_year + chronology_end_year) / 2
