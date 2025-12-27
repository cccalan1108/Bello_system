<template>
  <div class="admin-meeting-chat-records">
    <h2>聚會聊天記錄</h2>
    
    <!-- 搜尋區塊 -->
    <div class="search-section mb-4">
      <div class="input-group" style="max-width: 400px;">
        <input 
          type="text" 
          class="form-control" 
          v-model="searchMeetingId"
          placeholder="輸入聚會ID查詢特定聚會"
          @keyup.enter="searchMeetingChats"
        >
        <button 
          class="btn btn-primary" 
          @click="searchMeetingChats"
        >
          查詢
        </button>
        <button 
          class="btn btn-outline-secondary" 
          @click="clearSearch"
          v-if="searchMeetingId || selectedMeeting"
        >
          清除
        </button>
      </div>
    </div>

    <!-- 所有聚會聊天列表 -->
    <div v-if="!selectedMeeting" class="meetings-list">
      <h3>有聊天記錄的聚會 <small class="text-muted">(共 {{ totalMeetings }} 個聚會)</small></h3>
      
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">載入中...</span>
        </div>
      </div>
      
      <div v-else class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr>
              <th>ID</th>
              <th>聚會主題</th>
              <th>類型</th>
              <th>發起人</th>
              <th>日期</th>
              <th>訊息數</th>
              <th>狀態</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="meeting in meetings" :key="meeting.meeting_id">
              <td>{{ meeting.meeting_id }}</td>
              <td>{{ meeting.content }}</td>
              <td><span class="badge bg-info">{{ meeting.meeting_type }}</span></td>
              <td>{{ meeting.holder_name }}</td>
              <td>{{ meeting.event_date }}</td>
              <td><span class="badge bg-primary">{{ meeting.message_count }}</span></td>
              <td>
                <span 
                  class="status-badge"
                  :class="{
                    'status-ongoing': meeting.status === '進行中' || meeting.status === 'Ongoing',
                    'status-finished': meeting.status === '已完成' || meeting.status === 'Finished',
                    'status-canceled': meeting.status === '已取消' || meeting.status === 'Canceled'
                  }"
                >
                  {{ meeting.status === 'Ongoing' ? '進行中' : meeting.status === 'Finished' ? '已完成' : meeting.status === 'Canceled' ? '已取消' : meeting.status }}
                </span>
              </td>
              <td>
                <button 
                  class="btn btn-sm btn-outline-primary"
                  @click="viewMeetingChat(meeting)"
                >
                  查看記錄
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-if="!loading && meetings.length === 0" class="text-center py-4 text-muted">
        目前沒有任何聚會聊天記錄
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

    <!-- 聚會聊天記錄詳情 -->
    <div v-if="selectedMeeting" class="chat-detail">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h3>{{ selectedMeeting.content }} 的聊天記錄</h3>
        <button class="btn btn-secondary" @click="backToList">
          ← 返回列表
        </button>
      </div>
      
      <!-- 聚會資訊卡片 -->
      <div class="card mb-4">
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <p><strong>聚會ID：</strong>{{ selectedMeeting.meeting_id }}</p>
              <p><strong>類型：</strong>{{ selectedMeeting.meeting_type }}</p>
              <p><strong>發起人：</strong>{{ selectedMeeting.holder_name }}</p>
            </div>
            <div class="col-md-6">
              <p><strong>日期：</strong>{{ selectedMeeting.event_date }}</p>
              <p><strong>地點：</strong>{{ selectedMeeting.event_place }}</p>
              <p><strong>狀態：</strong>{{ selectedMeeting.status }}</p>
            </div>
          </div>
        </div>
      </div>
      
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
      
      <div v-if="chatMessages.length === 0" class="no-messages">
        <p class="text-muted">此聚會尚無任何訊息</p>
      </div>
    </div>
  </div>
</template>

<script>
import { apiGet } from '@/utils/api'

export default {
  name: 'AdminMeetingChatRecords',
  data() {
    return {
      searchMeetingId: '',
      meetings: [],
      totalMeetings: 0,
      currentPage: 1,
      itemsPerPage: 20,
      loading: false,
      selectedMeeting: null,
      chatMessages: []
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalMeetings / this.itemsPerPage)
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
    async loadMeetings() {
      this.loading = true
      try {
        const data = await apiGet(`admin/all-meeting-chats?page=${this.currentPage}&limit=${this.itemsPerPage}`)
        
        if (data.status === 'success') {
          this.meetings = data.meetings
          this.totalMeetings = data.total
        } else {
          alert(data.message || '獲取聚會列表失敗')
        }
      } catch (error) {
        console.error('Error loading meetings:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        } else {
          alert('獲取聚會列表失敗')
        }
      } finally {
        this.loading = false
      }
    },
    
    async searchMeetingChats() {
      if (!this.searchMeetingId.trim()) {
        alert('請輸入聚會ID')
        return
      }

      try {
        const data = await apiGet(`admin/meeting-chat/${this.searchMeetingId}`)
        
        if (data.status === 'success') {
          this.selectedMeeting = {
            meeting_id: this.searchMeetingId,
            content: data.meeting_info.content,
            meeting_type: data.meeting_info.meeting_type,
            holder_name: data.meeting_info.holder_name,
            event_date: data.meeting_info.event_date,
            event_place: data.meeting_info.event_place,
            status: data.meeting_info.status
          }
          this.chatMessages = data.messages
        } else {
          alert(data.message || '查詢失敗')
        }
      } catch (error) {
        console.error('Error searching meeting chats:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        } else {
          alert('查詢失敗')
        }
      }
    },
    
    async viewMeetingChat(meeting) {
      try {
        const data = await apiGet(`admin/meeting-chat/${meeting.meeting_id}`)
        
        if (data.status === 'success') {
          this.selectedMeeting = meeting
          this.chatMessages = data.messages
        } else {
          alert(data.message || '獲取聊天記錄失敗')
        }
      } catch (error) {
        console.error('Error fetching meeting chat:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        } else {
          alert('獲取聊天記錄失敗')
        }
      }
    },
    
    backToList() {
      this.selectedMeeting = null
      this.chatMessages = []
      if (!this.searchMeetingId) {
        this.loadMeetings()
      }
    },
    
    clearSearch() {
      this.searchMeetingId = ''
      this.selectedMeeting = null
      this.chatMessages = []
      this.currentPage = 1
      this.loadMeetings()
    },
    
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        this.loadMeetings()
      }
    },

    formatTime(timestamp) {
      if (!timestamp) return '-'
      return new Date(timestamp).toLocaleString()
    }
  },
  mounted() {
    this.loadMeetings()
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

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #212529;
  background-color: #e9ecef;
}

.status-ongoing {
  background-color: #d1e7dd;
  color: #212529;
}

.status-finished {
  background-color: #e2e3e5;
  color: #212529;
}

.status-canceled {
  background-color: #f8d7da;
  color: #212529;
}
</style>
