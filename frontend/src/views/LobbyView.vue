<template>
  <div class="lobby-container">
    <!-- 好友請求提醒 -->
    <div v-if="pendingRequestsCount > 0" class="friend-requests-alert mb-4">
      <div class="alert alert-info d-flex align-items-center justify-content-between">
        <span>
          <i class="bi bi-person-plus-fill me-2"></i>
          你有 {{ pendingRequestsCount }} 個待處理的好友請求
        </span>
        <button class="btn btn-primary btn-sm" @click="showAddFriendModal = true">
          查看
        </button>
      </div>
    </div>

    <div class="row g-4">
      <div v-for="(option, index) in options" :key="index" class="col-md-6">
        <router-link v-if="option.path" :to="option.path" class="card-link">
          <div class="card h-100 lobby-card" :class="option.cardClass">
            <div class="card-body">
              <div class="card-icon" v-if="option.icon">
                <i :class="option.icon"></i>
              </div>
              <h5 class="card-title mb-2">{{ option.title }}</h5>
              <p class="card-text text-muted">{{ option.description }}</p>
              <i class="bi bi-arrow-right card-arrow"></i>
            </div>
          </div>
        </router-link>
        <div v-else @click="option.action" class="card-link">
          <div class="card h-100 lobby-card" :class="option.cardClass">
            <div class="card-body">
              <div class="card-icon" v-if="option.icon">
                <i :class="option.icon"></i>
              </div>
              <h5 class="card-title mb-2">{{ option.title }}</h5>
              <p class="card-text text-muted">{{ option.description }}</p>
              <i class="bi bi-arrow-right card-arrow"></i>
              <span v-if="option.badge" class="badge bg-danger position-absolute top-0 end-0 m-3">
                {{ option.badge }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 好友列表側邊欄 -->
    <div v-if="showFriendsSidebar" class="friends-sidebar-overlay" @click="showFriendsSidebar = false">
      <div class="friends-sidebar" @click.stop>
        <div class="sidebar-header">
          <h5>好友列表</h5>
          <button class="btn-close" @click="showFriendsSidebar = false"></button>
        </div>
        <div class="sidebar-actions">
          <button class="btn btn-primary w-100 mb-3" @click="showAddFriendModal = true">
            <i class="bi bi-person-plus"></i> 添加好友
          </button>
        </div>
        
        <!-- 待處理的好友請求 -->
        <div v-if="pendingRequests.length > 0" class="pending-section mb-3">
          <h6 class="section-title">好友請求</h6>
            <div v-for="request in pendingRequests" :key="request.user_id" class="friend-request-item">
              <div class="user-info">
                <div class="avatar-circle small">
                  {{ request.user_name?.charAt(0) }}
                </div>
                <span class="user-name">{{ request.user_name }}</span>
              </div>
            <div class="request-actions">
              <button class="btn btn-success btn-sm" @click="acceptFriend(request.user_id)">
                接受
              </button>
            </div>
          </div>
        </div>
        
        <!-- 好友列表 -->
        <div class="friends-list-section">
          <h6 class="section-title">我的好友 ({{ friends.length }})</h6>
          <div v-if="friendsLoading" class="text-center py-3">
            <div class="spinner-border spinner-border-sm" role="status"></div>
          </div>
          <div v-else-if="friends.length === 0" class="text-center text-muted py-4">
            還沒有好友，快去添加吧！
          </div>
          <div v-else class="friends-items">
            <div 
              v-for="friend in friends" 
              :key="friend.user_id"
              class="friend-item"
              @click="goToChat(friend)"
            >
              <div class="friend-avatar">
                <img 
                  v-if="friend.avatar_url" 
                  :src="friend.avatar_url" 
                  class="avatar-img"
                  alt="avatar"
                />
                <div v-else class="avatar-circle">
                  {{ friend.user_name?.charAt(0) }}
                </div>
                <span class="online-dot" :class="{ online: friend.is_online }"></span>
              </div>
              <div class="friend-info">
                <div class="friend-name">{{ friend.user_name }}</div>
                <small :class="friend.is_online ? 'text-success' : 'text-muted'">
                  {{ friend.is_online ? '在線' : '離線' }}
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加好友對話框 -->
    <AddFriendModal 
      :show="showAddFriendModal" 
      @close="showAddFriendModal = false"
      @friend-added="loadFriends"
    />
  </div>
</template>

<script>
import { apiGet, apiPost } from '@/utils/api'
import AddFriendModal from '@/components/AddFriendModal.vue'

export default {
  name: 'LobbyView',
  components: {
    AddFriendModal
  },
  data() {
    return {
      friends: [],
      friendsLoading: false,
      pendingRequests: [],
      showFriendsSidebar: false,
      showAddFriendModal: false
    }
  },
  computed: {
    pendingRequestsCount() {
      return this.pendingRequests.length
    },
    options() {
      return [
        {
          title: '新增聚會',
          description: '建立新的聚會',
          path: '/create-meeting',
          icon: 'bi bi-plus-circle'
        },
        {
          title: '所有聚會',
          description: '瀏覽所有可參加的聚會',
          path: '/meetings',
          icon: 'bi bi-calendar-event'
        },
        {
          title: '我的聚會',
          description: '查看我參加和舉辦的聚會',
          path: '/my-meetings',
          icon: 'bi bi-calendar-check'
        },
        {
          title: '私人聊天',
          description: '與其他用戶進行私人對話',
          path: '/chat',
          icon: 'bi bi-chat-dots'
        },
        {
          title: '聚會聊天',
          description: '與聚會成員進行群組對話',
          path: '/meeting-chat',
          icon: 'bi bi-people'
        },
        {
          title: '好友列表',
          description: '查看好友和添加新好友',
          path: null,
          action: () => this.openFriendsSidebar(),
          icon: 'bi bi-person-heart',
          badge: this.pendingRequestsCount > 0 ? this.pendingRequestsCount : null
        },
        {
          title: '添加好友',
          description: '搜尋並添加新好友',
          path: null,
          action: () => this.showAddFriendModal = true,
          icon: 'bi bi-person-plus'
        },
        {
          title: '個人資料',
          description: '編輯個人資料',
          path: '/profile',
          icon: 'bi bi-person-circle'
        }
      ]
    }
  },
  async created() {
    await this.loadFriends()
  },
  methods: {
    async loadFriends() {
      this.friendsLoading = true
      try {
        const data = await apiGet('friends')
        console.log('Friends API response:', data)
        if (data.status === 'success') {
          this.friends = data.friends
          console.log('Friends data with avatar:', this.friends.map(f => ({ name: f.user_name, avatar: f.avatar_url })))
        }
        
        const requestsData = await apiGet('friends/requests')
        if (requestsData.status === 'success') {
          this.pendingRequests = requestsData.pending_requests
        }
      } catch (error) {
        console.error('Error loading friends:', error)
      } finally {
        this.friendsLoading = false
      }
    },
    
    async acceptFriend(friendId) {
      try {
        const data = await apiPost('friends/accept', { friend_id: friendId })
        if (data.status === 'success') {
          await this.loadFriends()
        } else {
          alert(data.message || '接受好友請求失敗')
        }
      } catch (error) {
        console.error('Error accepting friend:', error)
        alert('接受好友請求失敗')
      }
    },
    
    openFriendsSidebar() {
      this.showFriendsSidebar = true
      this.loadFriends()
    },
    
    goToChat(friend) {
      this.$router.push({
        path: '/chat',
        query: {
          userId: friend.user_id,
          userName: friend.user_name
        }
      })
    }
  }
}
</script>

<style scoped>
.lobby-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 30px 20px;
}

.friend-requests-alert .alert {
  border-radius: 16px;
  background: linear-gradient(135deg, #FFF5F5 0%, #FFE8E8 100%);
  border: 2px solid #FFD5D5;
  color: #FF6B6B;
}

.friend-requests-alert .btn-primary {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  border: none;
  border-radius: 20px;
  padding: 6px 16px;
}

.card-link {
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  display: block;
}

.lobby-card {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: none;
  border-radius: 20px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(145deg, #ffffff 0%, #FFF9F9 100%);
  box-shadow: 
    0 4px 20px rgba(255, 107, 107, 0.08),
    0 2px 8px rgba(0, 0, 0, 0.04);
}

.lobby-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #FF6B6B 0%, #FFB6C1 50%, #4ECDC4 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.lobby-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 
    0 20px 40px rgba(255, 107, 107, 0.15),
    0 8px 16px rgba(0, 0, 0, 0.06);
}

.lobby-card:hover::before {
  opacity: 1;
}

.card-body {
  padding: 24px;
}

.card-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #FF6B6B 0%, #FFB6C1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  transition: transform 0.3s ease;
}

.lobby-card:hover .card-icon {
  transform: scale(1.1) rotate(-5deg);
}

.card-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.card-text {
  font-size: 0.9rem;
  color: #888;
}

.card-arrow {
  position: absolute;
  right: 20px;
  bottom: 20px;
  font-size: 1.5rem;
  color: #FFB6C1;
  transition: all 0.3s ease;
}

.lobby-card:hover .card-arrow {
  transform: translateX(8px);
  color: #FF6B6B;
}

/* 好友側邊欄 */
.friends-sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 107, 107, 0.2);
  backdrop-filter: blur(4px);
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.friends-sidebar {
  position: fixed;
  top: 0;
  right: 0;
  width: 380px;
  max-width: 100%;
  height: 100vh;
  background: linear-gradient(180deg, #FFFFFF 0%, #FFF9F9 100%);
  box-shadow: -8px 0 30px rgba(255, 107, 107, 0.15);
  padding: 24px;
  overflow-y: auto;
  animation: slideIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #FFE5E5;
}

.sidebar-header h5 {
  margin: 0;
  font-weight: 700;
  font-size: 1.3rem;
  color: #FF6B6B;
}

.sidebar-header .btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.sidebar-header .btn-close:hover {
  opacity: 1;
}

.sidebar-actions .btn-primary {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  border: none;
  border-radius: 12px;
  padding: 12px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
  transition: all 0.3s ease;
}

.sidebar-actions .btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

.section-title {
  font-size: 13px;
  color: #888;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

.pending-section {
  background: linear-gradient(135deg, #FFF5E6 0%, #FFE8D4 100%);
  border-radius: 16px;
  padding: 16px;
  border: 2px solid #FFD4B8;
}

.friend-request-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name {
  font-weight: 600;
  color: #333;
}

.request-actions .btn-success {
  background: linear-gradient(135deg, #4ECDC4 0%, #44B8AF 100%);
  border: none;
  border-radius: 20px;
  padding: 6px 16px;
  font-weight: 600;
}

.friends-items {
  max-height: calc(100vh - 350px);
  overflow-y: auto;
}

.friend-item {
  display: flex;
  align-items: center;
  padding: 14px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 8px;
}

.friend-item:hover {
  background: linear-gradient(135deg, #FFF5F5 0%, #FFE8E8 100%);
  transform: translateX(4px);
}

.friend-avatar {
  position: relative;
  margin-right: 14px;
}

.avatar-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF6B6B 0%, #FFB6C1 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 17px;
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
}

.avatar-img {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #FFE5E5;
}

.avatar-circle.small {
  width: 36px;
  height: 36px;
  font-size: 14px;
}

.online-dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ccc;
  border: 3px solid #fff;
  transition: background-color 0.3s ease;
}

.online-dot.online {
  background: #4ECDC4;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

.friend-info {
  flex: 1;
}

.friend-name {
  font-weight: 600;
  color: #333;
  font-size: 1rem;
}

.friend-info small {
  font-size: 0.8rem;
}
</style>
