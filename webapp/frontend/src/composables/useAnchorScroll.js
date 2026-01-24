import { onMounted, onUnmounted } from 'vue'

/**
 * Composable for handling anchor link scrolling in custom scroll containers
 * Intercepts clicks on anchor links and scrolls to target within .app-content
 */
export function useAnchorScroll() {
  const handleAnchorClick = (event) => {
    const target = event.target.closest('a[href^="#"]')
    if (!target) return

    const hash = target.getAttribute('href')
    if (!hash || hash === '#') return

    event.preventDefault()

    try {
      const targetElement = document.querySelector(hash)
      const appContent = document.querySelector('.app-content')

      if (targetElement && appContent) {
        // Get the element's position relative to the scroll container
        const elementTop = targetElement.offsetTop
        // Scroll the container to the element (with 20px offset for better visibility)
        appContent.scrollTo({
          top: elementTop - 20,
          behavior: 'smooth'
        })

        // Update URL hash without triggering scroll
        if (window.history && window.history.pushState) {
          window.history.pushState(null, null, hash)
        }
      }
    } catch (e) {
      console.warn('Error scrolling to anchor:', hash, e)
    }
  }

  onMounted(() => {
    // Add click listener to document
    document.addEventListener('click', handleAnchorClick)

    // On mount, scroll to hash if present in URL
    if (window.location.hash) {
      setTimeout(() => {
        try {
          const targetElement = document.querySelector(window.location.hash)
          const appContent = document.querySelector('.app-content')

          if (targetElement && appContent) {
            const elementTop = targetElement.offsetTop
            appContent.scrollTo({
              top: elementTop - 20,
              behavior: 'smooth'
            })
          }
        } catch (e) {
          console.warn('Error scrolling to initial hash:', window.location.hash, e)
        }
      }, 200) // Wait for DOM to be fully rendered
    }
  })

  onUnmounted(() => {
    document.removeEventListener('click', handleAnchorClick)
  })
}
