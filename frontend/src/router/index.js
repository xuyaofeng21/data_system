import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Layout from '../views/Layout.vue'
import Dashboard from '../views/dashboard/Index.vue'
import Analytics from '../views/Analytics.vue'
import TemplateList from '../views/TemplateList.vue'
import TaskList from '../views/TaskList.vue'
import UserList from '../views/UserList.vue'
import SystemLogs from '../views/SystemLogs.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/',
      component: Layout,
      children: [
        {
          path: '',
          redirect: '/dashboard'
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: Dashboard
        },
        {
          path: 'analytics',
          name: 'analytics',
          component: Analytics
        },
        {
          path: 'templates',
          name: 'templates',
          component: TemplateList
        },
        {
          path: 'tasks',
          name: 'tasks',
          component: TaskList
        },
        {
          path: 'users',
          name: 'users',
          component: UserList
        },
        {
          path: 'logs',
          name: 'logs',
          component: SystemLogs
        }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.name !== 'login' && !token) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
