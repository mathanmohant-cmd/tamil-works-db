# Tamil Transliteration Rules Guide

## Overview

This guide explains the English to Tamil transliteration rules used in the Tamil Literature Search application.

## Files

- **`translit_rules.json`** - Complete transliteration mapping (English → Tamil)
- **`composables/useTransliteration.js`** - Transliteration composable (currently uses Sanscript library)
- **Source library:** `@indic-transliteration/sanscript` (ITRANS scheme)

## Current Implementation

The application currently uses the **`@indic-transliteration/sanscript`** library with the **ITRANS scheme**. The rules are embedded in the library code.

The `translit_rules.json` file is an **extracted reference** of the current rules for easy viewing and potential customization.

## How to Use the Rules Reference

### Vowels

| English | Tamil | Alternates | Example |
|---------|-------|------------|---------|
| a | அ | - | aram → அரம் |
| aa, A | ஆ | A | Azhagu → ஆழகு |
| i | இ | - | iyal → இயல் |
| ii, I, ee | ஈ | I, ee | Isan → ஈசன் |
| u | உ | - | uyir → உயிர் |
| uu, U, oo | ஊ | U, oo | Urvam → ஊர்வம் |
| e | ஏ | - | eLuthu → ஏழுது |
| è | எ | - | - |
| ai | ஐ | - | aiyya → ஐயா |
| o | ஓ | - | Oviyam → ஓவியம் |
| ò | ஒ | - | - |
| au | ஔ | - | - |

### Consonants (Common)

| English | Tamil | Notes | Example |
|---------|-------|-------|---------|
| k, g | க | k and g both map to க | kallal → கள்ளல் |
| ch, c | ச | ch or c | chella → செல்ல |
| j | ஜ | Grantha letter | jalam → ஜலம் |
| t | த | Dental t | thamizh → தமிழ் |
| p, b | ப | p and b both map to ப | paal → பால் |
| m | ம | - | mozhi → மொழி |
| y | ய | - | yaar → யார் |
| r | ர | - | ram → ரம் |
| l | ல | - | lakshmi → லக்ஷ்மி |
| v, w | வ | v or w | vazhi → வழி |
| n | ந | Dental n | nalam → நலம் |
| s | ஸ | Grantha letter | satya → ஸத்ய |
| sh | ஶ | Grantha letter | shiva → ஶிவ |
| h | ஹ | Grantha letter | hari → ஹரி |

### Special Tamil Letters

| English | Tamil | Notes | Example |
|---------|-------|-------|---------|
| zh | ழ | Unique to Tamil | azhagu → அழகு |
| R | ற | Alveolar r | aRam → அறம் |
| L | ள | Retroflex l | vaLLuvar → வள்ளுவர் |
| ng | ங | Velar nasal | sangam → சங்கம் |
| ny | ஞ | Palatal nasal | gnyaanam → ஞானம் |
| N | ண | Retroflex n | kaN → கண் |
| T | ட | Retroflex t | Tamilar → டமிழர் |
| D | ட | Same as T | Daivam → டைவம் |
| n_ | ன | Alveolar n | - |

### Special Marks

| English | Tamil | Notes |
|---------|-------|-------|
| M | ம் | Anusvara (rarely used in Tamil) |
| H | ஃ | Aytham |
| ் | ் | Pulli (virama) |

### Numbers

| English | Tamil |
|---------|-------|
| 0 | ௦ |
| 1 | ௧ |
| 2 | ௨ |
| 3 | ௩ |
| 4 | ௪ |
| 5 | ௫ |
| 6 | ௬ |
| 7 | ௭ |
| 8 | ௮ |
| 9 | ௯ |

## Common Examples

```
aram           → அரம்
thirukkural    → திருக்குறள்
naalaayira     → நாலாயிர
azhagu         → அழகு
sangam         → சங்கம்
thirumuRai     → திருமுறை
kambaramayanam → கம்பராமாயணம்
tolkappiyam    → தொல்காப்பியம்
silappathikaram→ சிலப்பதிகாரம்
manimegalai    → மணிமேகலை
vaLLuvar       → வள்ளுவர்
```

## Important Notes

1. **Case Sensitivity:**
   - Lowercase: dental letters (t, d, n)
   - Uppercase: retroflex letters (T, D, N)
   - Capital R → ற (alveolar r)
   - Small r → ர (regular r)

2. **Long Vowels:**
   - Use double letters: aa, ii, uu
   - OR use capitals: A, I, U
   - Both work: "thirukkural" or "thirukkurAl"

3. **Special Tamil Sounds:**
   - **ழ (zh):** Unique Tamil letter - use "zh"
   - **ற (R):** Alveolar r - use capital "R"
   - **ன (n_):** Alveolar n - use "n_"
   - **ள (L):** Retroflex l - use capital "L"

4. **Nasal Sounds:**
   - **ங (ng):** Like "ng" in "sing"
   - **ஞ (ny):** Like "ny" in "canyon"
   - **ண (N):** Retroflex n - capital N

## How to Customize Rules

### Option 1: Modify the JSON file

Edit `translit_rules.json` to change mappings. For example:

```json
{
  "consonants": {
    "z": "ழ"  // Add 'z' as alternate for ழ instead of just 'zh'
  }
}
```

### Option 2: Create custom implementation

To use the custom JSON file instead of Sanscript library:

1. **Create new transliteration function** in `useTransliteration.js`
2. **Import the JSON rules**
3. **Implement custom mapping logic**
4. **Replace Sanscript.t() calls**

Example implementation:

```javascript
import translitRules from './translit_rules.json'

const customTransliterate = (text) => {
  // Implement custom logic here using translitRules
  // This is more work but gives you full control
}
```

### Option 3: Override Sanscript library (not recommended)

Directly modify: `node_modules/@indic-transliteration/sanscript/sanscript.js`

⚠️ **Warning:** Changes will be lost when you run `npm install`

## Testing Your Changes

1. Edit `translit_rules.json` with your custom mappings
2. If using custom implementation, update `useTransliteration.js`
3. Test in the search interface
4. Verify with common Tamil words

## Common Use Cases

### Search for Literary Works

```
thirukkural     → திருக்குறள்
naalaayira      → நாலாயிர
kambar          → கம்பர்
silappathikaram → சிலப்பதிகாரம்
thirumurai      → திருமுறை
```

### Search for Concepts

```
aram     → அரம் (virtue)
poruL    → பொருள் (meaning/wealth)
inbam    → இன்பம் (pleasure)
veedu    → வீடு (liberation)
azhagu   → அழகு (beauty)
kaadhal  → காதல் (love)
```

### Search for Deities

```
shiva      → ஶிவ
murugan    → முருகன்
vishNu     → விஷ்ணு
kaNNan     → கண்ணன்
amman      → அம்மன்
```

## Troubleshooting

### Issue: Letters not appearing correctly

- Check that you're using correct case (T vs t, N vs n, R vs r)
- Verify special combinations (zh for ழ, ng for ங)

### Issue: Long vowels not working

- Use double letters (aa, ii, uu) or capitals (A, I, U)
- "thirukkural" ✓ or "thirukkurAl" ✓

### Issue: Special letters missing

- Use "zh" for ழ (not "z")
- Use "R" (capital) for ற
- Use "ng" for ங
- Use "ny" for ஞ

## References

- **ITRANS Scheme:** [https://en.wikipedia.org/wiki/ITRANS](https://en.wikipedia.org/wiki/ITRANS)
- **Sanscript Library:** [https://github.com/sanskrit/sanscript.js](https://github.com/sanskrit/sanscript.js)
- **Tamil Script:** [https://en.wikipedia.org/wiki/Tamil_script](https://en.wikipedia.org/wiki/Tamil_script)

## Questions?

For questions about transliteration rules or customization, refer to:
- This guide
- `translit_rules.json` (complete reference)
- `useTransliteration.js` (implementation)
- Sanscript library documentation
