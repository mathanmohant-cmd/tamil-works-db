<template>
  <div class="verse-view-container">
    <div class="verse-view-header">
      <button @click="goBack" class="back-button">← Back to Search Results</button>
    </div>

    <div v-if="loading" class="loading">Loading verse...</div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="goBack">Go Back</button>
    </div>

    <div v-else-if="verse" class="verse-content">
      <!-- Verse Header with Full Hierarchy and Export Button -->
      <div class="verse-header">
        <div class="verse-title-line">
          <h2>
            <span class="work-title">{{ verse.work_name_tamil }}</span>
            <template v-if="cleanHierarchyPath(verse.hierarchy_path_tamil || verse.hierarchy_path)">
              <span class="separator"> • </span>
              <span class="hierarchy">{{ cleanHierarchyPath(verse.hierarchy_path_tamil || verse.hierarchy_path) }}</span>
            </template>
            <span class="separator"> • </span>
            <span class="verse-info">{{ verse.verse_type_tamil || verse.verse_type || 'பாடல்' }} {{ verse.verse_number }}</span>
          </h2>
        </div>
        <button @click="toggleExportMenu" class="export-verse-button">
          📥 Export
        </button>
      </div>

      <!-- Export Menu -->
      <div v-if="showExportMenu" class="export-menu" @click.stop>
        <div class="export-menu-content">
          <h3>Export Verse</h3>
          <button @click="exportVerse('csv')" class="export-option">
            📊 Export as CSV
          </button>
          <button @click="exportVerse('txt')" class="export-option">
            📄 Export as TXT
          </button>
          <button @click="showExportMenu = false" class="export-modal-cancel">
            Cancel
          </button>
        </div>
      </div>

      <!-- Lines displayed in two columns -->
      <div class="verse-lines-table">
        <div v-for="(line, index) in verse.lines" :key="line.line_id" class="line-row">
          <span class="line-number">{{ shouldShowLineNumber(index + 1) ? (index + 1) : '' }}</span>
          <span class="line-text" v-html="highlightSearchWord(line.line_text)"></span>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from './api.js'

export default {
  name: 'VerseView',
  props: {
    verseId: {
      type: Number,
      required: true
    },
    searchWord: {
      type: String,
      default: ''
    }
  },
  emits: ['close'],
  setup(props, { emit }) {
    const verse = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const showExportMenu = ref(false)

    const loadVerse = async () => {
      loading.value = true
      error.value = null

      try {
        const response = await api.getVerse(props.verseId)
        verse.value = response.data
      } catch (err) {
        error.value = 'Failed to load verse: ' + err.message
      } finally {
        loading.value = false
      }
    }

    const goBack = () => {
      emit('close')
    }

    const cleanHierarchyPath = (path) => {
      if (!path) return ''

      // Split by ' > ' to get each level
      const levels = path.split(' > ')

      // If there's only one section, check if it's a generic label and hide it
      if (levels.length === 1) {
        const parts = levels[0].split(':')
        if (parts.length === 2) {
          const sectionName = parts[1].trim()
          // Hide generic section labels like "முக்கிய தொகுப்பு"
          if (sectionName === 'முக்கிய தொகுப்பு' || sectionName === 'Main Collection') {
            return ''
          }
        }
        return ''
      }

      // Clean each level - remove the "type:" prefix and keep only the name
      const cleanedLevels = levels.map(level => {
        // Split by ':' to separate level_type and section_name
        const parts = level.split(':')
        if (parts.length === 2) {
          // Return only the section name (part after the colon)
          return parts[1].trim()
        }
        // If no colon, return as-is
        return level.trim()
      })

      return cleanedLevels.join(' • ')
    }

    const highlightSearchWord = (lineText) => {
      if (!props.searchWord || !lineText) return lineText

      const escapeHtml = (text) => {
        const div = document.createElement('div')
        div.textContent = text
        return div.innerHTML
      }

      const escapedLineText = escapeHtml(lineText)
      const regex = new RegExp(`(${props.searchWord})`, 'g')
      return escapedLineText.replace(regex, '<span class="word-highlight">$1</span>')
    }

    const shouldShowLineNumber = (lineNumber) => {
      // Show line number every 5th line
      return lineNumber % 5 === 0
    }

    const toggleExportMenu = () => {
      showExportMenu.value = !showExportMenu.value
    }

    const exportVerse = (format) => {
      showExportMenu.value = false
      if (format === 'csv') {
        exportVerseToCSV()
      } else if (format === 'txt') {
        exportVerseToTXT()
      }
    }

    const exportVerseToCSV = () => {
      if (!verse.value) return

      const headers = ['Line Number', 'Line Text']
      const rows = verse.value.lines.map((line, index) => [
        index + 1,
        line.line_text
      ])

      const csvContent = [
        '"Data Source: tamilconcordence.in"',
        '"Compiled by: Prof. Dr. P. Pandiyaraja"',
        '',
        `"Work: ${verse.value.work_name_tamil}"`,
        cleanHierarchyPath(verse.value.hierarchy_path_tamil || verse.value.hierarchy_path) ? `"Section: ${cleanHierarchyPath(verse.value.hierarchy_path_tamil || verse.value.hierarchy_path)}"` : '',
        `"${verse.value.verse_type_tamil || 'பாடல்'}: ${verse.value.verse_number}"`,
        '',
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
      ].filter(line => line !== '').join('\n')

      const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `verse_${verse.value.verse_id}_${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }

    const exportVerseToTXT = () => {
      if (!verse.value) return

      let content = 'Data Source: tamilconcordence.in\n'
      content += 'Compiled by: Prof. Dr. P. Pandiyaraja\n\n'

      content += `Work: ${verse.value.work_name_tamil}\n`
      if (cleanHierarchyPath(verse.value.hierarchy_path_tamil || verse.value.hierarchy_path)) {
        content += `Section: ${cleanHierarchyPath(verse.value.hierarchy_path_tamil || verse.value.hierarchy_path)}\n`
      }
      content += `${verse.value.verse_type_tamil || 'பாடல்'}: ${verse.value.verse_number}\n\n`
      content += '---\n\n'

      verse.value.lines.forEach((line, index) => {
        const lineNum = index + 1
        if (lineNum % 5 === 0) {
          content += `${lineNum}. ${line.line_text}\n`
        } else {
          content += `    ${line.line_text}\n`
        }
      })

      const blob = new Blob(['\ufeff' + content], { type: 'text/plain;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `verse_${verse.value.verse_id}_${new Date().toISOString().split('T')[0]}.txt`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }

    // Close export menu when clicking outside
    const handleClickOutside = (event) => {
      if (showExportMenu.value && !event.target.closest('.export-menu') && !event.target.closest('.export-verse-button')) {
        showExportMenu.value = false
      }
    }

    onMounted(() => {
      loadVerse()
      document.addEventListener('click', handleClickOutside)
    })

    return {
      verse,
      loading,
      error,
      showExportMenu,
      goBack,
      cleanHierarchyPath,
      highlightSearchWord,
      shouldShowLineNumber,
      toggleExportMenu,
      exportVerse
    }
  }
}
</script>

<style scoped>
.verse-view-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.verse-view-header {
  margin-bottom: 2rem;
}

.back-button {
  padding: 0.75rem 1.5rem;
  background: var(--secondary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  font-family: var(--english-font);
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 2px 6px rgba(25, 118, 210, 0.3);
}

.back-button:hover {
  background: #1565c0;
  transform: translateX(-4px);
  box-shadow: 0 4px 10px rgba(25, 118, 210, 0.4);
}

.back-button:active {
  transform: translateX(-2px);
}

.verse-header {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.verse-title-line {
  flex: 1;
  min-width: 0;
}

.verse-header h2 {
  font-size: 1.3rem;
  font-family: var(--tamil-font), var(--english-font);
  color: var(--text-primary);
  margin: 0;
  line-height: 1.5;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.25rem;
}

.work-title {
  font-weight: 700;
  color: var(--primary-color);
}

.separator {
  color: var(--text-secondary);
  font-weight: normal;
}

.hierarchy {
  font-weight: 600;
  color: var(--text-secondary);
}

.verse-info {
  font-weight: 700;
  color: var(--text-primary);
}

.export-verse-button {
  padding: 0.75rem 1.5rem;
  background: var(--success);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(76, 175, 80, 0.3);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.export-verse-button:hover {
  background: #388e3c;
  box-shadow: 0 4px 10px rgba(76, 175, 80, 0.4);
  transform: translateY(-2px);
}

.export-menu {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.export-menu-content {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 280px;
}

.export-option {
  padding: 1rem 1.5rem;
  background: white;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-primary);
}

.export-option:hover {
  border-color: var(--primary-color);
  background: #fff5f5;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(211, 47, 47, 0.15);
}

.verse-lines-table {
  background: white;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  line-height: 1.5;
}

.line-row {
  display: grid;
  grid-template-columns: 60px 1fr;
  gap: 1.5rem;
  margin: 0;
  padding: 0;
  align-items: baseline;
  line-height: 1.5;
}

.line-number {
  text-align: right;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.95rem;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  padding-right: 0.5rem;
  border-right: 2px solid var(--border-color);
  line-height: 1.5;
  margin: 0;
}

.line-text {
  font-size: 1.3rem;
  font-family: var(--tamil-font), var(--english-font);
  color: var(--text-primary);
  line-height: 1.5;
  margin: 0;
  padding: 0;
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .line-row {
    grid-template-columns: 30px 1fr;
    gap: 0.5rem;
  }

  .line-number {
    font-size: 0.7rem;
    padding-right: 0.25rem;
  }

  .line-text {
    font-size: 1.1rem;
  }

  .verse-lines-table {
    padding: 0.75rem;
    padding-left: 0.5rem;
  }
}

.verse-metadata {
  background: #f9f9f9;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid var(--primary-color);
}

.verse-metadata p {
  margin: 0.5rem 0;
  font-size: 0.95rem;
}

.loading,
.error {
  text-align: center;
  padding: 3rem;
  font-size: 1.1rem;
}

.error {
  color: var(--error);
}

.error button {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
}

.word-highlight {
  background: linear-gradient(120deg, #ffd54f 0%, #ffeb3b 100%);
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(255, 193, 7, 0.3);
}
</style>
