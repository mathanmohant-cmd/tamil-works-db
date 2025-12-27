/**
 * API client for Thamizh Words Search backend
 */
import axios from 'axios'

// Auto-detect API URL based on current hostname
// If VITE_API_URL is set in .env, use it; otherwise use current hostname with port 8000
const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  // Use the same hostname as the frontend, but on port 8000
  const protocol = window.location.protocol // http: or https:
  const hostname = window.location.hostname // localhost or 192.168.1.198
  return `${protocol}//${hostname}:8000`
}

const API_BASE_URL = getApiBaseUrl()

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
  },

  /**
   * Get all collections (for sort options)
   */
  getPublicCollections() {
    return api.get('/collections')
  },

  // =========================================================================
  // Admin Authentication
  // =========================================================================

  /**
   * Admin login
   */
  adminLogin(username, password) {
    return api.post('/admin/login', { username, password })
  },

  // =========================================================================
  // Admin Collection APIs
  // =========================================================================

  /**
   * Get all collections
   */
  getCollections(params = {}) {
    return api.get('/admin/collections', { params })
  },

  /**
   * Get collection tree (nested structure)
   */
  getCollectionTree() {
    return api.get('/admin/collections', { params: { tree: true } })
  },

  /**
   * Get single collection
   */
  getCollection(collectionId) {
    return api.get(`/admin/collections/${collectionId}`)
  },

  /**
   * Create collection
   */
  createCollection(data) {
    return api.post('/admin/collections', data)
  },

  /**
   * Update collection
   */
  updateCollection(collectionId, data) {
    return api.put(`/admin/collections/${collectionId}`, data)
  },

  /**
   * Delete collection
   */
  deleteCollection(collectionId) {
    return api.delete(`/admin/collections/${collectionId}`)
  },

  /**
   * Add work to collection
   */
  addWorkToCollection(collectionId, data) {
    return api.post(`/admin/collections/${collectionId}/works`, data)
  },

  /**
   * Remove work from collection
   */
  removeWorkFromCollection(collectionId, workId) {
    return api.delete(`/admin/collections/${collectionId}/works/${workId}`)
  },

  /**
   * Update work position in collection
   */
  updateWorkPosition(collectionId, workId, position) {
    return api.patch(`/admin/collections/${collectionId}/works/${workId}/position`, null, {
      params: { position }
    })
  }
}
