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
          <h4>{{ selectedMeeting.content }}</h4>
          <button class="btn-close" @click="closeChat"></button>
        </div>
        
        <div class="chat-messages" ref="messageContainer">
          <div v-for="message in messages" :key="message.id" 
               class="message" 
               :class="{ 'message-mine': message.sender_id === currentUserId }">
            <div class="message-content">
              <div class="message-header">
                <span class="sender">{{ message.sender_name }}</span>
                <span class="time">{{ formatTime(message.timestamp) }}</span>
              </div>
              <div class="message-text">{{ message.content }}</div>
            </div>
          </div>
        </div>
        
        <div class="chat-input">
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
  </div>
</template>

<script>
export default {
  name: 'MeetingChatView',
  data() {
    return {
      myMeetings: [],
      selectedMeeting: null,
      messageText: '',
      messages: [],
      currentUserId: null,
      pollingInterval: null
    }
  },
  methods: {
    async fetchMyMeetings() {
      const user = JSON.parse(localStorage.getItem('user'))
      if (!user) {
        this.$router.push('/login')
        return
      }
      this.currentUserId = user.user_id
      
      try {
        const response = await fetch(`http://localhost:8800/api/my-meetings/${user.user_id}`)
        const data = await response.json()
        console.log(data)
        if (data.status === 'success') {
          this.myMeetings = data.meetings.ongoing || []
        }
      } catch (error) {
        console.error('Error fetching meetings:', error)
      }
    },
    
    openChat(meeting) {
      this.selectedMeeting = meeting
      this.loadChatHistory()
      this.startPolling()
    },
    
    closeChat() {
      this.selectedMeeting = null
      this.messages = []
      this.messageText = ''
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
      }
    },
    
    async loadChatHistory() {
      try {
        const response = await fetch(`http://localhost:8800/api/meeting-chat/${this.selectedMeeting.meeting_id}`)
        const data = await response.json()
        if (data.status === 'success') {
          this.messages = data.messages
          this.$nextTick(() => {
            this.scrollToBottom()
          })
        }
      } catch (error) {
        console.error('Error loading chat history:', error)
      }
    },
    
    startPolling() {
      this.pollingInterval = setInterval(() => {
        this.loadChatHistory()
      }, 1000) // 每1秒更新一次
    },
    
    async sendMessage() {
      if (!this.messageText.trim()) return
      
      const user = JSON.parse(localStorage.getItem('user'))
      try {
        const response = await fetch('http://localhost:8800/api/meeting-chat/send', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            meeting_id: this.selectedMeeting.meeting_id,
            sender_id: user.user_id,
            content: this.messageText
          })
        })
        
        const data = await response.json()
        if (data.status === 'success') {
          this.messageText = ''
          this.loadChatHistory()
        }
      } catch (error) {
        console.error('Error sending message:', error)
      }
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
  beforeDestroy() {
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
