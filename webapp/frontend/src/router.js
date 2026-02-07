import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from './layouts/AppLayout.vue'
import Home from './features/home/pages/Home.vue'
import HelpPageMenu from './features/help/pages/HelpPageMenu.vue'
import Acknowledgment from './features/home/pages/Acknowledgment.vue'
import QuickStart from './features/help/pages/QuickStart.vue'
import SearchResultsPage from './features/search/pages/SearchResultsPage.vue'
import WorksBrowser from './features/works/pages/WorksBrowser.vue'
import WorksList from './features/works/components/WorksList.vue'
import WorkDetail from './features/works/components/WorkDetail.vue'
import SectionView from './features/works/components/SectionView.vue'
import VerseView from './features/works/pages/VerseView.vue'
import UnderstandingThisToolPage from './features/help/pages/UnderstandingThisToolPage.vue'
import WordSegmentationPage from './features/help/pages/WordSegmentationPage.vue'
import TransliterationGuidePage from './features/help/pages/TransliterationGuidePage.vue'
import AboutUsPage from './features/home/pages/AboutUsPage.vue'
import ContactUsPage from './features/home/pages/ContactUsPage.vue'
import DisclaimerPage from './features/home/pages/DisclaimerPage.vue'
import OurJourney from './features/about/pages/OurJourney.vue'
import OurInspiration from './features/about/pages/OurInspiration.vue'
import AboutUsMenu from './features/about/pages/AboutUsMenu.vue'
import AdminPage from './features/admin/pages/AdminPage.vue'
import InsightsPage from './features/insights/pages/InsightsPage.vue'
import { useUserRole } from './composables/useUserRole.js'

const routes = [
  {
    path: '/',
    component: AppLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: Home,
        meta: { title: 'Home' }
      },
      {
        path: 'acknowledgment',
        name: 'Acknowledgment',
        component: Acknowledgment,
        meta: { title: 'Acknowledgment' }
      },
      {
        path: 'help',
        name: 'Help',
        component: HelpPageMenu,
        meta: { title: 'Help' }
      },
      {
        path: 'help/quick-start',
        name: 'QuickStart',
        component: QuickStart,
        meta: { title: 'Quick Start' }
      },
      {
        path: 'help/quick-start/results',
        name: 'SearchResults',
        component: SearchResultsPage,
        meta: { title: 'Search Results' }
      },
      {
        path: 'help/understanding-this-tool',
        name: 'UnderstandingThisTool',
        component: UnderstandingThisToolPage,
        meta: { title: 'Understanding This Tool' }
      },
      {
        path: 'help/word-segmentation',
        name: 'WordSegmentation',
        component: WordSegmentationPage,
        meta: { title: 'Word Segmentation Principles' }
      },
      {
        path: 'help/transliteration-guide',
        name: 'TransliterationGuide',
        component: TransliterationGuidePage,
        meta: { title: 'Transliteration Guide' }
      },
      {
        path: 'works',
        component: WorksBrowser,
        children: [
          {
            path: '',
            name: 'WorksList',
            component: WorksList,
            meta: { title: 'Browse Works', requiresBrowse: true }
          },
          {
            path: ':workId',
            name: 'WorkDetail',
            component: WorkDetail,
            props: true,
            meta: { title: 'Work Details', requiresBrowse: true }
          },
          {
            path: ':workId/section/:sectionId',
            name: 'SectionView',
            component: SectionView,
            props: true,
            meta: { title: 'Section', requiresBrowse: true }
          }
        ]
      },
      {
        path: 'verse/:workId/:verseId',
        name: 'VerseView',
        component: VerseView,
        props: true,
        meta: { title: 'Verse' }
        // Note: VerseView is publicly accessible (no requiresBrowse flag)
      },
      {
        path: 'story',
        name: 'TheStoryBehind',
        component: AboutUsMenu,
        meta: { title: 'The Story Behind' }
      },
      {
        path: 'story/journey',
        name: 'Journey',
        component: OurJourney,
        meta: { title: 'Our Journey' }
      },
      {
        path: 'story/inspiration',
        name: 'Inspiration',
        component: OurInspiration,
        meta: { title: 'Our Inspiration' }
      },
      {
        path: 'about-us',
        name: 'AboutUs',
        component: AboutUsPage,
        meta: { title: 'About Us' }
      },
      {
        path: 'contact-us',
        name: 'ContactUs',
        component: ContactUsPage,
        meta: { title: 'Contact Us' }
      },
      {
        path: 'insights',
        name: 'Insights',
        component: InsightsPage,
        meta: { title: 'Insights' }
      },
      {
        path: 'disclaimer',
        name: 'Disclaimer',
        component: DisclaimerPage,
        meta: { title: 'Disclaimer' }
      }
    ]
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminPage,
    meta: { title: 'Admin Panel', requiresAdmin: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  // Scroll to top on route change, or to hash anchor if present
  scrollBehavior(to, from, savedPosition) {
    // The app uses a custom scroll container (.app-content), not window scrolling
    // So we need to handle scrolling manually
    return new Promise((resolve) => {
      setTimeout(() => {
        const appContent = document.querySelector('.app-content')
        if (appContent) {
          if (savedPosition) {
            // Restore saved position for back/forward navigation
            appContent.scrollTop = savedPosition.top || 0
          } else if (to.hash) {
            // Handle anchor links (e.g., #section-id)
            try {
              const targetElement = document.querySelector(to.hash)
              if (targetElement) {
                // Get the element's position relative to the scroll container
                const elementTop = targetElement.offsetTop
                // Scroll the container to the element (with 80px offset for sticky header)
                appContent.scrollTop = elementTop - 80
              } else {
                // Element not found, scroll to top
                appContent.scrollTop = 0
              }
            } catch (e) {
              // Invalid selector, scroll to top
              console.warn('Invalid hash selector:', to.hash, e)
              appContent.scrollTop = 0
            }
          } else {
            // Scroll to top for new navigation
            appContent.scrollTop = 0
          }
        }
        resolve({ top: 0 })
      }, 100) // Timeout to ensure DOM is ready
    })
  }
})

// Dynamic page titles and route guards
router.beforeEach((to, from, next) => {
  document.title = to.meta.title
    ? `${to.meta.title} | Thamizh Word Explorer`
    : 'Thamizh Word Explorer'

  // Check if route requires browse works permission
  if (to.meta.requiresBrowse) {
    const { canBrowseWorks } = useUserRole()
    if (!canBrowseWorks.value) {
      // Redirect to home if user doesn't have browse works permission
      console.warn('Access denied: Browse Works requires user or admin role')
      next({ name: 'Home' })
      return
    }
  }

  // Check if route requires admin permission
  if (to.meta.requiresAdmin) {
    const { canAccessAdmin } = useUserRole()
    if (!canAccessAdmin.value) {
      console.warn('Access denied: Admin access required')
      next({ name: 'Home' })
      return
    }
  }

  next()
})

export default router
