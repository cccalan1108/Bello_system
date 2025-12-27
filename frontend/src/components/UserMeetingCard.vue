<template>
  <div class="card mb-4">
    <div class="card-body">
      <h5 class="card-title">
        {{ meeting.content || meeting.title }}
        <span v-if="meeting.has_password" class="ms-2" title="需要密碼才能加入">🔒</span>
      </h5>
      <div class="card-text">
        <p>日期：{{ formatDate(meeting.date) }}</p>
        <p>時間：{{ meeting.start_time }} - {{ meeting.end_time }}</p>
        <p>
          地點：{{ meeting.place || meeting.city || '未指定' }}
          <span 
            v-if="meeting.latitude && meeting.longitude" 
            class="map-icon" 
            title="查看地圖"
            @click="handleShowMap"
          >📍</span>
        </p>
        <p>人數：{{ meeting.num_participant || meeting.current_members || 0 }} / 
              {{ meeting.max_participants || meeting.max_members || 0 }}</p>
        <p v-if="showStatus">狀態：{{ getStatusText(meeting.status) }}</p>
        <p v-if="meeting.holder_name">舉辦者：{{ meeting.holder_name }}</p>
      </div>
      
      <div v-if="isJoinable" class="mt-3">
        <button 
          class="btn btn-primary"
          @click="handleJoinMeeting"
          :disabled="(meeting.num_participant >= meeting.max_participants) || 
                    (meeting.current_members >= meeting.max_members)"
        >
          加入聚會
        </button>
      </div>

      <div v-if="!isJoinable" class="mt-3">
        <button 
          v-if="showLeaveButton && meeting.holder_id !== currentUserId"
          class="btn btn-danger me-2"
          @click="$emit('leave', meeting.meeting_id)"
        >
          退出聚會
        </button>
        
        <template v-if="showManageButtons">
          <button 
            class="btn btn-warning me-2"
            @click="$emit('finish', meeting.meeting_id)"
          >
            結束聚會
          </button>
          <button 
            class="btn btn-danger"
            @click="$emit('cancel', meeting.meeting_id)"
          >
            取消聚會
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { getUser } from '@/utils/api'

export default {
  name: 'UserMeetingCard',
  props: {
    meeting: {
      type: Object,
      required: true
    },
    isJoinable: {
      type: Boolean,
      default: false
    },
    showLeaveButton: {
      type: Boolean,
      default: false
    },
    showManageButtons: {
      type: Boolean,
      default: false
    },
    showStatus: {
      type: Boolean,
      default: true
    },
    currentUserId: {
      type: [Number, String],
      default: null
    }
  },
  emits: ['join-meeting', 'leave', 'finish', 'cancel', 'show-map'],
  methods: {
    formatDate(date) {
      if (!date) return 'Invalid Date'
      try {
        return new Date(date).toLocaleDateString('zh-TW')
      } catch (e) {
        console.error('Date formatting error:', e)
        return 'Invalid Date'
      }
    },
    getStatusText(status) {
      const statusMap = {
        'Ongoing': '進行中',
        'Finished': '已結束',
        'Cancelled': '已取消'
      }
      return statusMap[status] || status || '進行中'
    },
    handleJoinMeeting() {
      console.log('UserMeetingCard - Meeting data:', this.meeting);
      console.log('UserMeetingCard - Meeting ID:', this.meeting.meeting_id);
      const user = getUser()
      if (!user || !user.user_id) {
        alert('請先登入')
        this.$router.push('/login')
        return
      }
      this.$emit('join-meeting', this.meeting.meeting_id)
    },
    handleShowMap() {
      this.$emit('show-map', {
        place: this.meeting.place,
        address: this.meeting.address,
        latitude: this.meeting.latitude,
        longitude: this.meeting.longitude
      })
    }
  }
}
</script>

<style scoped>
.card {
  border: none;
  border-radius: 20px;
  background: linear-gradient(145deg, #ffffff 0%, #fff5f5 100%);
  box-shadow: 0 4px 20px rgba(255, 107, 107, 0.1);
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  overflow: hidden;
  position: relative;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #FF6B6B 0%, #FFB6C1 50%, #4ECDC4 100%);
}

.card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 12px 40px rgba(255, 107, 107, 0.25);
}

.card-body {
  padding: 1.5rem;
}

.card-title {
  font-family: 'Nunito', sans-serif;
  font-weight: 800;
  font-size: 1.2rem;
  color: #343A40;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-text p {
  margin-bottom: 0.6rem;
  color: #6C757D;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.card-text p::before {
  font-size: 1rem;
  margin-right: 0.3rem;
}

.map-icon {
  cursor: pointer;
  font-size: 1.2em;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  display: inline-block;
}

.map-icon:hover {
  transform: scale(1.4) rotate(10deg);
}

.btn {
  font-family: 'Nunito', sans-serif;
  font-weight: 600;
  border-radius: 50px;
  padding: 0.5rem 1.2rem;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #E85555 0%, #FF6B6B 100%);
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

.btn-primary:disabled {
  background: #CED4DA;
  box-shadow: none;
  transform: none;
}

.btn-danger {
  background: linear-gradient(135deg, #FF6B6B 0%, #ff8585 100%);
}

.btn-danger:hover {
  background: linear-gradient(135deg, #E85555 0%, #FF6B6B 100%);
}

.btn-warning {
  background: linear-gradient(135deg, #FFE66D 0%, #ffe066 100%);
  color: #343A40;
}

.btn-warning:hover {
  background: linear-gradient(135deg, #ffd93d 0%, #FFE66D 100%);
}

/* 可愛的鎖頭圖示動畫 */
.card-title span {
  display: inline-block;
  transition: transform 0.3s ease;
}

.card-title span:hover {
  transform: scale(1.2) rotate(-10deg);
}
</style>