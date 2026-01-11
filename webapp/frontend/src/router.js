import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from './layouts/AppLayout.vue'
import Home from './Home.vue'
import SearchPage from './pages/SearchPage.vue'
import WorksBrowser from './pages/WorksBrowser.vue'
import WorksList from './components/works/WorksList.vue'
import WorkDetail from './components/works/WorkDetail.vue'
import SectionView from './components/works/SectionView.vue'
import VerseView from './VerseView.vue'
import AboutConcordance from './AboutConcordance.vue'
import OurJourney from './OurJourney.vue'
import AdminPage from './AdminPage.vue'

const routes = [
  {
    path: '/',
    component: AppLayout,
    children: [
      {
        path: '',
        redirect: '/search'
      },
      {
        path: 'home',
        name: 'Home',
        component: Home,
        meta: { title: 'Acknowledgment' }
      },
      {
        path: 'search',
        name: 'Search',
        component: SearchPage,
        meta: { title: 'Search' }
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
        path: 'about',
        name: 'About',
        component: AboutConcordance,
        meta: { title: 'About & Help' },
        props: route => ({
          initialTab: route.query.tab || 'qa'
        })
      },
      {
        path: 'journey',
        name: 'Journey',
        component: OurJourney,
        meta: { title: 'The Story Behind' }
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
    redirect: '/search'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  // Prevent page from scrolling when changing tabs
  scrollBehavior(to, from, savedPosition) {
    // If user clicked back/forward, restore scroll position
    if (savedPosition) {
      return savedPosition
    }
    // If navigating to same route with different params (like verse navigation)
    if (to.path.startsWith('/works/') && from.path.startsWith('/works/')) {
      // Scroll to top for verse navigation
      return { top: 0 }
    }
    // For tab navigation, maintain current scroll position
    return false
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
