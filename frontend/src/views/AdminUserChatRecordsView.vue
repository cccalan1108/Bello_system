<template>
  <div class="admin-user-chat-records">
    <h2>用戶聊天記錄</h2>
    
    <!-- 搜尋區塊 -->
    <div class="search-section mb-4">
      <div class="input-group" style="max-width: 400px;">
        <input 
          type="text" 
          class="form-control" 
          v-model="searchUserId"
          placeholder="輸入用戶ID查詢特定用戶的聊天"
          @keyup.enter="searchUserChats"
        >
        <button 
          class="btn btn-primary" 
          @click="searchUserChats"
        >
          查詢
        </button>
        <button 
          class="btn btn-outline-secondary" 
          @click="clearSearch"
          v-if="searchUserId || selectedConversation"
        >
          清除
        </button>
      </div>
    </div>

    <!-- 所有對話列表 -->
    <div v-if="!selectedConversation" class="conversations-list">
      <h3>所有私人聊天對話 <small class="text-muted">(共 {{ totalConversations }} 組對話)</small></h3>
      
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">載入中...</span>
        </div>
      </div>
      
      <div v-else class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr>
              <th>用戶 1</th>
              <th>用戶 2</th>
              <th>訊息數</th>
              <th>最後訊息時間</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="conv in conversations" :key="`${conv.user1_id}-${conv.user2_id}`">
              <td>
                <div>{{ conv.user1_nickname || conv.user1_name }}</div>
                <small class="text-muted">ID: {{ conv.user1_id }}</small>
              </td>
              <td>
                <div>{{ conv.user2_nickname || conv.user2_name }}</div>
                <small class="text-muted">ID: {{ conv.user2_id }}</small>
              </td>
              <td><span class="badge bg-primary">{{ conv.message_count }}</span></td>
              <td>{{ formatTime(conv.last_message_time) }}</td>
              <td>
                <button 
                  class="btn btn-sm btn-outline-primary"
                  @click="viewConversation(conv)"
                >
                  查看記錄
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 分頁 -->
      <nav v-if="totalPages > 1" class="mt-3">
        <ul class="pagination justify-content-center">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">上一頁</a>
          </li>
          <li v-for="page in displayedPages" :key="page" class="page-item" :class="{ active: page === currentPage }">
            <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">下一頁</a>
          </li>
        </ul>
      </nav>
    </div>

    <!-- 聊天記錄詳情 -->
    <div v-if="selectedConversation" class="chat-detail">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h3>
          {{ selectedConversation.user1_nickname || selectedConversation.user1_name }}
          <i class="bi bi-arrow-left-right mx-2"></i>
          {{ selectedConversation.user2_nickname || selectedConversation.user2_name }}
          的聊天記錄
        </h3>
        <button class="btn btn-secondary" @click="backToList">
          ← 返回列表
        </button>
      </div>
      
      <div class="chat-messages">
        <div v-for="message in chatHistory" 
             :key="message.message_id"
             class="message"
             :class="{ 'message-right': message.sender_id === selectedConversation.user1_id }">
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
import { apiGet, apiPost } from '@/utils/api'

export default {
  name: 'AdminUserChatRecords',
  data() {
    return {
      searchUserId: '',
      conversations: [],
      totalConversations: 0,
      currentPage: 1,
      itemsPerPage: 20,
      loading: false,
      selectedConversation: null,
      chatHistory: []
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalConversations / this.itemsPerPage)
    },
    displayedPages() {
      const delta = 2
      const range = []
      for (let i = Math.max(1, this.currentPage - delta); 
           i <= Math.min(this.totalPages, this.currentPage + delta); 
           i++) {
        range.push(i)
      }
      return range
    }
  },
  methods: {
    async loadConversations() {
      this.loading = true
      try {
        const data = await apiGet(`admin/all-private-chats?page=${this.currentPage}&limit=${this.itemsPerPage}`)
        
        if (data.status === 'success') {
          this.conversations = data.conversations
          this.totalConversations = data.total
        } else {
          alert(data.message || '獲取對話列表失敗')
        }
      } catch (error) {
        console.error('Error loading conversations:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        } else {
          alert('獲取對話列表失敗')
        }
      } finally {
        this.loading = false
      }
    },
    
    async searchUserChats() {
      if (!this.searchUserId.trim()) {
        alert('請輸入用戶ID')
        return
      }

      this.loading = true
      try {
        const data = await apiGet(`admin/chat-partners/${this.searchUserId}`)
        
        if (data.status === 'success') {
          // 將搜尋結果轉換為對話格式
          this.conversations = data.partners.map(partner => ({
            user1_id: parseInt(this.searchUserId),
            user2_id: partner.user_id,
            user1_name: '搜尋用戶',
            user1_nickname: `ID: ${this.searchUserId}`,
            user2_name: partner.user_name,
            user2_nickname: partner.nickname,
            message_count: partner.message_count,
            last_message_time: null
          }))
          this.totalConversations = data.partners.length
          this.selectedConversation = null
        } else {
          alert(data.message || '查詢失敗')
        }
      } catch (error) {
        console.error('Error searching user chats:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        } else {
          alert('查詢失敗')
        }
      } finally {
        this.loading = false
      }
    },
    
    async viewConversation(conv) {
      try {
        const data = await apiPost('admin/chat-history', {
          user1_id: conv.user1_id,
          user2_id: conv.user2_id,
          limit: 100
        })
        
        if (data.status === 'success') {
          this.chatHistory = data.messages
          this.selectedConversation = conv
        } else {
          alert(data.message || '獲取聊天記錄失敗')
        }
      } catch (error) {
        console.error('Error fetching chat history:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        } else {
          alert('獲取聊天記錄失敗')
        }
      }
    },
    
    backToList() {
      this.selectedConversation = null
      this.chatHistory = []
      if (!this.searchUserId) {
        this.loadConversations()
      }
    },
    
    clearSearch() {
      this.searchUserId = ''
      this.selectedConversation = null
      this.chatHistory = []
      this.currentPage = 1
      this.loadConversations()
    },
    
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        this.loadConversations()
      }
    },

    formatTime(timestamp) {
      if (!timestamp) return '-'
      return new Date(timestamp).toLocaleString()
    }
  },
  mounted() {
    this.loadConversations()
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
  background-color: #fff;
}

.message {
  margin-bottom: 15px;
  display: flex;
}

.message-right {
  justify-content: flex-end;
}

.message-content {
  max-width: 70%;
  padding: 10px;
  border-radius: 8px;
  background-color: #f8f9fa;
}

.message-right .message-content {
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

.message-right .message-header,
.message-right .time {
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

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
}
</style>
