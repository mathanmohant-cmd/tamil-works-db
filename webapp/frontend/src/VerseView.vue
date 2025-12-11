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
      <!-- Work and Hierarchy -->
      <div class="verse-breadcrumb">
        <span class="work-title">{{ verse.work_name_tamil }}</span>
        <span v-if="verse.hierarchy_path_tamil" class="separator">›</span>
        <span v-if="verse.hierarchy_path_tamil" class="hierarchy">{{ cleanHierarchyPath(verse.hierarchy_path_tamil || verse.hierarchy_path) }}</span>
      </div>

      <!-- Verse Header -->
      <div class="verse-header">
        <h2>{{ verse.verse_type_tamil || verse.verse_type || 'பாடல்' }} {{ verse.verse_number }}</h2>
      </div>

      <!-- Lines displayed separately -->
      <div class="verse-lines">
        <div v-for="line in verse.lines" :key="line.line_id" class="line-item">
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

      const levels = path.split(' > ')
      const cleanedLevels = levels.map(level => {
        const parts = level.split(':')
        if (parts.length === 2) {
          const levelType = parts[0].trim()
          const sectionName = parts[1].trim()
          if (sectionName.startsWith(levelType)) {
            return sectionName
          }
        }
        return level
      })

      return cleanedLevels.join(' > ')
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

    onMounted(() => {
      loadVerse()
    })

    return {
      verse,
      loading,
      error,
      goBack,
      cleanHierarchyPath,
      highlightSearchWord
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
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.back-button:hover {
  background: var(--primary-dark);
  transform: translateX(-4px);
}

.verse-breadcrumb {
  font-size: 0.95rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
  font-family: var(--tamil-font), var(--english-font);
}

.work-title {
  font-weight: 600;
  color: var(--primary-color);
}

.separator {
  margin: 0 0.5rem;
}

.hierarchy {
  font-style: italic;
}

.verse-header {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 2rem;
}

.verse-header h2 {
  font-size: 1.8rem;
  font-family: var(--tamil-font), var(--english-font);
  color: var(--text-primary);
  margin: 0;
}

.verse-lines {
  background: white;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.line-item {
  margin: 0.2rem 0;
  line-height: 1.4;
}

.line-text {
  font-size: 1.3rem;
  font-family: var(--tamil-font), var(--english-font);
  color: var(--text-primary);
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
