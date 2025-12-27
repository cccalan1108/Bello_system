<template>
  <div class="admin-meeting-list">
    <h2 class="mb-4">所有聚會列表</h2>
    
    <!-- 進行中的聚會 -->
    <div class="mb-5">
      <h3 class="mb-3">進行中的聚會</h3>
      <div class="row g-4">
        <div v-if="meetings.ongoing.length === 0" class="col-12 text-center">
          <p class="text-muted">目前沒有進行中的聚會</p>
        </div>
        <div v-for="meeting in meetings.ongoing" :key="meeting.meeting_id" class="col-md-6 col-lg-4">
          <MeetingCard 
            :meeting="meeting"
            :showAdminControls="true"
            @cancel="cancelMeeting"
            @finish="finishMeeting"
            @remove-user="removeUserFromMeeting"
          />
        </div>
      </div>
    </div>

    <!-- 已結束的聚會 -->
    <div class="mb-5">
      <h3 class="mb-3">已結束的聚會</h3>
      <div class="row g-4">
        <div v-if="meetings.finished.length === 0" class="col-12 text-center">
          <p class="text-muted">沒有已結束的聚會</p>
        </div>
        <div v-for="meeting in meetings.finished" :key="meeting.meeting_id" class="col-md-6 col-lg-4">
          <MeetingCard 
            :meeting="meeting"
            :showAdminControls="true"
          />
        </div>
      </div>
    </div>

    <!-- 已取消的聚會 -->
    <div class="mb-5">
      <h3 class="mb-3">已取消的聚會</h3>
      <div class="row g-4">
        <div v-if="meetings.cancelled.length === 0" class="col-12 text-center">
          <p class="text-muted">沒有已取消的聚會</p>
        </div>
        <div v-for="meeting in meetings.cancelled" :key="meeting.meeting_id" class="col-md-6 col-lg-4">
          <MeetingCard 
            :meeting="meeting"
            :showAdminControls="true"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import MeetingCard from '@/components/MeetingCard.vue'
import { apiGet, apiPost } from '@/utils/api'

export default {
  name: 'AdminMeetingsView',
  components: {
    MeetingCard
  },
  data() {
    return {
      meetings: {
        ongoing: [],
        finished: [],
        cancelled: []
      }
    }
  },
  methods: {
    async fetchAllMeetings() {
      try {
        const data = await apiGet('admin/meetings')
        if (data.status === 'success') {
          // 根據狀態分類聚會
          console.log(data);
          const meetings = {
            ongoing: [],
            finished: [],
            cancelled: []
          }
          
          data.meetings.forEach(meeting => {
            if (meeting.status === 'Ongoing') {
              meetings.ongoing.push(meeting)
            } else if (meeting.status === 'Finished') {
              meetings.finished.push(meeting)
            } else if (meeting.status === 'Canceled') {
              meetings.cancelled.push(meeting)
            }
          })
          
          this.meetings = meetings
        } else {
          alert(data.message || '獲取聚會列表失敗')
        }
      } catch (error) {
        console.error('Error fetching meetings:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        } else {
          alert('獲取聚會列表失敗')
        }
      }
    },
    async cancelMeeting(meetingId) {
      if (!confirm('確定要取消這個聚會嗎？')) return
      
      try {
        const data = await apiPost('admin/cancel-meeting', {
          meeting_id: meetingId
        })
        
        if (data.status === 'success') {
          this.fetchAllMeetings()
        } else {
          alert(data.message || '取消聚會失敗')
        }
      } catch (error) {
        console.error('Error canceling meeting:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        } else {
          alert('取消聚會失敗')
        }
      }
    },
    async finishMeeting(meetingId) {
      if (!confirm('確定要結束這個聚會嗎？')) return
      
      try {
        const data = await apiPost('admin/finish-meeting', {
          meeting_id: meetingId
        })
        
        if (data.status === 'success') {
          this.fetchAllMeetings()
        } else {
          alert(data.message || '結束聚會失敗')
        }
      } catch (error) {
        console.error('Error finishing meeting:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        } else {
          alert('結束聚會失敗')
        }
      }
    },
    async removeUserFromMeeting(meetingId, userId) {
      if (!confirm('確定要將此用戶從聚會中移除嗎？')) return
      
      try {
        const data = await apiPost('admin/remove-user-from-meeting', {
          meeting_id: meetingId,
          user_id: userId
        })
        
        if (data.status === 'success') {
          this.fetchAllMeetings()
        } else {
          alert(data.message || '移除用戶失敗')
        }
      } catch (error) {
        console.error('Error removing user:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        } else {
          alert('移除用戶失敗')
        }
      }
    }
  },
  created() {
    this.fetchAllMeetings()
  }
}
</script>

<style scoped>
.admin-meeting-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
</style>
