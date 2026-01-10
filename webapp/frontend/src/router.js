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
  routes
})

// Check if Works Browser should be accessible
function isWorksBrowserAllowed() {
  const hostname = window.location.hostname
  return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '192.168.1.198'
}

// Dynamic page titles and route guards
router.beforeEach((to, from, next) => {
  document.title = to.meta.title
    ? `${to.meta.title} | Thamizh Word Explorer`
    : 'Thamizh Word Explorer'

  // Block access to Works Browser routes if not on allowed hostname
  if (to.path.startsWith('/works') && !isWorksBrowserAllowed()) {
    next('/search')
    return
  }

  next()
})

export default router
