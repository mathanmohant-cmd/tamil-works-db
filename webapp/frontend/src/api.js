/**
 * API client for Tamil Words Search backend
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  /**
   * Search for words
   */
  searchWords(params) {
    return api.get('/search', { params })
  },

  /**
   * Get all literary works
   */
  getWorks() {
    return api.get('/works')
  },

  /**
   * Get word roots
   */
  getWordRoots(searchTerm = null) {
    return api.get('/roots', { params: searchTerm ? { q: searchTerm } : {} })
  },

  /**
   * Get verse details
   */
  getVerse(verseId) {
    return api.get(`/verse/${verseId}`)
  },

  /**
   * Get database statistics
   */
  getStatistics() {
    return api.get('/stats')
  },

  /**
   * Health check
   */
  healthCheck() {
    return api.get('/health')
  }
}
