# Collection ID Scheme

This document defines the collection IDs used across all devotional literature parsers.

## Main Collections

- **321**: திருமுறை (Thirumurai) - Main collection for all 12 Thirumurai books
- **322**: நாலாயிரத் திவ்விய பிரபந்தம் (Naalayira Divya Prabandham) - Main Vaishnavite collection

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

## Notes

- Collection 3218 (8th Thirumurai) is shared by two works, so neither delete script removes the collection
- Devaram has the most complex structure with 3-level collection hierarchy
- All collection IDs use dynamic queries, not hardcoded values in work metadata or bulk insert methods
