import { ref } from 'vue'
import { getTransliterateSuggestions } from '@ai4bharat/indic-transliterate'

/**
 * Composable for handling English to Tamil transliteration using AI4Bharat
 * Uses @ai4bharat/indic-transliterate library with AI-powered IndicXlit models
 *
 * @returns {Object} - transliteration state and methods
 */
export function useAI4BharatTransliteration() {
  // Transliteration enabled by default
  const transliterationEnabled = ref(true)

  // Model loading state (API-based, so always "ready")
  const modelLoading = ref(false)
  const modelLoaded = ref(true) // API-based, no model to load
  const modelError = ref(null)

  // Performance metrics
  const modelLoadTime = ref(0) // N/A for API-based
  const lastTransliterationTime = ref(0)

  /**
   * Initialize the AI4Bharat model
   * Note: This is API-based, so no initialization needed
   * Kept for compatibility with the interface
   */
  const initializeModel = async () => {
    // API-based, no initialization needed
    modelLoaded.value = true
    console.log('AI4Bharat API ready (no model loading required)')
  }

  /**
   * Transliterate English text to Tamil using AI4Bharat API
   * Examples:
   * - "aram" → "அரம்"
   * - "thirukkural" → "திருக்குறள்"
   * - "naalaayira" → "நாலாயிர"
   * - "azhagu" → "அழகு" (zh → ழ்)
   * - "sangam" → "சங்கம்" (ng → ங்)
   *
   * @param {string} text - English text to transliterate
   * @returns {Promise<string>} - Tamil text
   */
  const transliterate = async (text) => {
    if (!text || !transliterationEnabled.value) {
      return text
    }

    try {
      const startTime = performance.now()

      // Call AI4Bharat API to get transliteration suggestions
      const suggestions = await getTransliterateSuggestions(text, {
        numOptions: 5,
        showCurrentWordAsLastSuggestion: false,
        lang: 'ta' // Tamil
      })

      lastTransliterationTime.value = performance.now() - startTime

      // Return the first (best) suggestion, or original text if no suggestions
      if (suggestions && suggestions.length > 0) {
        return suggestions[0]
      }

      return text
    } catch (error) {
      console.error('AI4Bharat transliteration error:', error)
      modelError.value = error.message
      return text
    }
  }

  /**
   * Transliterate synchronously (for compatibility)
   * Note: AI4Bharat is async-only, so this returns original text
   *
   * @param {string} text - English text to transliterate
   * @returns {string} - Original text (AI4Bharat requires async)
   */
  const transliterateSync = (text) => {
    console.warn('AI4Bharat transliteration is async-only, use transliterate() instead')
    return text
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
    // State
    transliterationEnabled,
    modelLoading,
    modelLoaded,
    modelError,
    modelLoadTime,
    lastTransliterationTime,

    // Methods
    initializeModel,
    transliterate,
    transliterateSync,
    toggleTransliteration,
    enableTransliteration,
    disableTransliteration
  }
}
