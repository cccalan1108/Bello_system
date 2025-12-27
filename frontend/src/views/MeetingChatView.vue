<template>
  <div class="meeting-chat-container">
    <div class="content-wrapper">
      <h2 class="mb-4">聚會聊天</h2>
      
      <!-- 聚會列表 -->
      <div class="meetings-section mb-4">
        <h3>我的聚會</h3>
        <div class="row g-5">
          <div v-if="!myMeetings.length" class="col-12 text-center">
            <p class="text-muted">目前沒有進行中的聚會</p>
          </div>
          <div v-for="meeting in myMeetings" :key="meeting.meeting_id" class="col-lg-6">
            <div class="meeting-card">
              <div class="card-body p-4">
                <h5 class="card-title mb-3">{{ meeting.content }}</h5>
                <p class="card-text mb-4">
                  <small class="text-muted">
                    參與人數: {{ meeting.num_participant }}/{{ meeting.max_participants || '-' }}
                  </small>
                </p>
                <button 
                  class="btn btn-primary w-100"
                  @click="openChat(meeting)"
                >
                  開啟聊天室
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 聊天室彈窗 -->
    <div v-if="selectedMeeting" class="chat-modal">
      <div class="chat-window">
        <div class="chat-header">
          <div class="header-left">
            <h4>{{ selectedMeeting.content }}</h4>
            <span class="participant-count text-muted ms-2">
              ({{ participants.length }} 位成員)
            </span>
          </div>
          <div class="header-right">
            <button 
              class="btn btn-outline-secondary btn-sm me-2"
              @click="toggleParticipantList"
            >
              <span v-if="!showParticipants">👥 查看成員</span>
              <span v-else>💬 返回聊天</span>
            </button>
            <button class="btn-close" @click="closeChat"></button>
          </div>
        </div>
        
        <!-- 成員列表 -->
        <div v-if="showParticipants" class="participant-list">
          <h5 class="mb-3">聚會成員</h5>
          <div 
            v-for="participant in participants" 
            :key="participant.user_id"
            class="participant-item"
            :class="{ 'is-me': participant.user_id === currentUserId }"
            @click="participant.user_id !== currentUserId && showUserProfile({ 
              sender_id: participant.user_id, 
              sender_name: participant.user_name,
              sender_nickname: participant.user_nickname
            })"
          >
            <div class="participant-avatar">
              <img v-if="participant.avatar_url" :src="participant.avatar_url" alt="頭像">
              <span v-else>{{ participant.user_nickname?.charAt(0) || participant.user_name?.charAt(0) }}</span>
            </div>
            <div class="participant-info">
              <div class="participant-name">
                {{ participant.user_name }}
                <span v-if="participant.is_host" class="badge bg-primary ms-1">主辦人</span>
                <span v-if="participant.user_id === currentUserId" class="badge bg-secondary ms-1">我</span>
              </div>
              <div class="participant-nickname text-muted">{{ participant.user_nickname }}</div>
            </div>
          </div>
        </div>
        
        <div v-else class="chat-messages" ref="messageContainer">
          <div v-for="message in messages" :key="message.id" 
               class="message" 
               :class="{ 'message-mine': message.sender_id === currentUserId }">
            <div class="message-content">
              <div class="message-header">
                <span 
                  class="sender" 
                  :class="{ 'clickable': message.sender_id !== currentUserId }"
                  @click="message.sender_id !== currentUserId && showUserProfile(message)"
                >
                  {{ message.sender_name }}
                </span>
                <span class="time">{{ formatTime(message.timestamp) }}</span>
              </div>
              <div class="message-text">{{ message.content }}</div>
            </div>
          </div>
        </div>
        
        <div v-if="!showParticipants" class="chat-input">
          <div class="input-group">
            <input
              type="text"
              class="form-control"
              v-model="messageText"
              placeholder="輸入訊息..."
              @keyup.enter="sendMessage"
            >
            <button class="btn btn-primary" @click="sendMessage">發送</button>
          </div>
        </div>
      </div>
    </div>

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
import UserProfilePopup from '@/components/UserProfilePopup.vue'

export default {
  name: 'MeetingChatView',
  components: {
    UserProfilePopup
  },
  data() {
    return {
      myMeetings: [],
      selectedMeeting: null,
      messageText: '',
      messages: [],
      currentUserId: null,
      pollingInterval: null,
      // 成員列表
      participants: [],
      showParticipants: false,
      // 用戶資訊彈窗
      showProfilePopup: false,
      selectedUser: {
        user_id: null,
        user_name: '',
        user_nickname: ''
      }
    }
  },
  methods: {
    async fetchMyMeetings() {
      const user = getUser()
      if (!user) {
        this.$router.push('/login')
        return
      }
      this.currentUserId = user.user_id
      
      try {
        const data = await apiGet(`my-meetings/${user.user_id}`)
        console.log(data)
        if (data.status === 'success') {
          this.myMeetings = data.meetings.ongoing || []
        }
      } catch (error) {
        console.error('Error fetching meetings:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        }
      }
    },
    
    openChat(meeting) {
      this.selectedMeeting = meeting
      this.showParticipants = false
      this.loadChatHistory()
      this.loadParticipants()
      this.startPolling()
    },
    
    closeChat() {
      this.selectedMeeting = null
      this.messages = []
      this.messageText = ''
      this.participants = []
      this.showParticipants = false
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
      }
    },
    
    toggleParticipantList() {
      this.showParticipants = !this.showParticipants
    },
    
    async loadParticipants() {
      if (!this.selectedMeeting) return
      
      try {
        const data = await apiGet(`meeting/${this.selectedMeeting.meeting_id}/participants`)
        if (data.status === 'success') {
          this.participants = data.participants
        }
      } catch (error) {
        console.error('Error loading participants:', error)
      }
    },
    
    async loadChatHistory() {
      if (!this.selectedMeeting) return
      
      try {
        const data = await apiGet(`meeting-chat/${this.selectedMeeting.meeting_id}`)
        if (data.status === 'success') {
          this.messages = data.messages
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
      this.pollingInterval = setInterval(() => {
        this.loadChatHistory()
      }, 1000)
    },
    
    async sendMessage() {
      if (!this.messageText.trim()) return
      
      try {
        const data = await apiPost('meeting-chat/send', {
          meeting_id: this.selectedMeeting.meeting_id,
          content: this.messageText
        })
        
        if (data.status === 'success') {
          this.messageText = ''
          this.loadChatHistory()
        }
      } catch (error) {
        console.error('Error sending message:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        }
      }
    },
    
    showUserProfile(message) {
      this.selectedUser = {
        user_id: message.sender_id,
        user_name: message.sender_real_name || message.sender_name,
        user_nickname: message.sender_nickname || message.sender_name
      }
      this.showProfilePopup = true
    },
    
    goToPrivateChat(user) {
      // 關閉聊天室
      this.closeChat()
      // 導向私人聊天頁面
      this.$router.push({
        path: '/chat',
        query: {
          userId: user.user_id,
          userName: user.user_name || user.user_nickname
        }
      })
    },
    
    onFriendUpdated() {
      // 好友狀態更新後的回調
      console.log('Friend status updated')
    },
    
    scrollToBottom() {
      const container = this.$refs.messageContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },
    
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleString()
    }
  },
  created() {
    this.fetchMyMeetings()
  },
  beforeUnmount() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval)
    }
  }
}
</script>

<style scoped>
.meeting-chat-container {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 2rem 0;
}

.content-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

.meeting-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
  border: none;
  height: 100%;
}

.card-body {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.card-text {
  flex-grow: 1;
}

.meeting-card:hover {
  transform: translateY(-5px);
}

.chat-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.chat-window {
  width: 90%;
  max-width: 800px;
  height: 80vh;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  background: #f8f9fa;
  border-radius: 1rem 1rem 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.participant-count {
  font-size: 0.875rem;
}

/* 成員列表樣式 */
.participant-list {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  background: #fff;
}

.participant-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.participant-item:hover:not(.is-me) {
  background-color: #f8f9fa;
}

.participant-item.is-me {
  cursor: default;
  background-color: #e3f2fd;
}

.participant-avatar {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 18px;
  margin-right: 1rem;
  overflow: hidden;
}

.participant-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.participant-info {
  flex: 1;
}

.participant-name {
  font-weight: 600;
  color: #2d3748;
}

.participant-nickname {
  font-size: 0.875rem;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  background: #fff;
}

.message {
  margin-bottom: 1rem;
  max-width: 75%;
}

.message-mine {
  margin-left: auto;
}

.message-content {
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  background: #f8f9fa;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message-mine .message-content {
  background: #0d6efd;
  color: white;
}

.message-header {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.sender {
  font-weight: 600;
}

.sender.clickable {
  cursor: pointer;
  color: #667eea;
  transition: color 0.2s;
}

.sender.clickable:hover {
  color: #764ba2;
  text-decoration: underline;
}

.message-mine .sender {
  color: white;
}

.time {
  color: #6c757d;
  margin-left: 0.5rem;
  font-size: 0.75rem;
}

.message-mine .time {
  color: rgba(255, 255, 255, 0.8);
}

.chat-input {
  padding: 1rem;
  background: #fff;
  border-top: 1px solid #dee2e6;
  border-radius: 0 0 1rem 1rem;
}

.input-group {
  background: #fff;
  border-radius: 0.5rem;
  overflow: hidden;
}

.form-control {
  border: 1px solid #dee2e6;
  padding: 0.75rem;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
}
</style>
