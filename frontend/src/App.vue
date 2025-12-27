<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg">
      <div class="container">
        <router-link class="navbar-brand bello-logo" :to="homeRoute">
          <span class="logo-icon">🎈</span>
          <span class="logo-text">Bello</span>
        </router-link>
        <div class="d-flex nav-buttons">
          <template v-if="!isLoggedIn">
            <router-link v-if="$route.path !== '/register'" to="/register" class="btn btn-cute-outline me-2">
              ✨ 註冊新帳號
            </router-link>
            <router-link v-if="$route.path !== '/login'" to="/login" class="btn btn-cute">
              🔑 登入
            </router-link>
          </template>
          <template v-else>
            <router-link :to="homeRoute" class="btn btn-cute-outline me-2">
              🏠 回到主頁
            </router-link>
            <button @click="handleLogout" class="btn btn-cute-danger">
              👋 登出
            </button>
          </template>
        </div>
      </div>
    </nav>
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script>
import { getUser, clearAuth, apiPost } from '@/utils/api'

export default {
  name: 'App',
  data() {
    return {
      isLoggedIn: false,
      userRole: null,
      onlineStatusInterval: null
    }
  },
  computed: {
    homeRoute() {
      return this.userRole === 'Admin' ? '/admin-lobby' : '/lobby'
    },
    isAuthPage() {
      return ['/login', '/register'].includes(this.$route.path)
    }
  },
  created() {
    this.checkLoginStatus()
  },
  methods: {
    checkLoginStatus() {
      const user = getUser()
      if (user) {
        this.isLoggedIn = true
        this.userRole = user.role
        // 登入後開始追蹤在線狀態
        this.startOnlineStatusTracking()
      } else {
        this.isLoggedIn = false
        this.userRole = null
        this.stopOnlineStatusTracking()
      }
    },
    async updateOnlineStatus(isOnline) {
      try {
        await apiPost('online-status', { is_online: isOnline })
      } catch (error) {
        // 靜默處理錯誤
      }
    },
    startOnlineStatusTracking() {
      // 立即設置為在線
      this.updateOnlineStatus(true)
      
      // 每 30 秒更新一次在線狀態
      if (this.onlineStatusInterval) {
        clearInterval(this.onlineStatusInterval)
      }
      this.onlineStatusInterval = setInterval(() => {
        this.updateOnlineStatus(true)
      }, 30000)
    },
    stopOnlineStatusTracking() {
      if (this.onlineStatusInterval) {
        clearInterval(this.onlineStatusInterval)
        this.onlineStatusInterval = null
      }
    },
    handleLogout() {
      // 登出時設置為離線
      this.updateOnlineStatus(false)
      this.stopOnlineStatusTracking()
      clearAuth()
      this.isLoggedIn = false
      this.userRole = null
      this.$router.push('/login')
    }
  },
  watch: {
    $route() {
      this.checkLoginStatus()
    }
  },
  beforeUnmount() {
    // 關閉頁面時設置為離線
    this.updateOnlineStatus(false)
    this.stopOnlineStatusTracking()
  }
}
</script>

<style>
#app {
  font-family: 'Nunito', 'Microsoft JhengHei', Arial, sans-serif;
  min-height: 100vh;
}

/* 🎀 導航欄樣式 */
.navbar {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 50%, #FFB6C1 100%) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 4px 30px rgba(255, 107, 107, 0.3);
  padding: 0.8rem 0;
  position: sticky;
  top: 0;
  z-index: 1000;
  border-bottom: none;
}

.bello-logo {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  text-decoration: none !important;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.bello-logo:hover {
  transform: scale(1.05);
}

.logo-icon {
  font-size: 1.8rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.logo-text {
  font-family: 'Nunito', sans-serif;
  font-weight: 800;
  font-size: 1.8rem;
  color: white;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

@keyframes gradient {
  0% { background-position: 0% center; }
  50% { background-position: 100% center; }
  100% { background-position: 0% center; }
}

/* 🔘 導航按鈕樣式 */
.nav-buttons .btn {
  font-family: 'Nunito', sans-serif;
  font-weight: 600;
  border-radius: 50px;
  padding: 0.5rem 1.2rem;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  font-size: 0.9rem;
}

.nav-buttons .btn.btn-cute {
  background: white !important;
  color: #FF6B6B !important;
  border: none !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
}

.nav-buttons .btn.btn-cute:hover {
  background: #FFF5F5 !important;
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2) !important;
  color: #E85555 !important;
}

.nav-buttons .btn.btn-cute-outline {
  background: white !important;
  color: #FF6B6B !important;
  border: 2px solid rgba(255, 107, 107, 0.3) !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
}

.nav-buttons .btn.btn-cute-outline:hover {
  background: #FFF5F5 !important;
  border-color: #FF6B6B !important;
  transform: translateY(-2px);
  color: #E85555 !important;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15) !important;
}

.nav-buttons .btn.btn-cute-danger {
  background: white !important;
  color: #FF6B6B !important;
  border: none !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
}

.nav-buttons .btn.btn-cute-danger:hover {
  background: #FFF0F0 !important;
  transform: translateY(-2px) scale(1.05);
  color: #E85555 !important;
}

/* 📄 主內容區 */
.main-content {
  padding: 1rem;
  min-height: calc(100vh - 80px);
}

/* ✨ 頁面過渡動畫 */
.page-enter-active {
  animation: pageIn 0.4s ease;
}

.page-leave-active {
  animation: pageOut 0.3s ease;
}

@keyframes pageIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pageOut {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-10px);
  }
}

/* 📱 響應式調整 */
@media (max-width: 768px) {
  .navbar {
    padding: 0.5rem 0;
  }
  
  .logo-text {
    font-size: 1.4rem;
  }
  
  .logo-icon {
    font-size: 1.4rem;
  }
  
  .nav-buttons .btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.8rem;
  }
  
  .main-content {
    padding: 0.5rem;
  }
}
</style>