import { createRouter, createWebHistory } from 'vue-router'
import MainApp from './MainApp.vue'
import AdminPage from './AdminPage.vue'

const routes = [
  {
    path: '/',
    component: MainApp
  },
  {
    path: '/admin',
    component: AdminPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
