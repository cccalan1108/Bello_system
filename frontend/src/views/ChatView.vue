<template>
  <div class="chat-container">
    <div class="content-wrapper">
      <div class="row g-4">
        <!-- 左側列表 -->
        <div class="col-md-4">
          <!-- 標籤切換 -->
          <div class="list-tabs mb-3">
            <button 
              class="tab-btn" 
              :class="{ active: activeTab === 'chats' }"
              @click="activeTab = 'chats'"
            >
              聊天列表
            </button>
            <button 
              class="tab-btn" 
              :class="{ active: activeTab === 'friends' }"
              @click="activeTab = 'friends'; loadFriends()"
            >
              好友列表
              <span v-if="pendingRequestsCount > 0" class="badge bg-danger ms-1">
                {{ pendingRequestsCount }}
              </span>
            </button>
          </div>

          <!-- 聊天列表 -->
          <div v-show="activeTab === 'chats'" class="chat-sidebar">
            <div class="chat-list">
              <div v-if="chatList.length === 0" class="no-chats">
                <p>目前沒有進行中的聊天</p>
              </div>
              <div v-else class="chat-items">
                <div v-for="chat in chatList" 
                     :key="chat.other_user_id"
                     @click="selectChat(chat.other_user_id, chat.other_user_name)"
                     class="chat-item"
                     :class="{ active: selectedUserId === chat.other_user_id }">
                  <div class="chat-avatar">
                    <img 
                      v-if="chat.avatar_url" 
                      :src="chat.avatar_url" 
                      class="avatar-img"
                      alt="avatar"
                    />
                    <div v-else class="avatar-circle">
                      {{ chat.other_user_name?.charAt(0) }}
                    </div>
                    <span 
                      class="online-dot" 
                      :class="{ online: friendsOnlineStatus[chat.other_user_id] }"
                    ></span>
                  </div>
                  <div class="chat-item-content">
                    <h5>{{ chat.other_user_name }}</h5>
                    <small>{{ chat.last_message_time || '尚未開始對話' }}</small>
                  </div>
                </div>
              </div>
            </div>
            <div class="sidebar-footer">
              <button class="btn btn-primary w-100" @click="showUserSearch = true">
                開始新對話
              </button>
            </div>
          </div>

          <!-- 好友列表 -->
          <div v-show="activeTab === 'friends'" class="friends-sidebar">
            <div class="friends-actions mb-3">
              <button class="btn btn-primary w-100" @click="showAddFriend = true">
                <i class="bi bi-person-plus"></i> 添加好友
              </button>
            </div>
            
            <!-- 待處理的好友請求 -->
            <div v-if="pendingRequests.length > 0" class="pending-section mb-3">
              <h6 class="section-title">好友請求 ({{ pendingRequests.length }})</h6>
              <div v-for="request in pendingRequests" :key="request.user_id" class="request-item">
                  <div class="user-avatar">
                    <img 
                      v-if="request.avatar_url" 
                      :src="request.avatar_url" 
                      class="avatar-img small"
                      alt="avatar"
                    />
                    <div v-else class="avatar-circle small">
                      {{ request.user_name?.charAt(0) }}
                    </div>
                  </div>
                  <div class="user-info">
                    <div class="user-name">{{ request.user_name }}</div>
                  </div>
                <div class="request-actions">
                  <button class="btn btn-success btn-sm" @click="acceptFriend(request.user_id)">
                    接受
                  </button>
                  <button class="btn btn-outline-secondary btn-sm ms-1" @click="rejectFriend(request.user_id)">
                    拒絕
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
              <div v-else-if="friends.length === 0" class="no-friends">
                <p class="text-muted">還沒有好友</p>
              </div>
              <div v-else class="friends-items">
                <div 
                  v-for="friend in friends" 
                  :key="friend.user_id"
                  class="friend-item"
                  @click="startChatWithFriend(friend)"
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
                  <button 
                    class="btn btn-sm btn-outline-primary chat-btn"
                    @click.stop="startChatWithFriend(friend)"
                  >
                    聊天
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右側聊天內容 -->
        <div class="col-md-8">
          <div class="chat-main">
            <div v-if="selectedUserId" class="chat-window">
              <div class="chat-header">
                <div class="chat-header-info">
                  <h4 
                    class="clickable-name"
                    @click="showUserProfile"
                    style="cursor: pointer;"
                  >
                    {{ selectedUserName }}
                  </h4>
                  <small v-if="selectedUserOnline !== null" :class="selectedUserOnline ? 'text-success' : 'text-muted'">
                    {{ selectedUserOnline ? '在線' : '離線' }}
                  </small>
                </div>
              </div>
              <div class="chat-messages" ref="messageContainer">
                <div v-if="chatHistory.length === 0" class="no-messages">
                  <p>還沒有任何對話，開始聊天吧！</p>
                </div>
                <div v-else>
                  <div v-for="message in chatHistory" 
                       :key="message.timestamp"
                       class="message"
                       :class="{ 'message-mine': message.sender_id === currentUserId }">
                    <div class="message-content">
                      <div class="message-text">{{ message.content }}</div>
                      <small class="message-time">{{ formatTime(message.timestamp) }}</small>
                    </div>
                  </div>
                </div>
              </div>
              <div class="chat-input">
                <div class="input-group">
                  <input type="text" 
                         class="form-control" 
                         v-model="newMessage"
                         @keyup.enter="sendMessage" 
                         placeholder="輸入訊息...">
                  <button class="btn btn-primary" @click="sendMessage">發送</button>
                </div>
              </div>
            </div>
            <div v-else class="no-chat-selected">
              <h4>選擇一個聊天對象開始對話</h4>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜尋用戶對話框 -->
    <div class="modal fade" :class="{ 'show d-block': showUserSearch }" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">選擇聊天對象</h5>
            <button type="button" class="btn-close" @click="closeUserSearch"></button>
          </div>
          <div class="modal-body">
            <div class="search-box mb-3">
              <input 
                type="text" 
                class="form-control" 
                v-model="searchQuery"
                placeholder="輸入用戶暱稱或ID搜尋..."
                @input="handleSearch"
              >
            </div>
            <div v-if="searchQuery && !filteredUsers.length" class="text-center text-muted my-3">
              請輸入搜尋關鍵字
            </div>
            <div class="user-list">
              <div v-for="user in filteredUsers" 
                   :key="user.user_id"
                   @click="startNewChat(user)"
                   class="user-item">
                <div class="user-info">
                  <div class="user-name">{{ user.user_name }}</div>
                  <div class="user-nickname text-muted">{{ user.user_nickname }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showUserSearch" class="modal-backdrop fade show"></div>

    <!-- 添加好友對話框 -->
    <AddFriendModal 
      :show="showAddFriend" 
      @close="showAddFriend = false"
      @friend-added="loadFriends"
    />

    <!-- 用戶資訊彈窗 -->
    <UserProfilePopup
      :show="showProfilePopup"
      :userId="selectedUser.user_id"
      :userName="selectedUser.user_name"
      :userNickname="selectedUser.user_nickname"
      @close="showProfilePopup = false"
      @start-chat="goToPrivateChat"
      @friend-updated="onFriendUpdated"
    />
  </div>
</template>

<script>
import { getUser, apiGet, apiPost } from '@/utils/api'
import AddFriendModal from '@/components/AddFriendModal.vue'
import UserProfilePopup from '@/components/UserProfilePopup.vue'

function debounce(fn, delay) {
  let timeout
  return function(...args) {
    clearTimeout(timeout)
    timeout = setTimeout(() => fn.apply(this, args), delay)
  }
}

export default {
  name: 'PrivateChatView',
  components: {
    AddFriendModal,
    UserProfilePopup
  },
  data() {
    return {
      currentUserId: null,
      activeTab: 'chats',
      // 聊天相關
      chatList: [],
      selectedUserId: null,
      selectedUserName: '',
      selectedUserOnline: null,
      chatHistory: [],
      newMessage: '',
      showUserSearch: false,
      searchQuery: '',
      filteredUsers: [],
      // 好友相關
      friends: [],
      friendsLoading: false,
      pendingRequests: [],
      showAddFriend: false,
      friendsOnlineStatus: {},
      pollingInterval: null,
      onlineStatusInterval: null,
      // 用戶資訊彈窗
      showProfilePopup: false,
      selectedUser: {
        user_id: null,
        user_name: '',
        user_nickname: ''
      }
    }
  },
  computed: {
    pendingRequestsCount() {
      return this.pendingRequests.length
    }
  },
  async created() {
    const user = getUser()
    if (!user || !user.user_id) {
      this.$router.push('/login')
      return
    }
    this.currentUserId = user.user_id
    
    // 更新自己的在線狀態
    this.updateMyOnlineStatus(true)
    
    await this.loadChatList()
    await this.loadFriends()
    
    // 檢查是否有從其他頁面傳來的用戶參數
    const { userId, userName } = this.$route.query
    if (userId && userName) {
      this.startNewChat({
        user_id: parseInt(userId),
        user_name: userName
      })
      // 清除 query 參數
      this.$router.replace({ path: '/chat' })
    }
    
    // 定期更新在線狀態
    this.onlineStatusInterval = setInterval(() => {
      this.updateMyOnlineStatus(true)
      this.loadFriendsOnlineStatus()
    }, 30000) // 每30秒更新一次
  },
  methods: {
    // ======= 在線狀態 =======
    async updateMyOnlineStatus(isOnline) {
      try {
        await apiPost('online-status', { is_online: isOnline })
      } catch (error) {
        console.error('Error updating online status:', error)
      }
    },
    
    async loadFriendsOnlineStatus() {
      for (const friend of this.friends) {
        try {
          const data = await apiGet(`user-status/${friend.user_id}`)
          if (data.status === 'success') {
            this.friendsOnlineStatus[friend.user_id] = data.is_online
            friend.is_online = data.is_online
          }
        } catch (error) {
          console.error('Error loading friend online status:', error)
        }
      }
    },

    // ======= 好友相關 =======
    async loadFriends() {
      this.friendsLoading = true
      try {
        const data = await apiGet('friends')
        console.log('ChatView Friends API response:', data)
        if (data.status === 'success') {
          this.friends = data.friends
          console.log('Friends with avatar_url:', this.friends.map(f => ({ name: f.user_name, avatar: f.avatar_url })))
          // 更新在線狀態映射
          this.friends.forEach(f => {
            this.friendsOnlineStatus[f.user_id] = f.is_online
          })
        }
        
        // 同時加載待處理的好友請求
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
    
    async rejectFriend(friendId) {
      try {
        const data = await apiPost('friends/reject', { friend_id: friendId })
        if (data.status === 'success') {
          this.pendingRequests = this.pendingRequests.filter(r => r.user_id !== friendId)
        } else {
          alert(data.message || '拒絕好友請求失敗')
        }
      } catch (error) {
        console.error('Error rejecting friend:', error)
        alert('拒絕好友請求失敗')
      }
    },
    
    startChatWithFriend(friend) {
      this.activeTab = 'chats'
      this.startNewChat({
        user_id: friend.user_id,
        user_name: friend.user_name
      })
    },

    // ======= 聊天相關 =======
    async loadChatList() {
      try {
        const data = await apiGet('my-chats')
        if (data.status === 'success') {
          const sortedChats = data.chats.sort((a, b) => {
            const timeA = a.last_message_time ? new Date(a.last_message_time).getTime() : 0
            const timeB = b.last_message_time ? new Date(b.last_message_time).getTime() : 0
            return timeB - timeA
          })
          
          // 如果當前選中的好友不在列表中（還沒有聊天記錄），保留它
          if (this.selectedUserId) {
            const selectedChatExists = sortedChats.some(
              chat => chat.other_user_id === this.selectedUserId
            )
            if (!selectedChatExists) {
              // 從當前 chatList 中找到選中的聊天並保留
              const currentSelectedChat = this.chatList.find(
                chat => chat.other_user_id === this.selectedUserId
              )
              if (currentSelectedChat) {
                sortedChats.unshift(currentSelectedChat)
              }
            }
          }
          
          this.chatList = sortedChats
        }
      } catch (error) {
        console.error('Error loading chat list:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        }
      }
    },
    
    async selectChat(userId, userName) {
      this.selectedUserId = userId
      this.selectedUserName = userName || this.getSelectedUserName()
      await this.loadChatHistory()
      await this.loadSelectedUserOnlineStatus()
      this.startPolling()
    },
    
    async loadSelectedUserOnlineStatus() {
      if (!this.selectedUserId) return
      try {
        const data = await apiGet(`user-status/${this.selectedUserId}`)
        if (data.status === 'success') {
          this.selectedUserOnline = data.is_online
        }
      } catch (error) {
        console.error('Error loading user online status:', error)
      }
    },
    
    async loadChatHistory() {
      if (!this.selectedUserId) return
      
      try {
        const data = await apiPost('private-chat/history', {
          user2_id: this.selectedUserId
        })
        if (data.status === 'success') {
          this.chatHistory = data.messages
          this.$nextTick(() => {
            this.scrollToBottom()
          })
        }
      } catch (error) {
        console.error('Error loading chat history:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        }
      }
    },
    
    startPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
      }
      // 延遲第一次調用，避免立即覆蓋新添加的聊天
      setTimeout(() => {
        // 立即執行一次
        Promise.all([
          this.loadChatList(),
          this.loadChatHistory()
        ])
        // 然後開始定期輪詢
        this.pollingInterval = setInterval(async () => {
          await Promise.all([
            this.loadChatList(),
            this.loadChatHistory()
          ])
        }, 1000)
      }, 500)
    },
    
    async sendMessage() {
      if (!this.newMessage.trim()) return
      
      try {
        const data = await apiPost('private-chat/send', {
          receiver_id: this.selectedUserId,
          content: this.newMessage
        })
        if (data.status === 'success') {
          this.newMessage = ''
          await this.loadChatHistory()
          await this.loadChatList()
        }
      } catch (error) {
        console.error('Error sending message:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        }
      }
    },
    
    async startNewChat(user) {
      this.selectedUserId = user.user_id
      this.selectedUserName = user.user_name
      
      const existingChat = this.chatList.find(chat => chat.other_user_id === user.user_id)
      if (!existingChat) {
        this.chatList.unshift({
          other_user_id: user.user_id,
          other_user_name: user.user_name,
          last_message_time: null
        })
      }
      
      this.showUserSearch = false
      await this.loadChatHistory()
      await this.loadSelectedUserOnlineStatus()
      this.startPolling()
    },
    
    getSelectedUserName() {
      if (this.selectedUserName) {
        return this.selectedUserName
      }
      const chat = this.chatList.find(chat => chat.other_user_id === this.selectedUserId)
      return chat ? chat.other_user_name : ''
    },
    
    scrollToBottom() {
      const container = this.$refs.messageContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },
    
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleString()
    },
    
    handleSearch: debounce(async function() {
      if (!this.searchQuery.trim()) {
        this.filteredUsers = [];
        return;
      }
      
      try {
        const data = await apiGet(`search-users?query=${encodeURIComponent(this.searchQuery)}`);
        if (data.status === 'success') {
          this.filteredUsers = data.users;
        }
      } catch (error) {
        console.error('Error searching users:', error);
      }
    }, 300),
    
    closeUserSearch() {
      this.showUserSearch = false;
      this.searchQuery = '';
      this.filteredUsers = [];
    },
    
    showUserProfile() {
      if (!this.selectedUserId) return
      
      // 從聊天列表或好友列表中獲取用戶資訊
      const chat = this.chatList.find(c => c.other_user_id === this.selectedUserId)
      const friend = this.friends.find(f => f.user_id === this.selectedUserId)
      
      this.selectedUser = {
        user_id: this.selectedUserId,
        user_name: this.selectedUserName || (chat ? chat.other_user_name : '') || (friend ? friend.user_name : ''),
        user_nickname: (chat ? chat.other_user_nickname : '') || (friend ? friend.user_nickname : '') || ''
      }
      
      this.showProfilePopup = true
    },
    
    goToPrivateChat(user) {
      // 如果點擊「開始聊天」，切換到該用戶的聊天
      this.showProfilePopup = false
      this.startNewChat({
        user_id: user.user_id,
        user_name: user.user_name || user.user_nickname
      })
    },
    
    onFriendUpdated() {
      // 好友狀態更新後，重新載入好友列表
      this.loadFriends()
    }
  },
  beforeUnmount() {
    // 更新離線狀態
    this.updateMyOnlineStatus(false)
    
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval)
    }
    if (this.onlineStatusInterval) {
      clearInterval(this.onlineStatusInterval)
    }
  }
}
</script>

<style scoped>
.chat-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.list-tabs {
  display: flex;
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.tab-btn {
  flex: 1;
  padding: 12px;
  border: none;
  background: #fff;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.tab-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.chat-sidebar, .friends-sidebar {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  height: calc(100vh - 180px);
  display: flex;
  flex-direction: column;
}

.friends-sidebar {
  padding: 15px;
  overflow-y: auto;
}

.section-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.pending-section {
  background: #fff8e6;
  border-radius: 8px;
  padding: 12px;
}

.request-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.request-item:last-child {
  border-bottom: none;
}

.friends-items {
  max-height: 400px;
  overflow-y: auto;
}

.friend-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.friend-item:hover {
  background-color: #f8f9fa;
}

.friend-avatar, .user-avatar, .chat-avatar {
  position: relative;
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
  font-size: 16px;
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

.online-dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ccc;
  border: 2px solid #fff;
}

.online-dot.online {
  background: #28a745;
}

.friend-info, .user-info {
  flex: 1;
}

.friend-name, .user-name {
  font-weight: 500;
}

.chat-btn {
  opacity: 0;
  transition: opacity 0.2s;
}

.friend-item:hover .chat-btn {
  opacity: 1;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.chat-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 8px;
}

.chat-item:hover, .chat-item.active {
  background: #f8f9fa;
}

.chat-item-content {
  flex: 1;
}

.chat-item h5 {
  margin: 0;
  font-size: 1rem;
}

.chat-item small {
  color: #6c757d;
  font-size: 0.8rem;
}

.sidebar-footer {
  padding: 15px;
  border-top: 1px solid #eee;
}

.chat-main {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  height: calc(100vh - 120px);
}

.chat-window {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.chat-header-info h4 {
  margin: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message {
  margin-bottom: 15px;
}

.message-content {
  max-width: 70%;
  padding: 12px;
  border-radius: 12px;
  background: #f8f9fa;
  display: inline-block;
}

.message-mine {
  text-align: right;
}

.message-mine .message-content {
  background: #0d6efd;
  color: white;
}

.message-time {
  display: block;
  font-size: 0.75rem;
  margin-top: 5px;
  color: #6c757d;
}

.message-mine .message-time {
  color: rgba(255,255,255,0.8);
}

.chat-input {
  padding: 15px;
  border-top: 1px solid #eee;
}

.no-chat-selected, .no-chats, .no-friends, .no-messages {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  text-align: center;
  padding: 20px;
}

.modal {
  background: rgba(0,0,0,0.5);
}

.user-list {
  max-height: 300px;
  overflow-y: auto;
}

.user-item {
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
}

.user-item:hover {
  background-color: #f8f9fa;
}

.user-nickname {
  font-size: 0.875rem;
}

.search-box {
  position: sticky;
  top: 0;
  background-color: white;
  z-index: 1;
}
</style>
