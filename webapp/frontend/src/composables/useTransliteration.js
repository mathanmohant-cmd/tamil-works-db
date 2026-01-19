import { ref, watch } from 'vue'
import Sanscript from '@indic-transliteration/sanscript'

/**
 * Composable for handling English to Tamil transliteration
 * Uses @indic-transliteration/sanscript library
 *
 * @returns {Object} - transliteration state and methods
 */
export function useTransliteration() {
  // Transliteration enabled by default
  const transliterationEnabled = ref(true)

  /**
   * Transliterate English text to Tamil
   * Uses ITRANS Dravidian scheme for full Tamil support
   * Examples:
   * - "aram" → "அரம்"
   * - "thirukkural" → "திருக்குறள்"
   * - "naalaayira" → "நாலாயிர"
   * - "azhagu" → "அழகு" (zh → ழ்)
   * - "sangam" → "சங்கம்" (ng → ங்)
   * - "mathan2" → "மதன்" (n2 → ன்)
   * - "mathann" → "மதன்" (nn → ன், alternative)
   *
   * @param {string} text - English text to transliterate
   * @returns {string} - Tamil text
   */
  const transliterate = (text) => {
    if (!text || !transliterationEnabled.value) {
      return text
    }

    try {
      // Preprocess: Convert 'nn' to 'n2' for alveolar ன்
      // This allows both 'nn' and 'n2' to produce ன்
      // Use word boundary awareness to avoid converting unintended double-n
      let preprocessedText = text

      // Replace 'nn' with 'n2' when:
      // 1. At end of word (followed by space or end of string)
      // 2. Before a consonant (not followed by a vowel)
      // This prevents false matches like "inn" → "in2" when user wants "இன்ன்"
      preprocessedText = preprocessedText.replace(/nn(?=[^aeiouAEIOU]|$)/g, 'n2')

      // Use ITRANS Dravidian scheme for full Tamil support
      const tamilText = Sanscript.t(preprocessedText, 'itrans_dravidian', 'tamil')
      return tamilText
    } catch (error) {
      console.error('Transliteration error:', error)
      return text
    }
  }

  /**
   * Toggle transliteration on/off
   */
  const toggleTransliteration = () => {
    transliterationEnabled.value = !transliterationEnabled.value
  }

  /**
   * Enable transliteration
   */
  const enableTransliteration = () => {
    transliterationEnabled.value = true
  }

  /**
   * Disable transliteration
   */
  const disableTransliteration = () => {
    transliterationEnabled.value = false
  }

  return {
    transliterationEnabled,
    transliterate,
    toggleTransliteration,
    enableTransliteration,
    disableTransliteration
  }
}
