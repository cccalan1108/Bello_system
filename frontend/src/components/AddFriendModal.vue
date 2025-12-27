<template>
  <div class="modal fade" :class="{ 'show d-block': show }" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">添加好友</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <!-- 搜尋框 -->
          <div class="search-box mb-3">
            <input 
              type="text" 
              class="form-control" 
              v-model="searchQuery"
              placeholder="搜尋用戶名稱或暱稱..."
              @input="handleSearch"
            >
          </div>
          
          <!-- 搜尋結果 -->
          <div v-if="searching" class="text-center py-3">
            <div class="spinner-border spinner-border-sm" role="status">
              <span class="visually-hidden">搜尋中...</span>
            </div>
          </div>
          
          <div v-else-if="searchQuery && searchResults.length === 0" class="text-center text-muted py-3">
            找不到符合的用戶
          </div>
          
          <div v-else class="search-results">
            <div 
              v-for="user in searchResults" 
              :key="user.user_id"
              class="user-item"
            >
              <div class="user-avatar">
                <img 
                  v-if="user.avatar_url" 
                  :src="user.avatar_url" 
                  class="avatar-img"
                  alt="avatar"
                />
                <div v-else class="avatar-circle">
                  {{ user.user_nickname?.charAt(0) || user.user_name?.charAt(0) }}
                </div>
              </div>
              <div class="user-info">
                <div class="user-name">{{ user.user_name }}</div>
                <small class="user-nickname text-muted">{{ user.user_nickname }}</small>
              </div>
              <div class="user-action">
                <button 
                  v-if="user.friendship_status === 'none'"
                  class="btn btn-primary btn-sm"
                  @click="sendRequest(user.user_id)"
                  :disabled="sendingTo === user.user_id"
                >
                  {{ sendingTo === user.user_id ? '發送中...' : '加好友' }}
                </button>
                <span 
                  v-else-if="user.friendship_status === 'friend'"
                  class="badge bg-success"
                >
                  已是好友
                </span>
                <span 
                  v-else-if="user.friendship_status === 'pending_sent'"
                  class="badge bg-warning"
                >
                  已發送請求
                </span>
                <button 
                  v-else-if="user.friendship_status === 'pending_received'"
                  class="btn btn-success btn-sm"
                  @click="acceptRequest(user.user_id)"
                >
                  接受請求
                </button>
              </div>
            </div>
          </div>
          
          <!-- 好友請求區塊 -->
          <div v-if="pendingRequests.length > 0" class="pending-requests mt-4">
            <h6 class="section-title">待處理的好友請求</h6>
            <div 
              v-for="request in pendingRequests" 
              :key="request.user_id"
              class="request-item"
            >
              <div class="user-avatar">
                <img 
                  v-if="request.avatar_url" 
                  :src="request.avatar_url" 
                  class="avatar-img small"
                  alt="avatar"
                />
                <div v-else class="avatar-circle small">
                  {{ request.user_nickname?.charAt(0) || request.user_name?.charAt(0) }}
                </div>
              </div>
              <div class="user-info">
                <div class="user-name">{{ request.user_name }}</div>
                <small class="text-muted">{{ request.user_nickname }}</small>
              </div>
              <div class="request-actions">
                <button 
                  class="btn btn-success btn-sm me-1"
                  @click="acceptRequest(request.user_id)"
                >
                  接受
                </button>
                <button 
                  class="btn btn-outline-secondary btn-sm"
                  @click="rejectRequest(request.user_id)"
                >
                  拒絕
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-if="show" class="modal-backdrop fade show"></div>
</template>

<script>
import { apiGet, apiPost } from '@/utils/api'

function debounce(fn, delay) {
  let timeout
  return function(...args) {
    clearTimeout(timeout)
    timeout = setTimeout(() => fn.apply(this, args), delay)
  }
}

export default {
  name: 'AddFriendModal',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'friend-added'],
  data() {
    return {
      searchQuery: '',
      searchResults: [],
      searching: false,
      sendingTo: null,
      pendingRequests: []
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        this.loadPendingRequests()
      }
    }
  },
  methods: {
    handleSearch: debounce(async function() {
      if (!this.searchQuery.trim()) {
        this.searchResults = []
        return
      }
      
      this.searching = true
      try {
        const data = await apiGet(`friends/search?query=${encodeURIComponent(this.searchQuery)}`)
        if (data.status === 'success') {
          this.searchResults = data.users
        }
      } catch (error) {
        console.error('Error searching users:', error)
      } finally {
        this.searching = false
      }
    }, 300),
    
    async loadPendingRequests() {
      try {
        const data = await apiGet('friends/requests')
        if (data.status === 'success') {
          this.pendingRequests = data.pending_requests
        }
      } catch (error) {
        console.error('Error loading pending requests:', error)
      }
    },
    
    async sendRequest(userId) {
      this.sendingTo = userId
      try {
        const data = await apiPost('friends/add', { friend_id: userId })
        if (data.status === 'success') {
          // 更新搜尋結果中的狀態
          const user = this.searchResults.find(u => u.user_id === userId)
          if (user) {
            user.friendship_status = 'pending_sent'
          }
          alert('好友請求已發送！')
        } else {
          alert(data.message || '發送好友請求失敗')
        }
      } catch (error) {
        console.error('Error sending friend request:', error)
        alert('發送好友請求失敗')
      } finally {
        this.sendingTo = null
      }
    },
    
    async acceptRequest(userId) {
      try {
        const data = await apiPost('friends/accept', { friend_id: userId })
        if (data.status === 'success') {
          // 從待處理列表中移除
          this.pendingRequests = this.pendingRequests.filter(r => r.user_id !== userId)
          // 更新搜尋結果中的狀態
          const user = this.searchResults.find(u => u.user_id === userId)
          if (user) {
            user.friendship_status = 'friend'
          }
          this.$emit('friend-added')
          alert('已成為好友！')
        } else {
          alert(data.message || '接受好友請求失敗')
        }
      } catch (error) {
        console.error('Error accepting friend request:', error)
        alert('接受好友請求失敗')
      }
    },
    
    async rejectRequest(userId) {
      try {
        const data = await apiPost('friends/reject', { friend_id: userId })
        if (data.status === 'success') {
          this.pendingRequests = this.pendingRequests.filter(r => r.user_id !== userId)
        } else {
          alert(data.message || '拒絕好友請求失敗')
        }
      } catch (error) {
        console.error('Error rejecting friend request:', error)
        alert('拒絕好友請求失敗')
      }
    }
  }
}
</script>

<style scoped>
.modal {
  background: rgba(0,0,0,0.5);
}

.search-box input {
  border-radius: 20px;
  padding: 10px 20px;
}

.search-results {
  max-height: 300px;
  overflow-y: auto;
}

.user-item, .request-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.user-item:last-child, .request-item:last-child {
  border-bottom: none;
}

.user-avatar {
  margin-right: 12px;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.avatar-img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-img.small {
  width: 32px;
  height: 32px;
}

.avatar-circle.small {
  width: 32px;
  height: 32px;
  font-size: 14px;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 500;
}

.section-title {
  color: #666;
  font-size: 14px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.pending-requests {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
}

.request-actions {
  display: flex;
}
</style>

