import { ref, computed } from 'vue'
import api from '../api.js'

// Shared search state (singleton pattern for cross-component reactivity)
const searchQuery = ref('')
const matchType = ref('partial')
const wordPosition = ref('beginning')
const sortBy = ref('canonical')
const searchResults = ref(null)
const loading = ref(false)
const error = ref(null)
const expandedWords = ref(new Set())
const loadingWord = ref(null)
const loadedOccurrences = ref({}) // Track loaded occurrences per word with offset
const wordListSortBy = ref('alphabetical')

// Autocomplete
const autocompleteResults = ref([])
const showAutocomplete = ref(false)

// Export menus
const showWordsExportMenu = ref(false)
const currentExportWordText = ref(null)
const currentExportVersesWordText = ref(null)

// Verse view
const showVerseView = ref(false)
const selectedVerseId = ref(null)
const verseViewSearchWord = ref('')
const clickedOccurrenceWordId = ref(null)

export function useSearchState() {
  // Computed: Unique words with aggregated data
  const uniqueWords = computed(() => {
    if (!searchResults.value || !searchResults.value.unique_words) {
      return []
    }

    // Sort based on wordListSortBy
    const words = [...searchResults.value.unique_words]

    switch (wordListSortBy.value) {
      case 'alphabetical':
        return words.sort((a, b) => a.word_text.localeCompare(b.word_text, 'ta'))
      case 'count_high_to_low':
        return words.sort((a, b) => b.count - a.count)
      case 'count_low_to_high':
        return words.sort((a, b) => a.count - b.count)
      default:
        return words
    }
  })

  // Computed: Search summary
  const searchSummary = computed(() => {
    if (!searchResults.value) return ''

    const distinctWords = searchResults.value.unique_words.length
    const totalUsage = searchResults.value.total_count || 0

    // Count unique works
    const worksSet = new Set()
    searchResults.value.unique_words.forEach(word => {
      if (word.work_breakdown) {
        word.work_breakdown.forEach(item => {
          worksSet.add(item.work_name)
        })
      }
    })
    const worksCount = worksSet.size

    // Count unique verses from unique_words metadata
    // Use verse_count from backend (works even when results array is empty with limit=0)
    let versesCount = 0
    searchResults.value.unique_words.forEach(word => {
      versesCount += (word.verse_count || 0)
    })

    return `${worksCount} Work${worksCount !== 1 ? 's' : ''} | ${versesCount} Verse${versesCount !== 1 ? 's' : ''} | ${distinctWords} Distinct Word${distinctWords !== 1 ? 's' : ''} | ${totalUsage} Usage`
  })

  // Clear search
  const clearSearch = () => {
    searchQuery.value = ''
    searchResults.value = null
    expandedWords.value = new Set()
    loadedOccurrences.value = {}
    error.value = null
  }

  // Get occurrences for a specific word
  const getWordOccurrences = (wordText) => {
    if (!searchResults.value) return []
    return searchResults.value.results.filter(r => r.word_text === wordText)
  }

  // Get sorted occurrences for a word
  const getSortedWordOccurrences = (wordText) => {
    const occurrences = getWordOccurrences(wordText)
    // Note: Backend should handle sorting based on sortBy parameter
    // Frontend should NOT re-sort the results
    return occurrences
  }

  // Check if word has more occurrences to load
  const hasMoreOccurrences = (wordText) => {
    const tracking = loadedOccurrences.value[wordText]
    if (!tracking) return true

    const wordInfo = searchResults.value.unique_words?.find(w => w.word_text === wordText)
    const totalCount = wordInfo?.count || 0
    const loadedCount = getWordOccurrences(wordText).length

    return loadedCount < totalCount
  }

  // Get work counts for a word
  const getWorkCounts = (wordText) => {
    // First try to get from unique_words metadata
    const wordInfo = searchResults.value.unique_words?.find(w => w.word_text === wordText)

    if (wordInfo && wordInfo.work_breakdown) {
      // Aggregate by work_name
      const workCounts = {}
      wordInfo.work_breakdown.forEach(item => {
        const workName = item.work_name
        if (!workCounts[workName]) {
          workCounts[workName] = {
            work_name: workName,
            work_name_tamil: item.work_name_tamil,
            count: 0
          }
        }
        workCounts[workName].count += item.count
      })
      return Object.values(workCounts)
    }

    // Fallback: calculate from loaded occurrences
    const occurrences = getWordOccurrences(wordText)
    const workCounts = {}

    occurrences.forEach(result => {
      const workName = result.work_name
      const workNameTamil = result.work_name_tamil

      if (!workCounts[workName]) {
        workCounts[workName] = {
          work_name: workName,
          work_name_tamil: workNameTamil,
          count: 0
        }
      }
      workCounts[workName].count++
    })

    return Object.values(workCounts)
  }

  // Open verse view
  const openVerseView = (verseId, searchWord = '', wordId = null) => {
    selectedVerseId.value = verseId
    verseViewSearchWord.value = searchWord
    clickedOccurrenceWordId.value = wordId
    showVerseView.value = true
  }

  // Close verse view
  const closeVerseView = () => {
    showVerseView.value = false

    // Scroll back to the clicked occurrence if available
    if (clickedOccurrenceWordId.value) {
      setTimeout(() => {
        const element = document.querySelector(`[data-word-id="${clickedOccurrenceWordId.value}"]`)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }, 100)
    }
  }

  return {
    // State
    searchQuery,
    matchType,
    wordPosition,
    sortBy,
    searchResults,
    loading,
    error,
    expandedWords,
    loadingWord,
    loadedOccurrences,
    wordListSortBy,
    autocompleteResults,
    showAutocomplete,
    showWordsExportMenu,
    currentExportWordText,
    currentExportVersesWordText,
    showVerseView,
    selectedVerseId,
    verseViewSearchWord,
    clickedOccurrenceWordId,

    // Computed
    uniqueWords,
    searchSummary,

    // Methods
    clearSearch,
    getWordOccurrences,
    getSortedWordOccurrences,
    hasMoreOccurrences,
    getWorkCounts,
    openVerseView,
    closeVerseView
  }
}
