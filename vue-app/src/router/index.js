import { createRouter, createWebHistory } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/components/LoginView.vue')
    },
    {
      path: '/auth/callback',
      name: 'auth-callback',
      component: () => import('@/components/AuthCallback.vue')
    },
    {
      path: '/dashboard',
      component: DashboardLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('@/components/DashboardHome.vue')
        },
        {
          path: '/onboarding',
          name: 'onboarding',
          component: () => import('@/components/OnboardingView.vue')
        },
        {
          path: '/onboarding/bulk',
          name: 'onboarding-bulk',
          component: () => import('@/components/OnboardUsersBulkView.vue')
        },
        {
          path: '/onboarding/edit/:userId',
          name: 'edit-user',
          component: () => import('@/components/EditUser.vue')
        },
        {
          path: '/onboarding/create',
          name: 'create-user',
          component: () => import('@/components/CreateUser.vue')
        },
        {
          path: '/onboarding/user-tools/:userId',
          name: 'user-tools',
          component: () => import('@/components/UserToolsView.vue')
        },
        {
          path: '/print-onboarding',
          name: 'print-onboarding',
          component: () => import('@/components/PrintOnboardingView.vue')
        },
        {
          path: '/offboarding',
          name: 'offboarding',
          component: () => import('@/components/OffboardingView.vue')
        },
        {
          path: '/offboarding/edit/:userId',
          name: 'edit-offboarding',
          component: () => import('@/components/EditOffboarding.vue')
        },
        {
          path: '/offboarding/create',
          name: 'create-offboarding',
          component: () => import('@/components/CreateOffboarding.vue')
        },
        {
          path: '/offboarding/tools/:userId',
          name: 'offboarding-tools',
          component: () => import('@/components/OffboardingToolsView.vue')
        },
        {
          path: '/offboarded-users',
          name: 'offboarded-users',
          component: () => import('@/components/OffboardedUsersView.vue')
        },
        {
          path: '/settings',
          name: 'settings',
          component: () => import('@/components/SettingsView.vue')
        }
      ]
    }
  ],
})

// Navigation guard to check authentication
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('userToken') || sessionStorage.getItem('userClaims')
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Redirect to login if trying to access protected route without auth
    next('/')
  } else if (to.path === '/' && isAuthenticated) {
    // Redirect to dashboard if already authenticated and trying to access login
    next('/dashboard')
  } else {
    next()
  }
})

export default router
