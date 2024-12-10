<template>
  <div class="admin-user-chat-records">
    <h2>用戶聊天記錄查詢</h2>
    
    <div class="search-section mb-4">
      <div class="input-group" style="max-width: 300px;">
        <input 
          type="text" 
          class="form-control" 
          v-model="searchUserId"
          placeholder="輸入用戶ID"
          @keyup.enter="searchUserChats"
        >
        <button 
          class="btn btn-primary" 
          @click="searchUserChats"
        >
          查詢
        </button>
      </div>
    </div>

    <!-- 聊天對象列表 -->
    <div v-if="chatPartners.length" class="chat-partners mb-4">
      <h3>聊天對象列表</h3>
      <div class="list-group">
        <button
          v-for="partner in chatPartners"
          :key="partner.user_id"
          class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
          @click="viewChatHistory(partner.user_id)"
        >
          <div>
            <span class="fw-bold">{{ partner.nickname || partner.user_name }}</span>
            <small class="text-muted ms-2">(ID: {{ partner.user_id }})</small>
          </div>
          <span class="badge bg-primary rounded-pill">{{ partner.message_count }} 則訊息</span>
        </button>
      </div>
    </div>

    <!-- 聊天記錄顯示 -->
    <div v-if="chatHistory.length" class="chat-history">
      <h3>最近聊天記錄</h3>
      <div class="chat-messages">
        <div v-for="message in chatHistory" 
             :key="message.message_id"
             class="message"
             :class="{ 'message-mine': message.sender_id === searchUserId }">
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
  </div>
</template>

<script>
export default {
  name: 'AdminUserChatRecords',
  data() {
    return {
      searchUserId: '',
      chatPartners: [],
      chatHistory: [],
      selectedPartnerId: null
    }
  },
  methods: {
    async searchUserChats() {
      if (!this.searchUserId.trim()) {
        alert('請輸入用戶ID')
        return
      }

      try {
        const response = await fetch(`http://localhost:8800/api/admin/chat-partners/${this.searchUserId}`)
        const data = await response.json()
        
        if (data.status === 'success') {
          this.chatPartners = data.partners
          this.chatHistory = []
        } else {
          alert(data.message || '查詢失敗')
        }
      } catch (error) {
        console.error('Error searching user chats:', error)
        alert('查詢失敗')
      }
    },

    async viewChatHistory(partnerId) {
      try {
        const response = await fetch(`http://localhost:8800/api/admin/chat-history`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            user1_id: this.searchUserId,
            user2_id: partnerId,
            limit: 20
          })
        })
        
        const data = await response.json()
        if (data.status === 'success') {
          this.chatHistory = data.messages
          this.selectedPartnerId = partnerId
        } else {
          alert(data.message || '獲取聊天記錄失敗')
        }
      } catch (error) {
        console.error('Error fetching chat history:', error)
        alert('獲取聊天記錄失敗')
      }
    },

    formatTime(timestamp) {
      return new Date(timestamp).toLocaleString()
    }
  }
}
</script>

<style scoped>
.admin-user-chat-records {
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

.message-mine {
  justify-content: flex-end;
}

.message-content {
  max-width: 70%;
  padding: 10px;
  border-radius: 8px;
  background-color: #f8f9fa;
}

.message-mine .message-content {
  background-color: #007bff;
  color: white;
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

.message-mine .message-header,
.message-mine .time {
  color: rgba(255, 255, 255, 0.8);
}

.message-text {
  margin-top: 5px;
}

.list-group-item {
  cursor: pointer;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}
</style>
