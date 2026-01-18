import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from './layouts/AppLayout.vue'
import WelcomePage from './pages/WelcomePage.vue'
import HelpPage from './pages/HelpPage.vue'
import Home from './Home.vue'
import SearchPage from './pages/SearchPage.vue'
import SearchResultsPage from './pages/SearchResultsPage.vue'
import WorksBrowser from './pages/WorksBrowser.vue'
import WorksList from './components/works/WorksList.vue'
import WorkDetail from './components/works/WorkDetail.vue'
import SectionView from './components/works/SectionView.vue'
import VerseView from './VerseView.vue'
import UnderstandingThisToolPage from './pages/UnderstandingThisToolPage.vue'
import WordSegmentationPage from './pages/WordSegmentationPage.vue'
import TransliterationGuidePage from './pages/TransliterationGuidePage.vue'
import AboutUsPage from './pages/AboutUsPage.vue'
import ContactUsPage from './pages/ContactUsPage.vue'
import DisclaimerPage from './pages/DisclaimerPage.vue'
import OurJourney from './OurJourney.vue'
import AdminPage from './AdminPage.vue'

const routes = [
  {
    path: '/',
    component: AppLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: WelcomePage,
        meta: { title: 'Home' }
      },
      {
        path: 'acknowledgment',
        name: 'Acknowledgment',
        component: Home,
        meta: { title: 'Acknowledgment' }
      },
      {
        path: 'help',
        name: 'Help',
        component: HelpPage,
        meta: { title: 'Help' }
      },
      {
        path: 'help/quick-start',
        name: 'QuickStart',
        component: SearchPage,
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
            meta: { title: 'Browse Works' }
          },
          {
            path: ':workId',
            name: 'WorkDetail',
            component: WorkDetail,
            props: true,
            meta: { title: 'Work Details' }
          },
          {
            path: ':workId/section/:sectionId',
            name: 'SectionView',
            component: SectionView,
            props: true,
            meta: { title: 'Section' }
          },
          {
            path: ':workId/verse/:verseId',
            name: 'VerseView',
            component: VerseView,
            props: true,
            meta: { title: 'Verse' }
          }
        ]
      },
      {
        path: 'journey',
        name: 'Journey',
        component: OurJourney,
        meta: { title: 'The Story Behind' }
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
    meta: { title: 'Admin Panel' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  // Scroll to top on route change
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
          } else {
            // Scroll to top for new navigation
            appContent.scrollTop = 0
          }
        }
        resolve({ top: 0 })
      }, 0)
    })
  }
})

// Dynamic page titles
router.beforeEach((to, from, next) => {
  document.title = to.meta.title
    ? `${to.meta.title} | Thamizh Word Explorer`
    : 'Thamizh Word Explorer'

  // Note: Works Browser routes are always accessible (for verse links from search)
  // Only the navigation tab is hidden in production
  next()
})

export default router
