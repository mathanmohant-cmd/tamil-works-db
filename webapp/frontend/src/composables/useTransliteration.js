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
   *
   * @param {string} text - English text to transliterate
   * @returns {string} - Tamil text
   */
  const transliterate = (text) => {
    if (!text || !transliterationEnabled.value) {
      return text
    }

    try {
      // Use ITRANS Dravidian scheme for full Tamil support (includes n2 → ன்)
      const tamilText = Sanscript.t(text, 'itrans_dravidian', 'tamil')
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
