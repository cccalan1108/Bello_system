<template>
  <div class="modal fade" :class="{ 'show d-block': show }" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">用戶資訊</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">載入中...</span>
            </div>
          </div>
          <div v-else>
            <!-- 基本資訊區塊 -->
            <div class="text-center mb-4">
              <div class="user-avatar mx-auto mb-3">
                <div class="avatar-circle large" v-if="!userProfile.avatar_url">
                  {{ userNickname?.charAt(0) || userName?.charAt(0) }}
                </div>
                <img 
                  v-else 
                  :src="userProfile.avatar_url" 
                  alt="頭像" 
                  class="avatar-img"
                >
                <span 
                  v-if="onlineStatus !== null"
                  class="online-indicator" 
                  :class="{ 'online': onlineStatus }"
                ></span>
              </div>
              <h5 class="user-name mb-1">{{ userProfile.user_name || userName }}</h5>
              <p class="user-nickname text-muted mb-0">{{ userProfile.user_nickname || userNickname }}</p>
            </div>
            
            <!-- 詳細資料區塊 -->
            <div v-if="hasDetailInfo" class="profile-details">
              <h6 class="details-title mb-3">個人資料</h6>
              
              <div class="details-grid">
                <div v-if="userProfile.sex" class="detail-item">
                  <span class="detail-label">性別</span>
                  <span class="detail-value">{{ userProfile.sex }}</span>
                </div>
                <div v-if="userProfile.birthday" class="detail-item">
                  <span class="detail-label">生日</span>
                  <span class="detail-value">{{ userProfile.birthday }}</span>
                </div>
                <div v-if="userProfile.nationality" class="detail-item">
                  <span class="detail-label">國籍</span>
                  <span class="detail-value">{{ userProfile.nationality }}</span>
                </div>
                <div v-if="userProfile.city" class="detail-item">
                  <span class="detail-label">城市</span>
                  <span class="detail-value">{{ userProfile.city }}</span>
                </div>
                <div v-if="userProfile.star_sign" class="detail-item">
                  <span class="detail-label">星座</span>
                  <span class="detail-value">{{ userProfile.star_sign }}</span>
                </div>
                <div v-if="userProfile.mbti" class="detail-item">
                  <span class="detail-label">MBTI</span>
                  <span class="detail-value">{{ userProfile.mbti }}</span>
                </div>
                <div v-if="userProfile.blood_type" class="detail-item">
                  <span class="detail-label">血型</span>
                  <span class="detail-value">{{ userProfile.blood_type }}</span>
                </div>
                <div v-if="userProfile.religion" class="detail-item">
                  <span class="detail-label">宗教</span>
                  <span class="detail-value">{{ userProfile.religion }}</span>
                </div>
                <div v-if="userProfile.married" class="detail-item">
                  <span class="detail-label">婚姻狀態</span>
                  <span class="detail-value">{{ userProfile.married }}</span>
                </div>
                <div v-if="userProfile.sns" class="detail-item" :class="{ 'full-width': userProfile.sns === 'YES' && userProfile.sns_accounts && userProfile.sns_accounts.length > 0 }">
                  <span class="detail-label">社群帳號</span>
                  <div v-if="userProfile.sns === 'YES' && userProfile.sns_accounts && userProfile.sns_accounts.length > 0" class="sns-accounts">
                    <span v-for="(account, index) in userProfile.sns_accounts" :key="index" class="sns-badge">
                      {{ account.sns_type }}: {{ account.sns_id }}
                    </span>
                  </div>
                  <span v-else class="detail-value">無</span>
                </div>
                <div v-if="userProfile.university" class="detail-item full-width">
                  <span class="detail-label">學校</span>
                  <span class="detail-value">{{ userProfile.university }}</span>
                </div>
                <div v-if="userProfile.find_meeting_type" class="detail-item full-width">
                  <span class="detail-label">想找的聚會類型</span>
                  <span class="detail-value">{{ userProfile.find_meeting_type }}</span>
                </div>
              </div>
              
              <div v-if="userProfile.interest" class="detail-section">
                <span class="detail-label">興趣</span>
                <p class="detail-text">{{ userProfile.interest }}</p>
              </div>
              
              <div v-if="userProfile.self_introduction" class="detail-section">
                <span class="detail-label">自我介紹</span>
                <p class="detail-text">{{ userProfile.self_introduction }}</p>
              </div>
            </div>
            
            <div v-else class="text-center text-muted py-3">
              <small>此用戶尚未填寫詳細資料</small>
            </div>
            
            <!-- 操作按鈕 -->
            <div class="action-buttons mt-4">
              <!-- 好友操作按鈕 -->
              <button 
                v-if="friendshipStatus === 'none' && !loading"
                class="btn btn-primary w-100 mb-2"
                @click="addFriend"
                :disabled="actionLoading || loading"
              >
                {{ actionLoading ? '發送中...' : '加為好友' }}
              </button>
              
              <!-- 載入中時顯示 -->
              <div v-if="loading && friendshipStatus === 'none'" class="text-center py-2">
                <small class="text-muted">載入中...</small>
              </div>
              
              <button 
                v-else-if="friendshipStatus === 'pending_received'"
                class="btn btn-success w-100 mb-2"
                @click="acceptFriend"
                :disabled="actionLoading"
              >
                接受好友請求
              </button>
              
              <span 
                v-else-if="friendshipStatus === 'pending_sent'"
                class="badge bg-warning d-block mb-2 py-2"
              >
                已發送好友請求
              </span>
              
              <span 
                v-else-if="friendshipStatus === 'accepted'"
                class="badge bg-success d-block mb-2 py-2"
              >
                ✓ 已是好友
              </span>
              
              <!-- 聊天按鈕 -->
              <button 
                class="btn btn-outline-primary w-100"
                @click="startChat"
              >
                開始聊天
              </button>
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

export default {
  name: 'UserProfilePopup',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    userId: {
      type: [Number, String],
      required: true
    },
    userName: {
      type: String,
      default: ''
    },
    userNickname: {
      type: String,
      default: ''
    }
  },
  emits: ['close', 'start-chat', 'friend-updated'],
  data() {
    return {
      loading: false,
      actionLoading: false,
      friendshipStatus: 'none',
      onlineStatus: null,
      userProfile: {}
    }
  },
  computed: {
    hasDetailInfo() {
      return this.userProfile.sex || 
             this.userProfile.birthday ||
             this.userProfile.nationality || 
             this.userProfile.city ||
             this.userProfile.star_sign || 
             this.userProfile.mbti || 
             this.userProfile.blood_type ||
             this.userProfile.religion ||
             this.userProfile.married ||
             this.userProfile.sns ||
             this.userProfile.university ||
             this.userProfile.find_meeting_type ||
             this.userProfile.interest ||
             this.userProfile.self_introduction
    }
  },
  watch: {
    show(newVal) {
      if (newVal && this.userId) {
        // 重置狀態，避免顯示上一個用戶的狀態
        this.friendshipStatus = 'none'
        this.onlineStatus = null
        this.userProfile = {}
        this.loadUserInfo()
      } else {
        // 關閉時重置狀態
        this.friendshipStatus = 'none'
        this.onlineStatus = null
        this.userProfile = {}
      }
    },
    userId(newVal, oldVal) {
      // 當 userId 改變時，重置狀態並重新載入
      if (newVal && newVal !== oldVal && this.show) {
        this.friendshipStatus = 'none'
        this.onlineStatus = null
        this.userProfile = {}
        this.loadUserInfo()
      }
    }
  },
  methods: {
    async loadUserInfo() {
      this.loading = true
      this.userProfile = {}
      // 先重置狀態，避免顯示錯誤的狀態
      this.friendshipStatus = 'none'
      
      try {
        // 先獲取好友狀態（最重要，優先載入）
        const statusData = await apiGet(`friends/status/${this.userId}`)
        console.log('Friendship status API response:', statusData)
        
        if (statusData.status === 'success') {
          // 使用新的字段名 friendship_status
          if (statusData.is_friend) {
            this.friendshipStatus = 'accepted'
          } else if (statusData.friendship_status) {
            this.friendshipStatus = statusData.friendship_status
          } else {
            this.friendshipStatus = 'none'
          }
          console.log('Friendship status set to:', this.friendshipStatus)
        } else {
          console.warn('Failed to load friendship status:', statusData)
          this.friendshipStatus = 'none'
        }
        
        // 獲取用戶公開資料（使用 friends/user-profile 路由，專門用於查看其他用戶的公開資料）
        const profileData = await apiGet(`friends/user-profile/${this.userId}`)
        console.log('User profile API response:', profileData)
        if (profileData.status === 'success') {
          this.userProfile = profileData.profile || {}
          console.log('User profile loaded:', this.userProfile)
          console.log('Has detail info:', this.hasDetailInfo)
        } else {
          console.warn('Failed to load user profile:', profileData)
          this.userProfile = {}
        }
        
        // 獲取在線狀態
        const onlineData = await apiGet(`user-status/${this.userId}`)
        if (onlineData.status === 'success') {
          this.onlineStatus = onlineData.is_online
        }
      } catch (error) {
        console.error('Error loading user info:', error)
        this.friendshipStatus = 'none'
      } finally {
        this.loading = false
      }
    },
    
    async addFriend() {
      // 先檢查當前狀態，避免重複發送
      if (this.friendshipStatus === 'pending_sent') {
        alert('您已經發送過好友請求了')
        return
      }
      
      if (this.friendshipStatus === 'accepted') {
        alert('你們已經是好友了')
        return
      }
      
      // 如果正在載入，等待載入完成
      if (this.loading) {
        alert('請稍候，正在載入用戶資訊...')
        return
      }
      
      // 發送前再次檢查狀態（防止狀態更新延遲）
      try {
        const statusData = await apiGet(`friends/status/${this.userId}`)
        if (statusData.status === 'success') {
          const currentStatus = statusData.is_friend ? 'accepted' : (statusData.friendship_status || 'none')
          if (currentStatus === 'pending_sent') {
            this.friendshipStatus = 'pending_sent'
            alert('您已經發送過好友請求了')
            return
          }
          if (currentStatus === 'accepted') {
            this.friendshipStatus = 'accepted'
            alert('你們已經是好友了')
            return
          }
        }
      } catch (error) {
        console.warn('Failed to re-check status before sending:', error)
        // 繼續發送，讓後端驗證
      }
      
      this.actionLoading = true
      try {
        // 確保 friend_id 是數字
        const friendId = parseInt(this.userId)
        if (isNaN(friendId)) {
          alert('無效的用戶ID')
          this.actionLoading = false
          return
        }
        
        console.log('Sending friend request to:', friendId, 'Current status:', this.friendshipStatus)
        const data = await apiPost('friends/add', { friend_id: friendId })
        console.log('Friend request response:', data)
        
        if (data.status === 'success') {
          this.friendshipStatus = 'pending_sent'
          this.$emit('friend-updated')
          alert('好友請求已發送！')
        } else {
          // 如果後端返回「已有待處理的好友請求」，更新狀態
          if (data.message && (data.message.includes('已有待處理') || data.message.includes('已是好友'))) {
            // 重新載入狀態以確保同步
            await this.loadUserInfo()
            // 不顯示錯誤訊息，因為狀態已經更新
            return
          }
          alert(data.message || '發送好友請求失敗')
        }
      } catch (error) {
        console.error('Error adding friend:', error)
        alert('發送好友請求失敗: ' + (error.message || '未知錯誤'))
      } finally {
        this.actionLoading = false
      }
    },
    
    async acceptFriend() {
      this.actionLoading = true
      try {
        const data = await apiPost('friends/accept', { friend_id: this.userId })
        if (data.status === 'success') {
          this.friendshipStatus = 'accepted'
          this.$emit('friend-updated')
          alert('已成為好友！')
        } else {
          alert(data.message || '接受好友請求失敗')
        }
      } catch (error) {
        console.error('Error accepting friend:', error)
        alert('接受好友請求失敗')
      } finally {
        this.actionLoading = false
      }
    },
    
    startChat() {
      this.$emit('start-chat', {
        user_id: this.userId,
        user_name: this.userProfile.user_name || this.userName,
        user_nickname: this.userProfile.user_nickname || this.userNickname
      })
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.modal {
  background: rgba(0,0,0,0.5);
}

.modal-dialog {
  max-width: 450px;
}

.user-avatar {
  position: relative;
  display: inline-block;
}

.avatar-circle {
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.avatar-circle.large {
  width: 80px;
  height: 80px;
  font-size: 32px;
}

.avatar-img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
}

.online-indicator {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #ccc;
  border: 3px solid #fff;
}

.online-indicator.online {
  background: #28a745;
}

.user-name {
  font-weight: 600;
}

/* 詳細資料樣式 */
.profile-details {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
}

.details-title {
  font-weight: 600;
  color: #495057;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 0.5rem;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-item.full-width {
  grid-column: span 2;
}

.detail-label {
  font-size: 0.75rem;
  color: #6c757d;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}

.detail-value {
  font-weight: 500;
  color: #2d3748;
}

.detail-section {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid #dee2e6;
}

.detail-text {
  margin-top: 0.25rem;
  margin-bottom: 0;
  color: #4a5568;
  font-size: 0.9rem;
  line-height: 1.5;
}

.sns-accounts {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.sns-badge {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.25rem 0.6rem;
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: 500;
}

.action-buttons {
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
}

.badge {
  font-size: 14px;
}
</style>
