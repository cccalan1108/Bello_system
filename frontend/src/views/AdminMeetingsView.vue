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
        const response = await fetch('http://localhost:8800/api/admin/meetings')
        const data = await response.json()
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
          alert(data.message)
        }
      } catch (error) {
        console.error('Error fetching meetings:', error)
        alert('獲取聚會列表失敗')
      }
    },
    async cancelMeeting(meetingId) {
      if (!confirm('確定要取消這個聚會嗎？')) return
      
      try {
        const response = await fetch('http://localhost:8800/api/admin/cancel-meeting', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ meeting_id: meetingId })
        })
        
        const data = await response.json()
        if (data.status === 'success') {
          this.fetchAllMeetings()
        } else {
          alert(data.message)
        }
      } catch (error) {
        console.error('Error canceling meeting:', error)
        alert('取消聚會失敗')
      }
    },
    async finishMeeting(meetingId) {
      if (!confirm('確定要結束這個聚會嗎？')) return
      
      try {
        const response = await fetch('http://localhost:8800/api/admin/finish-meeting', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ meeting_id: meetingId })
        })
        
        const data = await response.json()
        if (data.status === 'success') {
          this.fetchAllMeetings()
        } else {
          alert(data.message)
        }
      } catch (error) {
        console.error('Error finishing meeting:', error)
        alert('結束聚會失敗')
      }
    },
    async removeUserFromMeeting(meetingId, userId) {
      if (!confirm('確定要將此用戶從聚會中移除嗎？')) return
      
      try {
        const response = await fetch('http://localhost:8800/api/admin/remove-user-from-meeting', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            meeting_id: meetingId,
            user_id: userId 
          })
        })
        
        const data = await response.json()
        if (data.status === 'success') {
          this.fetchAllMeetings()
        } else {
          alert(data.message)
        }
      } catch (error) {
        console.error('Error removing user:', error)
        alert('移除用戶失敗')
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
