<template>
  <div class="admin-meeting-chat-records">
    <h2>聚會聊天記錄查詢</h2>
    
    <div class="search-section mb-4">
      <div class="input-group" style="max-width: 300px;">
        <input 
          type="text" 
          class="form-control" 
          v-model="searchMeetingId"
          placeholder="輸入聚會ID"
          @keyup.enter="searchMeetingChats"
        >
        <button 
          class="btn btn-primary" 
          @click="searchMeetingChats"
        >
          查詢
        </button>
      </div>
    </div>

    <!-- 聊天記錄顯示 -->
    <div v-if="meetingInfo" class="meeting-info mb-4">
      <h3>聚會資訊</h3>
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">{{ meetingInfo.content }}</h5>
          <p class="card-text">
            <small class="text-muted">
              日期：{{ meetingInfo.event_date }} | 
              地點：{{ meetingInfo.event_place }}
            </small>
          </p>
        </div>
      </div>
    </div>

    <div v-if="chatMessages.length" class="chat-history">
      <h3>聊天記錄</h3>
      <div class="chat-messages">
        <div 
          v-for="message in chatMessages" 
          :key="message.message_id"
          class="message"
        >
          <div class="message-content">
            <div class="message-header">
              <span class="sender">{{ message.sender_name }}</span>
              <span class="time">{{ formatTime(message.timestamp) }}</span>
            </div>
            <div class="message-text">{{ message.content }}</div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="hasSearched" class="no-messages">
      <p class="text-muted">此聚會尚無任何訊息</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminMeetingChatRecords',
  data() {
    return {
      searchMeetingId: '',
      meetingInfo: null,
      chatMessages: [],
      hasSearched: false
    }
  },
  methods: {
    async searchMeetingChats() {
      if (!this.searchMeetingId.trim()) {
        alert('請輸入聚會ID')
        return
      }

      try {
        const response = await fetch(`http://localhost:8800/api/admin/meeting-chat/${this.searchMeetingId}`)
        const data = await response.json()
        
        if (data.status === 'success') {
          this.meetingInfo = data.meeting_info
          this.chatMessages = data.messages
          this.hasSearched = true
        } else {
          alert(data.message || '查詢失敗')
        }
      } catch (error) {
        console.error('Error searching meeting chats:', error)
        alert('查詢失敗')
      }
    },

    formatTime(timestamp) {
      return new Date(timestamp).toLocaleString()
    }
  }
}
</script>

<style scoped>
.admin-meeting-chat-records {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.chat-messages {
  max-height: 500px;
  overflow-y: auto;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 15px;
}

.message {
  margin-bottom: 15px;
  display: flex;
}

.message-content {
  max-width: 70%;
  padding: 10px;
  border-radius: 8px;
  background-color: #f8f9fa;
}

.message-header {
  font-size: 0.8em;
  margin-bottom: 5px;
}

.sender {
  font-weight: bold;
}

.time {
  color: #6c757d;
  margin-left: 10px;
}

.no-messages {
  text-align: center;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
}
</style>
