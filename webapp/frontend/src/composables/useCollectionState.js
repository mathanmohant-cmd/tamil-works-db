import { ref } from 'vue'

// Shared collection navigation state (singleton pattern)
// This stores the current collection path when navigating through WorksList
// State persists during navigation but resets on page refresh
const currentCollectionPath = ref([])
const rootCollection = ref(null)

export function useCollectionState() {
  /**
   * Set the current collection navigation path
   * Called by WorksList when user navigates through collections
   * @param {Array} path - Array of collection objects in the navigation path
   */
  const setCollectionPath = (path) => {
    currentCollectionPath.value = [...path]
  }

  /**
   * Clear the collection navigation path
   * Call when exiting Works browser or resetting navigation
   */
  const clearCollectionPath = () => {
    currentCollectionPath.value = []
  }

  /**
   * Get collection breadcrumbs formatted for breadcrumb UI
   * @returns {Array} Array of breadcrumb objects with id, type, name, routePath
   */
  const getCollectionBreadcrumbs = () => {
    return currentCollectionPath.value.map(collection => ({
      id: `collection-${collection.collection_id}`,
      type: 'collection',
      name: collection.collection_name_tamil || collection.collection_name,
      routePath: '/works', // Returns to WorksList (will filter by collection)
      data: collection
    }))
  }

  /**
   * Set the root collection (designated filter collection)
   * @param {Object} collection - The root collection object
   */
  const setRootCollection = (collection) => {
    rootCollection.value = collection
  }

  return {
    // State
    currentCollectionPath,
    rootCollection,

    // Methods
    setCollectionPath,
    clearCollectionPath,
    getCollectionBreadcrumbs,
    setRootCollection
  }
}
