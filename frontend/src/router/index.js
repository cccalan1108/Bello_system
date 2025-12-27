import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: (to) => {
      // 檢查登入狀態，決定重定向到哪裡
      const user = getUser()
      if (user) {
        return user.role === 'Admin' ? '/admin-lobby' : '/lobby'
      }
      return '/login'
    }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterView.vue')
  },
  {
    path: '/lobby',
    name: 'lobby',
    component: () => import('../views/LobbyView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/create-meeting',
    name: 'createMeeting',
    component: () => import('../views/CreateMeetingView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/meetings',
    name: 'meetings',
    component: () => import('../views/MeetingListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/my-meetings',
    name: 'myMeetings',
    component: () => import('../views/MyMeetingsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'chat',
    component: () => import('../views/ChatView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/meeting-chat',
    name: 'meetingChat',
    component: () => import('../views/MeetingChatView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin-lobby',
    name: 'admin-lobby',
    component: () => import('../views/AdminLobbyView.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/admin-meetings',
    name: 'admin-meetings',
    component: () => import('../views/AdminMeetingsView.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/admin-users',
    name: 'AdminUsers',
    component: () => import('@/views/AdminUsersView.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/admin/user-chat-records',
    name: 'AdminUserChatRecords',
    component: () => import('@/views/AdminUserChatRecordsView.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/admin/meeting-chat-records',
    name: 'AdminMeetingChatRecords',
    component: () => import('@/views/AdminMeetingChatRecordsView.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 導航守衛
import { getUser } from '@/utils/api'

router.beforeEach((to, from, next) => {
  const user = getUser()
  
  // 檢查是否需要認證
  if (to.meta.requiresAuth) {
    if (!user) {
      // 未登入，重定向到登入頁
      next('/login')
      return
    }
  }
  
  // 檢查是否需要管理員權限
  if (to.meta.requiresAdmin) {
    if (!user || user.role !== 'Admin') {
      // 不是管理員，重定向到登入頁
      next('/login')
      return
    }
  }
  
  // 如果已登入且訪問登入/註冊頁，重定向到首頁
  if ((to.path === '/login' || to.path === '/register') && user) {
    const homeRoute = user.role === 'Admin' ? '/admin-lobby' : '/lobby'
    next(homeRoute)
    return
  }
  
  next()
})

export default router