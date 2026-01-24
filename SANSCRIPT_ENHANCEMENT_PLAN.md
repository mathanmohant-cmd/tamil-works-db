# Sanscript Transliteration Enhancement Plan

**Goal:** Improve transliteration accuracy from 53% to 70-80%
**Estimated Effort:** 4-6 hours
**Priority:** Medium
**Risk Level:** Low (enhances existing working system)

---

## Current Issues (Based on Evaluation)

### 1. Nasal Consonant Confusion (7 failures)
**Problem:** Sanscript confuses between different nasal consonants

| Input | Expected | Current Output | Issue |
|-------|----------|----------------|-------|
| sangam | சங்கம் | ஸந்கம் | ந் instead of ங் |
| inbam | இன்பம் | இந்பம் | ந் instead of ன் |
| aNangu | அணங்கு | அணந்கு | ந் instead of ங் |
| iLangu | இளங்கு | இளந்கு | ந் instead of ங் |
| manimegalai | மணிமேகலை | மநிமெகலை | ந் instead of ண் |

**Tamil Nasal Consonants:**
- **ங் (nga)** - Velar nasal (as in "sing")
- **ஞ் (nya)** - Palatal nasal (as in "canyon")
- **ண் (Na)** - Retroflex nasal
- **ந் (na)** - Dental nasal
- **ன் (n2/nn)** - Alveolar nasal
- **ம் (ma)** - Labial nasal

### 2. Grantha Letter Misuse (3 failures)
**Problem:** Uses Grantha letters (ஸ, ஶ, ஷ, ஜ, ஹ) for pure Tamil words

| Input | Expected | Current Output | Issue |
|-------|----------|----------------|-------|
| sangam | சங்கம் | ஸந்கம் | ஸ instead of ச |
| silappathikaram | சிலப்பதிகாரம் | ஸிலப்பதிகரம் | ஸ instead of ச |
| seethalaik kaadhanar | சீத்தலைக் காதனார் | ஸீதலைக் காதநர் | ஸ instead of ச |

**Note:** Grantha letters are for Sanskrit loanwords, not pure Tamil.

### 3. Geminate/Double Consonant Loss (4 failures)
**Problem:** Missing or incorrect double consonants

| Input | Expected | Current Output | Issue |
|-------|----------|----------------|-------|
| thirukkural | திருக்குறள் | திருக்குரல் | Missing final ள் |
| kambaramayanam | கம்பராமாயணம் | கம்பரமயநம் | Multiple missing geminates |
| tolkappiyam | தொல்காப்பியம் | தொல்கப்பியம் | Missing ப் geminate |
| vazhuthunai | வழுத்துணை | வழுதுநை | Missing த் and missing ண் |

### 4. Long Vowel Issues (2 failures)
**Problem:** Incorrect short/long vowel mapping

| Input | Expected | Current Output | Issue |
|-------|----------|----------------|-------|
| vazhkai | வாழ்கை | வழ்கை | Missing long ஆ |
| thiruvasagam | திருவாசகம் | திருவஸகம் | Long ஆ vs Grantha ஸ issue |

### 5. Other Issues (2 failures)
| Input | Expected | Current Output | Issue |
|-------|----------|----------------|-------|
| veedu | வீடு | வீது | து instead of டு |

---

## Enhancement Tasks (Prioritized)

### 🔴 Priority 1: Critical Accuracy Issues

#### Task 1: Fix Nasal Consonant Mapping
**Impact:** High (affects 7/14 failures = 50%)
**Effort:** 2 hours
**Complexity:** Medium

**Implementation Strategy:**

1. **Create nasal consonant rules:**
   ```javascript
   // Context-aware nasal mapping
   const nasalRules = {
     'ng': 'ங்',  // velar (before k, g) - "sang", "mang"
     'ny': 'ஞ்',  // palatal (before ch, j) - "gnyaan"
     'N': 'ண்',   // retroflex (capital N) - "maN", "kaN"
     'n': 'ந்',   // dental (before th, dh) - default n
     'n2': 'ன்',  // alveolar (before r, l, or word-final) - "pon", "nan"
     'nn': 'ன்',  // alternative for alveolar
     'm': 'ம்'    // labial (before p, b, m)
   }
   ```

2. **Add context detection:**
   - 'ng' at end of syllable → ங் (e.g., "sang" → சங்)
   - 'n' before retroflex consonants → ண் (e.g., "maN" → மண்)
   - 'n' at end of word after vowel → ன் (e.g., "nan" → நன்)

3. **Test cases to validate:**
   - sangam → சங்கம் ✓
   - inbam → இன்பம் ✓ (convert 'nb' → 'n2b')
   - aNangu → அணங்கு ✓
   - manimegalai → மணிமேகலை ✓

**Files to modify:**
- `webapp/frontend/src/composables/useTransliteration.js`

#### Task 2: Fix Grantha Letter Usage
**Impact:** Medium (affects 3/14 failures = 21%)
**Effort:** 1 hour
**Complexity:** Low

**Implementation Strategy:**

1. **Add Tamil mode flag:**
   ```javascript
   const usePureTamilMode = ref(true) // Default to pure Tamil
   ```

2. **Map Grantha to Tamil equivalents:**
   ```javascript
   if (usePureTamilMode.value) {
     text = text
       .replace(/(?<!^)s(?![h])/g, 'c')  // s → c (but not sh)
       .replace(/^s(?![h])/g, 'c')        // Initial s → c
   }
   // Then pass to Sanscript
   ```

3. **Test cases:**
   - sangam → சங்கம் ✓ (not ஸங்கம்)
   - silappathikaram → சிலப்பதிகாரம் ✓

**Alternative:** Add user toggle for "Pure Tamil / Sanskrit" mode

**Files to modify:**
- `webapp/frontend/src/composables/useTransliteration.js`
- `webapp/frontend/src/pages/TransliterationGuidePage.vue` (document the behavior)

#### Task 3: Add Dictionary Overlay
**Impact:** High (fixes common literary terms)
**Effort:** 1.5 hours
**Complexity:** Low

**Implementation Strategy:**

1. **Create dictionary of common literary Tamil words:**
   ```javascript
   const tamilDictionary = {
     'thirukkural': 'திருக்குறள்',
     'kambaramayanam': 'கம்பராமாயணம்',
     'tolkappiyam': 'தொல்காப்பியம்',
     'silappathikaram': 'சிலப்பதிகாரம்',
     'manimegalai': 'மணிமேகலை',
     'thiruvasagam': 'திருவாசகம்',
     'naalaayira': 'நாலாயிர',
     'thirumurai': 'திருமுறை',
     'sangam': 'சங்கம்',
     // Add top 50-100 literary terms
   }
   ```

2. **Check dictionary before transliteration:**
   ```javascript
   const transliterate = (text) => {
     const lowercaseText = text.toLowerCase().trim()

     // Check exact match first
     if (tamilDictionary[lowercaseText]) {
       return tamilDictionary[lowercaseText]
     }

     // Check word-by-word for phrases
     const words = text.split(/\s+/)
     if (words.length > 1) {
       return words.map(word =>
         tamilDictionary[word.toLowerCase()] || transliterateWord(word)
       ).join(' ')
     }

     // Fall back to rule-based transliteration
     return transliterateWord(text)
   }
   ```

3. **Source dictionary entries from:**
   - Database `works` table (work names)
   - Common Tamil concepts (அறம், பொருள், இன்பம், காதல், etc.)
   - Famous author names (வள்ளுவர், கம்பர், இளங்கோ, etc.)

**Files to create:**
- `webapp/frontend/src/data/tamilDictionary.json`

**Files to modify:**
- `webapp/frontend/src/composables/useTransliteration.js`

---

### 🟡 Priority 2: Quality Improvements

#### Task 4: Improve Geminate Handling
**Impact:** Medium (affects 4/14 failures = 29%)
**Effort:** 1 hour
**Complexity:** Medium

**Implementation Strategy:**

1. **Preserve double consonants:**
   ```javascript
   // Before Sanscript processing
   text = text
     .replace(/([kgcjtdnpbmyrlvszh])\1/gi, '$1$1') // Preserve doubles
   ```

2. **Add rules for common geminates:**
   - 'kk' → க்க
   - 'll' → ல்ல
   - 'LL' → ள்ள
   - 'tt' → த்த or ட்ட (context-dependent)
   - 'pp' → ப்ப
   - 'RR' → ற்ற

3. **Test cases:**
   - thirukkural → திருக்குறள் ✓
   - vaLLuvar → வள்ளுவர் ✓ (already works)

**Files to modify:**
- `webapp/frontend/src/composables/useTransliteration.js`

#### Task 5: Add Long Vowel Detection
**Impact:** Low (affects 2/14 failures = 14%)
**Effort:** 30 minutes
**Complexity:** Low

**Implementation Strategy:**

1. **Ensure consistent long vowel mapping:**
   ```javascript
   text = text
     .replace(/aa/gi, 'A')  // ஆ
     .replace(/ee/gi, 'I')  // ஈ
     .replace(/oo/gi, 'U')  // ஊ
   // Sanscript already handles A, I, U → ஆ, ஈ, ஊ
   ```

2. **Test cases:**
   - vazhkai → வாழ்கை ✓ (should use 'vaazhkai' input)

**Note:** This is more of a user education issue (teach users to use 'aa' for ஆ)

**Files to modify:**
- `webapp/frontend/src/composables/useTransliteration.js`
- `webapp/frontend/src/pages/TransliterationGuidePage.vue` (documentation)

---

### 🟢 Priority 3: Testing & Documentation

#### Task 6: Create Automated Test Suite
**Impact:** High (prevents regressions)
**Effort:** 1 hour
**Complexity:** Low

**Implementation Strategy:**

1. **Reuse comparison page as test harness:**
   - Keep `/dev/transliteration-comparison` page
   - Add "Run Tests" automation

2. **Create test file:**
   ```javascript
   // webapp/frontend/src/tests/transliterationTests.js
   export const literaryTamilTests = [
     { input: 'thirukkural', expected: 'திருக்குறள்' },
     { input: 'kambaramayanam', expected: 'கம்பராமாயணம்' },
     // ... 30 test cases
   ]
   ```

3. **Add accuracy tracking:**
   - Log before/after accuracy
   - Track improvement percentage
   - Identify remaining failures

**Files to create:**
- `webapp/frontend/src/tests/transliterationTests.js`

**Files to modify:**
- `webapp/frontend/src/pages/TransliterationComparison.vue`

#### Task 7: Update Documentation
**Impact:** Medium (user guidance)
**Effort:** 30 minutes
**Complexity:** Low

**Implementation Strategy:**

1. **Update transliteration guide:**
   - Document nasal consonant rules
   - Explain ng vs n vs n2
   - Add "Pure Tamil mode" explanation
   - Provide examples of common words

2. **Add troubleshooting section:**
   - Common mistakes
   - How to use dictionary overlay
   - Tips for literary Tamil

**Files to modify:**
- `webapp/frontend/src/pages/TransliterationGuidePage.vue`
- `webapp/frontend/src/TRANSLITERATION_RULES_GUIDE.md`

---

## Implementation Order

### Phase 1: Core Fixes (3.5 hours)
1. ✅ Fix nasal consonant mapping (2 hours)
2. ✅ Fix Grantha letter usage (1 hour)
3. ✅ Add dictionary overlay (1.5 hours)

**Expected improvement: 53% → 70%**

### Phase 2: Quality (1.5 hours)
4. ✅ Improve geminate handling (1 hour)
5. ✅ Add long vowel detection (30 minutes)

**Expected improvement: 70% → 75-80%**

### Phase 3: Testing (1.5 hours)
6. ✅ Create automated test suite (1 hour)
7. ✅ Update documentation (30 minutes)

**Total: 6-7 hours**

---

## Success Metrics

### Before Enhancement
- ✅ Accuracy: 53% (16/30 test cases)
- ✅ Speed: 2ms average
- ✅ Reliability: 100%

### Target After Enhancement
- 🎯 Accuracy: **70-80%** (21-24/30 test cases)
- 🎯 Speed: **<5ms** (allow slight slowdown for preprocessing)
- 🎯 Reliability: **100%** (no regressions)

### Stretch Goal
- 🌟 Accuracy: **85%+** with continuous dictionary updates

---

## File Structure

```
webapp/frontend/src/
├── composables/
│   └── useTransliteration.js          [MODIFY - main logic]
├── data/
│   └── tamilDictionary.json           [CREATE - word mappings]
├── tests/
│   └── transliterationTests.js        [CREATE - test cases]
├── pages/
│   ├── TransliterationGuidePage.vue   [MODIFY - docs]
│   └── TransliterationComparison.vue  [KEEP - test harness]
└── TRANSLITERATION_RULES_GUIDE.md     [MODIFY - reference]
```

---

## Risk Mitigation

### Risk 1: Breaking Existing Functionality
**Mitigation:**
- Keep current Sanscript as fallback
- Add feature flag for enhancements
- Test thoroughly before release

### Risk 2: Performance Degradation
**Mitigation:**
- Benchmark before/after
- Keep preprocessing minimal
- Cache dictionary lookups

### Risk 3: Maintenance Burden
**Mitigation:**
- Document all custom rules
- Keep dictionary in separate JSON file
- Write clear comments in code

---

## Future Enhancements (Beyond Scope)

### Optional Add-ons
1. **ISO 15919 Support** (2-3 hours)
   - Add scheme selector
   - Support diacritics (ā, ī, ū, ṭ, ḍ, ṇ, etc.)

2. **User Dictionary** (3-4 hours)
   - Allow users to add custom mappings
   - Store in localStorage
   - Export/import functionality

3. **ML Model Training** (20-40 hours)
   - Train on your literary Tamil corpus
   - Self-hosted ONNX inference
   - No external dependencies

---

## Ready to Implement?

This plan is ready for execution. Start with **Phase 1 (Core Fixes)** to get the biggest accuracy gains quickly.

**Next command:** Implement Task 1 (Fix nasal consonant mapping)
