<template>
  <div class="search-results" v-if="searchResults">
    <!-- Results Header with Summary -->
    <div class="results-header">
      <div class="search-summary-panel">
        <div class="searched-word-display">
          Searched for: <strong>{{ searchResults.search_term }}</strong>
          <span class="separator">;</span>
          in:
          <span
            v-if="isSelectMode"
            @click="openSearchFilterPanel"
            class="search-context-link"
            title="Click to open filter panel"
          >
            {{ searchContextText }}
          </span>
          <span v-else class="search-context-text">{{ searchContextText }}</span>
        </div>
        <div class="summary-with-export">
          <span>Found: {{ searchSummary }}. Expand for details</span>
          <button @click="showWordsExportMenu = true" class="export-button-combined" title="Export list of found words">
            📥 Export Words
          </button>
        </div>
      </div>
    </div>

    <!-- Word List Sort Options -->
    <div class="word-list-sort-options">
      <span class="filter-label">Sort by:</span>
      <label>
        <input type="radio" v-model="wordListSortBy" value="alphabetical" />
        அ - ன 
      </label>
      <label>
        <input type="radio" v-model="wordListSortBy" value="count_high_to_low" />
        Count &#9660;
      </label>
      <label>
        <input type="radio" v-model="wordListSortBy" value="count_low_to_high" />
        Count &#9650;
      </label>
    </div>

    <!-- Word List with Expandable Details -->
    <div class="word-list-container">
      <div
        v-for="(word, index) in uniqueWords"
        :key="word.word_text"
        class="word-item-expandable"
        :class="{ expanded: expandedWords.has(word.word_text) }"
      >
        <!-- Word Header Row -->
        <div class="word-header-row">
          <div class="word-info">
            <span class="word-number">{{ index + 1 }}.</span>
            <a
              :href="`https://dsal.uchicago.edu/cgi-bin/app/tamil-lex_query.py?qs=${encodeURIComponent(word.word_text)}&searchhws=yes&matchtype=default`"
              target="_blank"
              class="word-text word-link"
              @click.stop
              title="Link to UChicago Combined Thamizh Dictionary"
            >
              {{ word.word_text }}
            </a>
            <span class="word-count-badge">({{ word.count }})</span>
          </div>
          <div class="word-actions">
            <button
              @click="toggleWordExpansion(word.word_text)"
              class="expand-collapse-button"
              :class="{ expanded: expandedWords.has(word.word_text) }"
              :title="expandedWords.has(word.word_text) ? 'Collapse' : 'Expand to see the lines'"
            >
              <span class="expand-icon">
                <span class="chevron-icon" :class="expandedWords.has(word.word_text) ? 'chevron-down' : 'chevron-up'"></span>
              </span>
            </button>
          </div>
        </div>

        <!-- Expandable Occurrences Section -->
        <div v-if="expandedWords.has(word.word_text)" class="word-expanded-content">
          <!-- Selected Word Summary: Works, Verses, Usage -->
          <div class="expanded-summary">
            <div class="summary-counts">
              <span class="summary-item">{{ word.count }} Usage</span>
              <span class="summary-divider">|</span>
              <span class="summary-item">{{ getWorkCounts(word.word_text).length }} Work{{ getWorkCounts(word.word_text).length !== 1 ? 's' : '' }}</span>
              <span class="summary-divider">|</span>
              <span class="summary-item">{{ word.verse_count || 0 }} Verse{{ (word.verse_count || 0) !== 1 ? 's' : '' }}</span>
            </div>
            <div class="export-buttons-group">
              <span class="export-label">Export</span>
              <button
                @click="showLinesExportMenu(word.word_text)"
                class="export-button-combined"
                title="Export all lines for this word"
              >
                📄 Lines
              </button>
              <button
                @click="showVersesExportMenu(word.word_text)"
                class="export-button-combined"
                title="Export complete verses for this word"
              >
                📜 Verses
              </button>
            </div>
          </div>

          <!-- Sort Lines Options -->
          <div class="lines-sort-options">
            <span class="filter-label">Sort by:</span>
            <label>
              <input type="radio" v-model="sortBy" value="canonical" />
              Canonical
            </label>
            <label>
              <input type="radio" v-model="sortBy" value="chronological" />
              Chronology
            </label>
            <label>
              <input type="radio" v-model="sortBy" value="alphabetical" />
              அ-ன
            </label>
          </div>

          <!-- Loading State -->
          <div v-if="loadingWord === word.word_text || sortingWord === word.word_text" class="loading-occurrences">
            {{ sortingWord === word.word_text ? 'Sorting...' : 'Loading occurrences...' }}
          </div>

          <!-- Occurrences List -->
          <div v-else class="occurrences-list">
            <div
              v-for="(result, occIndex) in getSortedWordOccurrences(word.word_text)"
              :key="result.word_id"
              :data-word-id="result.word_id"
              class="occurrence-item"
            >
              <div class="occurrence-content">
                <div class="occurrence-metadata">
                  <span class="occurrence-number">{{ occIndex + 1 }}.</span>
                  <span
                    class="work-name"
                    :title="getWorkChronologyTooltip(result)"
                  >
                    {{ result.work_name_tamil }}
                  </span>
                  <template v-if="cleanHierarchyPath(result.hierarchy_path_tamil || result.hierarchy_path)">
                    <span class="separator"> • </span>
                    <span class="hierarchy-path">{{ cleanHierarchyPath(result.hierarchy_path_tamil || result.hierarchy_path) }}</span>
                  </template>
                  <span class="separator"> • </span>
                  <span class="verse-link-text" @click="openVerseView(result.verse_id, word.word_text, result.word_id)" title="Click to view full verse">{{ formatVerseAndLine(result, false) }}</span>
                </div>
                <div class="occurrence-line" v-html="highlightWord(result.line_text, word.word_text)"></div>
              </div>
            </div>

            <!-- Load More Button if needed -->
            <div v-if="hasMoreOccurrences(word.word_text)" class="load-more-container">
              <button
                @click="loadMoreOccurrences(word.word_text)"
                class="load-more-button"
                :disabled="loadingWord === word.word_text || sortingWord === word.word_text"
              >
                {{ sortingWord === word.word_text ? 'Sorting...' : (loadingWord === word.word_text ? 'Loading...' : 'Load More') }}
              </button>
            </div>
          </div>

          <!-- Collapse Footer 
          <div class="collapse-footer">
            <button
              @click="toggleWordExpansion(word.word_text)"
              class="expand-collapse-button collapse-footer-button"
              title="Collapse"
            >
              <span class="expand-icon">
                <span class="chevron-icon chevron-up"></span>
              </span>
            </button>
          </div>
          -->
        </div>
      </div>
    </div>

    <!-- Export Words Menu -->
    <div v-if="showWordsExportMenu" class="export-modal" @click="showWordsExportMenu = false">
      <div class="export-modal-content" @click.stop>
        <h3>Export Found Words</h3>
        <button @click="exportWords('csv')" class="export-modal-option">
          📊 Export as CSV
        </button>
        <button @click="exportWords('txt')" class="export-modal-option">
          📄 Export as TXT
        </button>
        <button @click="showWordsExportMenu = false" class="export-modal-cancel">
          Cancel
        </button>
      </div>
    </div>

    <!-- Export Lines Menu -->
    <div v-if="currentExportWordText" class="export-modal" @click="currentExportWordText = null">
      <div class="export-modal-content" @click.stop>
        <h3>Export Lines for "{{ currentExportWordText }}"</h3>
        <button @click="exportWordLines('csv', currentExportWordText)" class="export-modal-option">
          📊 Export as CSV
        </button>
        <button @click="exportWordLines('txt', currentExportWordText)" class="export-modal-option">
          📄 Export as TXT
        </button>
        <button @click="currentExportWordText = null" class="export-modal-cancel">
          Cancel
        </button>
      </div>
    </div>

    <!-- Export Verses Menu -->
    <div v-if="currentExportVersesWordText" class="export-modal" @click="currentExportVersesWordText = null">
      <div class="export-modal-content" @click.stop>
        <h3>Export Verses for "{{ currentExportVersesWordText }}"</h3>
        <button @click="exportWordVerses('csv', currentExportVersesWordText)" class="export-modal-option">
          📊 Export as CSV
        </button>
        <button @click="exportWordVerses('txt', currentExportVersesWordText)" class="export-modal-option">
          📄 Export as TXT
        </button>
        <button @click="currentExportVersesWordText = null" class="export-modal-cancel">
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSearchState } from '../../../composables/useSearchState.js'
import { useFilterState } from '../../../composables/useFilterState.js'
import api from '../../../api.js'

const router = useRouter()
const route = useRoute()

// Use composables
const {
  searchQuery,
  matchType,
  wordPosition,
  sortBy,
  searchResults,
  expandedWords,
  loadingWord,
  sortingWord,
  loadedOccurrences,
  wordListSortBy,
  showWordsExportMenu,
  currentExportWordText,
  currentExportVersesWordText,
  uniqueWords,
  searchSummary,
  getWordOccurrences,
  getSortedWordOccurrences,
  hasMoreOccurrences,
  getWorkCounts
} = useSearchState()

const { works, getWorkById, filterMode, selectedWorks, toggleFilters, filtersExpanded } = useFilterState()

// Computed: Search context text
const searchContextText = computed(() => {
  if (filterMode.value === 'all') {
    return 'All Works'
  } else {
    const total = works.value.length
    const selected = selectedWorks.value.length
    if (selected === total) {
      return 'All Works'
    } else {
      return `Selected Works (${selected}/${total})`
    }
  }
})

// Computed: Is select mode
const isSelectMode = computed(() => {
  return filterMode.value === 'select'
})

// Open search filter panel
const openSearchFilterPanel = () => {
  window.dispatchEvent(new Event('open-search-panel'))
}

// Override openVerseView to use router navigation instead of modal
const openVerseView = (verseId, searchWord = '', wordId = null, workId = null) => {
  // Find work_id from the result if not provided
  if (!workId) {
    const allOccurrences = searchResults.value?.results || []
    const occurrence = allOccurrences.find(r => r.verse_id === verseId)
    workId = occurrence?.work_id
  }

  if (!workId) {
    console.error('Cannot navigate to verse: work_id not found')
    return
  }

  // Navigate to Works Browser VerseView with search context
  // Preserve current search query params so we can navigate back
  router.push({
    name: 'VerseView',
    params: {
      workId: workId,
      verseId: verseId
    },
    query: {
      word: searchWord,
      from: 'search',
      // Preserve search params for back navigation
      q: route.query.q,
      type: route.query.type,
      pos: route.query.pos,
      sort: route.query.sort
    }
  })
}

// Emit event for loading more occurrences
const emit = defineEmits(['loadMore'])

// Helper: Highlight word in line text
const highlightWord = (lineText, wordToHighlight) => {
  if (!lineText || !wordToHighlight) return lineText

  const escapeHtml = (text) => {
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
  }

  const escapedLineText = escapeHtml(lineText)
  const regex = new RegExp(`(${wordToHighlight})`, 'g')
  return escapedLineText.replace(regex, '<span class="word-highlight">$1</span>')
}

// Helper: Clean hierarchy path
const cleanHierarchyPath = (path) => {
  if (!path) return ''

  const levels = path.split(' > ')
  const cleanedLevels = levels.map(level => {
    const parts = level.split(':')
    if (parts.length === 2) {
      return parts[1].trim()
    }
    return level.trim()
  })

  return cleanedLevels.join(' • ')
}

// Helper: Format verse and line display
const formatVerseAndLine = (result, includeLink = false) => {
  const verseTypeTamil = result.verse_type_tamil || result.verse_type || 'பாடல்'

  if (result.work_verse_count === 1) {
    return `அடி ${result.line_number}`
  }

  if (result.work_name === 'Manimegalai' || result.work_name === 'Silapathikaram') {
    return `அடி ${result.line_number}`
  }

  return `${verseTypeTamil} ${result.verse_number} • அடி ${result.line_number}`
}

// Helper: Get work chronology tooltip
const getWorkChronologyTooltip = (work) => {
  if (!work) return ''
  if (!work.chronology_start_year) return work.work_name_tamil || work.work_name

  const start = work.chronology_start_year
  const end = work.chronology_end_year

  if (start === end) {
    return `${work.work_name_tamil || work.work_name} (${start} CE)`
  }
  return `${work.work_name_tamil || work.work_name} (${start} - ${end} CE)`
}

// Toggle word expansion
const toggleWordExpansion = async (wordText) => {
  if (expandedWords.value.has(wordText)) {
    const newSet = new Set(expandedWords.value)
    newSet.delete(wordText)
    expandedWords.value = newSet
  } else {
    const newSet = new Set(expandedWords.value)
    newSet.add(wordText)
    expandedWords.value = newSet

    // Load occurrences if not already loaded
    const currentOccurrences = getWordOccurrences(wordText)
    if (currentOccurrences.length === 0) {
      await loadMoreOccurrences(wordText)
    }
  }
}

// Load more occurrences for a word
const loadMoreOccurrences = async (wordText) => {
  if (loadingWord.value) return

  loadingWord.value = wordText
  try {
    const tracking = loadedOccurrences.value[wordText] || { offset: 0, hasMore: true }

    const params = {
      q: searchResults.value.search_term,
      match_type: matchType.value,
      word_position: wordPosition.value,
      limit: 100,
      offset: tracking.offset,
      sort_by: sortBy.value,
      word_text: wordText
    }

    // Apply work filters if selected
    if (filterMode.value === 'select' && selectedWorks.value.length > 0) {
      params.work_ids = selectedWorks.value.join(',')
    }

    const response = await api.searchWords(params)
    const newResults = response.data.results || []

    // Append new results to existing results
    if (searchResults.value && searchResults.value.results) {
      // CRITICAL: Do NOT merge - just append to maintain backend sort order
      searchResults.value.results = [...searchResults.value.results, ...newResults]
    }

    // Update tracking
    loadedOccurrences.value[wordText] = {
      offset: tracking.offset + newResults.length,
      hasMore: newResults.length === 100
    }
  } catch (err) {
    console.error('Failed to load more occurrences:', err)
  } finally {
    loadingWord.value = null
  }
}

// Show export menus
const showLinesExportMenu = (wordText) => {
  currentExportWordText.value = wordText
}

const showVersesExportMenu = (wordText) => {
  currentExportVersesWordText.value = wordText
}

// Export words
const exportWords = (format) => {
  showWordsExportMenu.value = false
  if (!uniqueWords.value || uniqueWords.value.length === 0) return

  if (format === 'csv') {
    exportWordsToCSV()
  } else if (format === 'txt') {
    exportWordsToTXT()
  }
}

// Export words to CSV
const exportWordsToCSV = () => {
  if (!uniqueWords.value || uniqueWords.value.length === 0) return

  const searchTerm = searchResults.value.search_term || searchQuery.value.trim()
  const totalWords = uniqueWords.value.length
  const totalUsage = searchResults.value.total_count || 0

  const worksSet = new Set()
  let totalVerses = 0
  searchResults.value.unique_words.forEach(word => {
    totalVerses += word.verse_count || 0
    if (word.work_breakdown) {
      word.work_breakdown.forEach(wb => worksSet.add(wb.work_name))
    }
  })

  const headers = ['Word', 'Usage Count']
  const rows = uniqueWords.value.map(word => [word.word_text, word.count])

  const csvContent = [
    '"Data Source: tamilconcordence.in"',
    '"Compiled by: Prof. Dr. P. Pandiyaraja"',
    '',
    `"Search Term: ${searchTerm}"`,
    `"Match Type: ${matchType.value}"`,
    `"Word Position: ${wordPosition.value}"`,
    `"Total Works Found: ${worksSet.size}"`,
    `"Total Verses Found: ${totalVerses}"`,
    `"Distinct Words Found: ${totalWords}"`,
    `"Total Usage Count: ${totalUsage}"`,
    '',
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n')

  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `tamizh_words_${searchTerm}_${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Export words to TXT
const exportWordsToTXT = () => {
  if (!uniqueWords.value || uniqueWords.value.length === 0) return

  const searchTerm = searchResults.value.search_term || searchQuery.value.trim()
  const totalWords = uniqueWords.value.length
  const totalUsage = searchResults.value.total_count || 0

  const worksSet = new Set()
  let totalVerses = 0
  searchResults.value.unique_words.forEach(word => {
    totalVerses += word.verse_count || 0
    if (word.work_breakdown) {
      word.work_breakdown.forEach(wb => worksSet.add(wb.work_name))
    }
  })

  const content = [
    'Data Source: tamilconcordence.in',
    'Compiled by: Prof. Dr. P. Pandiyaraja',
    '',
    `Search Term: ${searchTerm}`,
    `Match Type: ${matchType.value}`,
    `Word Position: ${wordPosition.value}`,
    `Total Works Found: ${worksSet.size}`,
    `Total Verses Found: ${totalVerses}`,
    `Distinct Words Found: ${totalWords}`,
    `Total Usage Count: ${totalUsage}`,
    '',
    'Found Words:',
    '─'.repeat(50),
    ...uniqueWords.value.map((word, i) => `${i + 1}. ${word.word_text} (${word.count})`)
  ].join('\n')

  const blob = new Blob(['\ufeff' + content], { type: 'text/plain;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `tamizh_words_${searchTerm}_${new Date().toISOString().split('T')[0]}.txt`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Export word lines
const exportWordLines = (format, wordText) => {
  currentExportWordText.value = null
  if (format === 'csv') {
    exportWordLinesToCSV(wordText)
  } else if (format === 'txt') {
    exportWordLinesToTXT(wordText)
  }
}

// Export word lines to CSV
const exportWordLinesToCSV = (wordText) => {
  const occurrences = getWordOccurrences(wordText)
  if (occurrences.length === 0) return

  const wordInfo = searchResults.value.unique_words?.find(w => w.word_text === wordText)
  const usageCount = wordInfo?.count || occurrences.length
  const verseCount = wordInfo?.verse_count || 0

  const workCounts = getWorkCounts(wordText)
  const workOrderMap = new Map()
  works.value.forEach((work, index) => {
    workOrderMap.set(work.work_name, index)
  })

  const sortedWorkCounts = [...workCounts].sort((a, b) => {
    const indexA = workOrderMap.get(a.work_name) ?? Infinity
    const indexB = workOrderMap.get(b.work_name) ?? Infinity
    return indexA - indexB
  })

  const worksList = sortedWorkCounts.map(w => `${w.work_name_tamil} (${w.count})`).join(', ')

  const headers = ['Work & Location', 'Line']
  const rows = occurrences.map(result => {
    const hierarchyPath = cleanHierarchyPath(result.hierarchy_path_tamil || result.hierarchy_path)
    const location = hierarchyPath
      ? `${result.work_name_tamil}: ${hierarchyPath} | ${formatVerseAndLine(result)}`
      : `${result.work_name_tamil}: ${formatVerseAndLine(result)}`
    return [location, result.line_text]
  })

  const csvContent = [
    '"Data Source: tamilconcordence.in"',
    '"Compiled by: Prof. Dr. P. Pandiyaraja"',
    '',
    `"Word: ${wordText}"`,
    `"Works: ${worksList}"`,
    `"Total Verses: ${verseCount}"`,
    `"Total Usage: ${usageCount}"`,
    '',
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n')

  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `tamizh_lines_${wordText}_${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Export word lines to TXT
const exportWordLinesToTXT = (wordText) => {
  const occurrences = getWordOccurrences(wordText)
  if (occurrences.length === 0) return

  const wordInfo = searchResults.value.unique_words?.find(w => w.word_text === wordText)
  const usageCount = wordInfo?.count || occurrences.length
  const verseCount = wordInfo?.verse_count || 0

  const workCounts = getWorkCounts(wordText)
  const workOrderMap = new Map()
  works.value.forEach((work, index) => {
    workOrderMap.set(work.work_name, index)
  })

  const sortedWorkCounts = [...workCounts].sort((a, b) => {
    const indexA = workOrderMap.get(a.work_name) ?? Infinity
    const indexB = workOrderMap.get(b.work_name) ?? Infinity
    return indexA - indexB
  })

  const worksList = sortedWorkCounts.map(w => `${w.work_name_tamil} (${w.count})`).join(', ')

  const content = [
    'Data Source: tamilconcordence.in',
    'Compiled by: Prof. Dr. P. Pandiyaraja',
    '',
    `Word: ${wordText}`,
    `Works: ${worksList}`,
    `Total Verses: ${verseCount}`,
    `Total Usage: ${usageCount}`,
    '',
    'Lines:',
    '─'.repeat(80),
    ...occurrences.map((result, i) => {
      const hierarchyPath = cleanHierarchyPath(result.hierarchy_path_tamil || result.hierarchy_path)
      const location = hierarchyPath
        ? `${result.work_name_tamil}: ${hierarchyPath} | ${formatVerseAndLine(result)}`
        : `${result.work_name_tamil}: ${formatVerseAndLine(result)}`
      return `${i + 1}. ${location}\n   ${result.line_text}`
    })
  ].join('\n')

  const blob = new Blob(['\ufeff' + content], { type: 'text/plain;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `tamizh_lines_${wordText}_${new Date().toISOString().split('T')[0]}.txt`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Export word verses
const exportWordVerses = async (format, wordText) => {
  currentExportVersesWordText.value = null

  try {
    // Get all occurrences for this word
    const occurrences = getWordOccurrences(wordText)
    if (occurrences.length === 0) {
      alert('No occurrences found for this word.')
      return
    }

    // Get unique verse IDs
    const uniqueVerseIds = [...new Set(occurrences.map(occ => occ.verse_id))]

    // Fetch complete verses with context extraction
    const verses = []
    for (const verseId of uniqueVerseIds) {
      try {
        const response = await api.getVerse(verseId)
        // Find all occurrences for this verse to get matching line numbers
        const verseOccurrences = occurrences.filter(occ => occ.verse_id === verseId)
        const matchingLineNumbers = [...new Set(verseOccurrences.map(occ => occ.line_number))]

        // Get work/section context from first occurrence
        const occurrence = verseOccurrences[0]

        const fullVerse = {
          ...response.data,
          work_name: occurrence.work_name,
          work_name_tamil: occurrence.work_name_tamil,
          hierarchy_path: occurrence.hierarchy_path,
          hierarchy_path_tamil: occurrence.hierarchy_path_tamil
        }

        // Extract context lines if verse is longer than 10 lines
        if (fullVerse.lines.length > 10) {
          // Use the first matching line number to determine context
          const matchLineNumber = Math.min(...matchingLineNumbers)

          // Calculate range: 5 before, the match line, 4 after (total 10 lines)
          const startLine = Math.max(1, matchLineNumber - 5)
          const endLine = Math.min(fullVerse.lines.length, matchLineNumber + 4)

          // Extract subset of lines
          const extractedLines = fullVerse.lines.filter(
            line => line.line_number >= startLine && line.line_number <= endLine
          )

          verses.push({
            ...fullVerse,
            lines: extractedLines,
            isExtract: true,
            extractStartLine: startLine,
            extractEndLine: endLine,
            totalLines: fullVerse.lines.length
          })
        } else {
          // Include full verse if 10 lines or fewer
          verses.push({
            ...fullVerse,
            isExtract: false
          })
        }
      } catch (err) {
        console.error(`Failed to fetch verse ${verseId}:`, err)
      }
    }

    if (verses.length === 0) {
      alert('Failed to fetch verses.')
      return
    }

    // Export based on format
    if (format === 'csv') {
      exportVersesToCSV(wordText, verses)
    } else if (format === 'txt') {
      exportVersesToTXT(wordText, verses)
    }
  } catch (err) {
    console.error('Failed to export verses:', err)
    alert('Failed to export verses. Please try again.')
  }
}

// Export verses to CSV
const exportVersesToCSV = (wordText, verses) => {
  const wordInfo = searchResults.value.unique_words?.find(w => w.word_text === wordText)
  const verseCount = verses.length
  const workCounts = getWorkCounts(wordText)

  const workOrderMap = new Map()
  works.value.forEach((work, index) => {
    workOrderMap.set(work.work_name, index)
  })

  const sortedWorkCounts = [...workCounts].sort((a, b) => {
    const indexA = workOrderMap.get(a.work_name) ?? Infinity
    const indexB = workOrderMap.get(b.work_name) ?? Infinity
    return indexA - indexB
  })

  const worksList = sortedWorkCounts.map(w => `${w.work_name_tamil} (${w.count})`).join(', ')

  const headers = ['Work & Location', 'Verse Text']
  const rows = verses.map(verse => {
    const hierarchyPath = cleanHierarchyPath(verse.hierarchy_path_tamil || verse.hierarchy_path)
    let location = hierarchyPath
      ? `${verse.work_name_tamil}: ${hierarchyPath} | ${verse.verse_type_tamil || 'பாடல்'} ${verse.verse_number}`
      : `${verse.work_name_tamil}: ${verse.verse_type_tamil || 'பாடல்'} ${verse.verse_number}`

    // Add line range info for extracts
    if (verse.isExtract) {
      location += ` [Lines ${verse.extractStartLine}-${verse.extractEndLine} of ${verse.totalLines}]`
    }

    // Combine all lines into complete verse text
    const verseText = verse.lines.map(line => line.line_text).join('\n')

    return [location, verseText]
  })

  const csvContent = [
    '"Data Source: tamilconcordence.in"',
    '"Compiled by: Prof. Dr. P. Pandiyaraja"',
    '',
    `"Word: ${wordText}"`,
    `"Works: ${worksList}"`,
    `"Total Verses: ${verseCount}"`,
    `"Note: For verses longer than 10 lines, only context lines (5 before + 4 after) around the search word are included"`,
    '',
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(','))
  ].join('\n')

  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `tamizh_verses_${wordText}_${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Export verses to TXT
const exportVersesToTXT = (wordText, verses) => {
  const wordInfo = searchResults.value.unique_words?.find(w => w.word_text === wordText)
  const verseCount = verses.length
  const workCounts = getWorkCounts(wordText)

  const workOrderMap = new Map()
  works.value.forEach((work, index) => {
    workOrderMap.set(work.work_name, index)
  })

  const sortedWorkCounts = [...workCounts].sort((a, b) => {
    const indexA = workOrderMap.get(a.work_name) ?? Infinity
    const indexB = workOrderMap.get(b.work_name) ?? Infinity
    return indexA - indexB
  })

  const worksList = sortedWorkCounts.map(w => `${w.work_name_tamil} (${w.count})`).join(', ')

  const content = [
    'Data Source: tamilconcordence.in',
    'Compiled by: Prof. Dr. P. Pandiyaraja',
    '',
    `Word: ${wordText}`,
    `Works: ${worksList}`,
    `Total Verses: ${verseCount}`,
    'Note: For verses longer than 10 lines, only context lines (5 before + 4 after) around the search word are included',
    '',
    'Verses:',
    '═'.repeat(80),
    ...verses.map((verse, i) => {
      const hierarchyPath = cleanHierarchyPath(verse.hierarchy_path_tamil || verse.hierarchy_path)
      let location = hierarchyPath
        ? `${verse.work_name_tamil}: ${hierarchyPath} | ${verse.verse_type_tamil || 'பாடல்'} ${verse.verse_number}`
        : `${verse.work_name_tamil}: ${verse.verse_type_tamil || 'பாடல்'} ${verse.verse_number}`

      // Add line range info for extracts
      if (verse.isExtract) {
        location += ` [Lines ${verse.extractStartLine}-${verse.extractEndLine} of ${verse.totalLines}]`
      }

      // Combine all lines into verse text with indentation
      const verseText = verse.lines.map(line => `   ${line.line_text}`).join('\n')

      return `${i + 1}. ${location}\n${verseText}\n`
    })
  ].join('\n')

  const blob = new Blob(['\ufeff' + content], { type: 'text/plain;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `tamizh_verses_${wordText}_${new Date().toISOString().split('T')[0]}.txt`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<style scoped>
/* Results Header */
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: .25rem;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: .25rem;
  gap: 0rem;
  flex-wrap: wrap;
}

.search-summary-panel {
  flex: 1;
  min-width: 250px;
}

.searched-word-display {
  font-size: 0.95rem;
  color: #495057;
  margin-bottom: 0.25rem;
}

.separator {
  color: #dee2e6;
  font-weight: 600;
}

.search-context-link {
  color: #4a90e2;
  cursor: pointer;
  text-decoration: underline;
  font-weight: 600;
  transition: color 0.2s;
}

.search-context-link:hover {
  color: #357abd;
}

.search-context-text {
  color: #495057;
  font-weight: 600;
}

.summary-with-export {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.export-buttons-group {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  align-items: center;
}

.export-label {
  font-weight: 600;
  font-size: 0.9rem;
  color: #495057;
  margin-right: 0.25rem;
}

.export-button-combined {
  padding: 0.5rem 1rem;
  background-color: #d89a5f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.export-button-combined:hover {
  background-color: #c17a3a;
}

/* Word List Sort Options */
.word-list-sort-options {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.75rem .25rem;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.word-list-sort-options label {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  cursor: pointer;
  font-size: 0.95rem;
  color: #495057;
}

.filter-label {
  font-weight: 600;
  color: #495057;
  white-space: nowrap;
}

/* Word List Container */
.word-list-container {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 0;
  margin: 0;
}

.word-item-expandable {
  border: none;
  border-bottom: 1px solid #c17a3a;
  border-radius: 0;
  background: transparent;
  overflow: hidden;
  transition: all 0.2s;
}

.word-item-expandable.expanded {
  border-bottom-color: transparent;
  box-shadow: none;
}

.word-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.word-header-row:hover {
  background-color: #f8f9fa;
}

.word-item-expandable.expanded .word-header-row {
  background: #faf5f5; /* linear-gradient(135deg, var(--primary-color) 0%, #c62828 100%); */
  /* border-left: 3px solid var(--primary-color);*/
  padding: 0.75rem 0.5rem;
}

.word-item-expandable.expanded .word-header-row .word-text,
.word-item-expandable.expanded .word-header-row .word-number,
.word-item-expandable.expanded .word-header-row .word-count-badge {
  color: #495057;
}

.word-item-expandable.expanded .word-actions .expand-collapse-button .chevron-icon {
  border-color: #495057;
}

.word-info {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: 1;
  padding-left: 0.5rem;
  padding-right: 0.0rem;
  word-break: break-word;
}

.word-number {
  color: #6c757d;
  font-size: 0.9rem;
  min-width: 5px;
}

.word-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
}

.word-link {
  text-decoration: none;
  transition: color 0.2s;
}

.word-link:hover {
  color: #4a90e2;
  text-decoration: underline;
}

.word-count-badge {
  color: #6c757d;
  font-size: 0.9rem;
}

.word-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.action-icon {
  font-size: 1.2rem;
  text-decoration: none;
  cursor: pointer;
  transition: transform 0.2s;
}

.action-icon:hover {
  transform: scale(1.1);
}

.expand-collapse-button {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.expand-icon {
  font-size: 1.2rem;
  color: #4a90e2;
  display: flex;
  align-items: center;
}

.chevron-icon {
  display: inline-block;
  width: 10px;
  height: 10px;
  border: none;
  border-right: 2px solid currentColor;
  border-bottom: 2px solid currentColor;
  color: var(--primary-color);
  transition: transform 0.2s ease;
}

.chevron-right {
  transform: rotate(-45deg);
}

.chevron-down {
  transform: rotate(45deg);
}

.chevron-up {
  transform: rotate(-135deg);
}

/* Expanded Content */
.word-expanded-content {
  border-top: none;
  padding: 0;
  background: transparent;
  animation: expandDown 0.2s ease-out;
}

@keyframes expandDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 5000px;
  }
}

.expanded-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: white;
  border-radius: 6px;
  margin-bottom: 0; /* No space - flows directly into sort panel */
  gap: 1rem;
  flex-wrap: wrap;
}

.summary-counts {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.95rem;
  color: #495057;
  flex-wrap: wrap;
}

.summary-item {
  font-weight: 600;
}

.summary-divider {
  color: #dee2e6;
}

/* Lines Sort Options */
.lines-sort-options {
  display: flex;
  align-items: center;
  gap: .25rem;
  padding: 0.25rem .5rem;
  background: white;
  border-radius: 6px;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.lines-sort-options label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  cursor: pointer;
  font-size: 0.95rem;
  color: #495057;
}

/* Occurrences List */
.loading-occurrences {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
  font-style: italic;
}

.occurrences-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.occurrence-item {
  background: transparent;
  border: none;
  border-bottom: 1px solid #c17a3a;
  border-radius: 0;
  padding: 0.5rem 0;
  transition: all 0.2s;
}

.occurrence-item:hover {
  background-color: #f8f9fa;
}

.occurrence-metadata {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #6c757d;
}

.occurrence-number {
  min-width: 5px;
}

.work-name {
  font-weight: 600;
  color: #2c3e50;
}

.hierarchy-path {
  color: #6c757d;
}

.verse-link-text {
  color: #4a90e2;
  cursor: pointer;
  text-decoration: underline;
  font-weight: 500;
}

.verse-link-text:hover {
  color: #357abd;
}

.occurrence-line {
  font-size: 1.05rem;
  line-height: 1.6;
  color: #2c3e50;
}

.occurrence-line :deep(.word-highlight) {
  background-color: #e8f5e9; /* Even lighter green highlight */
  padding: 0.1rem 0.2rem;
  border-radius: 2px;
  font-weight: 600;
}

/* Load More */
.load-more-container {
  text-align: center;
  padding: 1rem 0;
}

.load-more-button {
  padding: 0.6rem 1.5rem;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  transition: background-color 0.2s;
}

.load-more-button:hover:not(:disabled) {
  background-color: #357abd;
}

.load-more-button:disabled {
  background-color: #adb5bd;
  cursor: not-allowed;
}

/* Collapse Footer */
.collapse-footer {
  text-align: center;
  padding-top: 1rem;
  margin-top: 1rem;
  border-top: 1px solid #dee2e6;
}

.collapse-footer-button {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.collapse-footer-button:hover {
  background: #f8f9fa;
  border-color: #4a90e2;
}

/* Export Modals */
.export-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.export-modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  max-width: 400px;
  width: 90%;
  animation: slideUp 0.2s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.export-modal-content h3 {
  margin: 0 0 1.5rem 0;
  font-size: 1.2rem;
  color: #2c3e50;
}

.export-modal-option {
  display: block;
  width: 100%;
  padding: 0.75rem 1rem;
  margin-bottom: 0.75rem;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: background-color 0.2s;
  text-align: left;
}

.export-modal-option:hover {
  background: #357abd;
}

.export-modal-cancel {
  display: block;
  width: 100%;
  padding: 0.75rem 1rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: background-color 0.2s;
}

.export-modal-cancel:hover {
  background: #5a6268;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .results-header {
    flex-direction: column;
    align-items: stretch;
  }

  .word-list-sort-options,
  .lines-sort-options {
    /* Keep radio buttons in one line on mobile */
    flex-wrap: wrap;
    gap: 0.2rem;
  }

  .word-list-sort-options label,
  .lines-sort-options label {
    font-size: 0.85rem;
  }

  .word-list-sort-options .filter-label,
  .lines-sort-options .filter-label {
    font-size: 0.85rem;
  }

  .word-header-row {
    padding: 0.25rem 0.25rem;
  }

  .word-text {
    font-size: 1rem;
  }

  .occurrence-metadata {
    font-size: 0.85rem;
  }

  .occurrence-line {
    font-size: 0.95rem;
  }
}
</style>
