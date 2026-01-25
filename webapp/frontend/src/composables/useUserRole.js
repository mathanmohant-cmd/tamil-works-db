import { ref, computed } from 'vue'
import api from '../api.js'

// Reactive state (shared across all components)
const currentRole = ref(null)
const currentUser = ref(null)
const userId = ref(null)

export function useUserRole() {
  // Initialize role from sessionStorage on first load, default to 'guest'
  if (currentRole.value === null) {
    const storedRole = sessionStorage.getItem('userRole')
    const storedUser = sessionStorage.getItem('username')
    const storedUserId = sessionStorage.getItem('userId')
    if (storedRole) {
      currentRole.value = storedRole
      currentUser.value = storedUser
      userId.value = storedUserId ? parseInt(storedUserId) : null
    } else {
      // Default to guest if no role stored
      currentRole.value = 'guest'
      currentUser.value = 'Guest'
      userId.value = null
    }
  }

  // Computed properties for role checks
  const isGuest = computed(() => currentRole.value === 'guest')
  const isAdmin = computed(() => currentRole.value === 'admin')
  const isAuthenticated = computed(() => currentRole.value === 'admin')
  const canBrowseWorks = computed(() => currentRole.value === 'admin')
  const canAccessAdmin = computed(() => currentRole.value === 'admin')

  // Set role as guest
  const setGuestRole = () => {
    currentRole.value = 'guest'
    currentUser.value = 'Guest'
    userId.value = null
    sessionStorage.setItem('userRole', 'guest')
    sessionStorage.setItem('username', 'Guest')
    sessionStorage.removeItem('userId')
  }

  // Login with username/password (using backend admin auth)
  const login = async (username, password) => {
    try {
      const response = await api.adminLogin(username, password)

      if (response.data.success && response.data.user) {
        const user = response.data.user
        currentRole.value = 'admin'
        currentUser.value = user.username
        userId.value = user.user_id

        sessionStorage.setItem('userRole', 'admin')
        sessionStorage.setItem('username', user.username)
        sessionStorage.setItem('userId', user.user_id.toString())

        return { success: true, role: 'admin', user: user }
      } else {
        return { success: false, error: 'Invalid credentials' }
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Login failed'
      return { success: false, error: errorMessage }
    }
  }

  // Logout (sets back to guest instead of null)
  const logout = () => {
    currentRole.value = 'guest'
    currentUser.value = 'Guest'
    userId.value = null
    sessionStorage.setItem('userRole', 'guest')
    sessionStorage.setItem('username', 'Guest')
    sessionStorage.removeItem('userId')
  }

  return {
    currentRole,
    currentUser,
    userId,
    isGuest,
    isAdmin,
    isAuthenticated,
    canBrowseWorks,
    canAccessAdmin,
    setGuestRole,
    login,
    logout
  }
}
