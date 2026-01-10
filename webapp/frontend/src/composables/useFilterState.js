import { ref, watch, computed, onMounted } from 'vue'
import api from '../api.js'

// Shared filter state (singleton pattern)
const filterMode = ref('all')
const selectedWorks = ref([])
const works = ref([])
const filtersExpanded = ref(false)
const designatedCollectionId = ref(null)
const showWelcome = ref(true)

export function useFilterState() {
  // Restore filter state from session storage
  const restoreFilters = async () => {
    try {
      const savedSelection = sessionStorage.getItem('selectedWorks')
      const savedMode = sessionStorage.getItem('filterMode')

      if (savedSelection) {
        const parsedSelection = JSON.parse(savedSelection)
        selectedWorks.value = Array.isArray(parsedSelection) ? parsedSelection : []
      }

      if (savedMode && (savedMode === 'all' || savedMode === 'select')) {
        filterMode.value = savedMode
      }
    } catch (err) {
      console.error('Failed to restore filter state:', err)
    }
  }

  // Load works and designated collection
  const loadWorks = async () => {
    try {
      const worksResponse = await api.getWorks()
      works.value = worksResponse.data

      // Get designated collection
      const settingsResponse = await api.getDesignatedFilterCollection()
      designatedCollectionId.value = settingsResponse.data.collection_id
    } catch (err) {
      console.error('Failed to load works:', err)
    }
  }

  // Auto-persist to session storage
  watch([filterMode, selectedWorks], () => {
    sessionStorage.setItem('filterMode', filterMode.value)
    sessionStorage.setItem('selectedWorks', JSON.stringify(selectedWorks.value))
  }, { deep: true })

  // Computed: Works filter button text
  const worksFilterButtonText = computed(() => {
    const total = works.value.length
    if (selectedWorks.value.length === 0) {
      return 'Select Works'
    }
    return `${selectedWorks.value.length}/${total} Selected - Change`
  })

  // Computed: Sorted selected works (by canonical order)
  const sortedSelectedWorks = computed(() => {
    if (selectedWorks.value.length === 0) return []

    // Create a position map for selected works
    const positionMap = new Map()
    works.value.forEach(work => {
      positionMap.set(work.work_id, work.canonical_position || 999)
    })

    return [...selectedWorks.value].sort((a, b) => {
      const posA = positionMap.get(a) || 999
      const posB = positionMap.get(b) || 999
      return posA - posB
    })
  })

  // Get work name by ID
  const getWorkName = (workId) => {
    const work = works.value.find(w => w.work_id === workId)
    return work ? work.work_name_tamil || work.work_name : 'Unknown'
  }

  // Get work by ID
  const getWorkById = (workId) => {
    return works.value.find(w => w.work_id === workId)
  }

  // Get work chronology tooltip
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

  // Toggle filters panel
  const toggleFilters = () => {
    filtersExpanded.value = !filtersExpanded.value

    if (filtersExpanded.value) {
      // Wait for DOM to render, then scroll to filters panel
      setTimeout(() => {
        const filtersPanel = document.querySelector('.filters-panel')
        if (filtersPanel) {
          filtersPanel.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      }, 100)
    }
  }

  // Close filters panel
  const closeFilters = () => {
    filtersExpanded.value = false
  }

  // Clear all filters
  const clearFilters = () => {
    selectedWorks.value = []
  }

  // Remove a single work
  const removeWork = (workId) => {
    selectedWorks.value = selectedWorks.value.filter(id => id !== workId)
  }

  // Handle filter mode change
  const handleFilterModeChange = () => {
    showWelcome.value = false

    if (filterMode.value === 'select' && selectedWorks.value.length === 0) {
      // Auto-expand filters if no works selected
      filtersExpanded.value = true

      setTimeout(() => {
        const filtersPanel = document.querySelector('.filters-panel')
        if (filtersPanel) {
          filtersPanel.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      }, 100)
    }
  }

  // Handle collection selection from CollectionTree
  const handleCollectionSelection = (workIds) => {
    selectedWorks.value = workIds
    showWelcome.value = false
  }

  return {
    // State
    filterMode,
    selectedWorks,
    works,
    filtersExpanded,
    designatedCollectionId,
    showWelcome,

    // Computed
    worksFilterButtonText,
    sortedSelectedWorks,

    // Methods
    restoreFilters,
    loadWorks,
    getWorkName,
    getWorkById,
    getWorkChronologyTooltip,
    toggleFilters,
    closeFilters,
    clearFilters,
    removeWork,
    handleFilterModeChange,
    handleCollectionSelection
  }
}
