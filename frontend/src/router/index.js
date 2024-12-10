import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login'
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
    component: () => import('../views/ProfileView.vue')
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
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 導航守衛
router.beforeEach((to, from, next) => {
  console.log('Navigation guard - from:', from.path)
  console.log('Navigation guard - to:', to.path)
  console.log('Navigation guard - matched routes:', to.matched)
  
  if (to.meta.requiresAdmin) {
    const user = JSON.parse(localStorage.getItem('user'))
    console.log('Current user:', user)
    if (!user || user.role !== 'Admin') {
      console.log('Unauthorized access, redirecting to login')
      next('/login')
      return
    }
  }
  next()
})

export default router