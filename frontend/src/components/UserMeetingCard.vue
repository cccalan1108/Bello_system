<template>
  <div class="card mb-4">
    <div class="card-body">
      <h5 class="card-title">{{ meeting.content || meeting.title }}</h5>
      <div class="card-text">
        <p>日期：{{ formatDate(meeting.date) }}</p>
        <p>時間：{{ meeting.start_time }} - {{ meeting.end_time }}</p>
        <p>地點：{{ meeting.place || meeting.city || '未指定' }}</p>
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
      const user = JSON.parse(localStorage.getItem('user'))
      if (!user || !user.user_id) {
        alert('請先登入')
        this.$router.push('/login')
        return
      }
      this.$emit('join-meeting', this.meeting.meeting_id)
    }
  }
}
</script>