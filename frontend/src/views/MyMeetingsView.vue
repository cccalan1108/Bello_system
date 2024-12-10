<template>
  <div class="meeting-list">
    <h2 class="mb-4">我參加的聚會</h2>
    
    <!-- 進行中的聚會 -->
    <div class="mb-5">
      <h3 class="mb-3">進行中的聚會</h3>
      <div class="row g-4">
        <div v-if="!meetings.ongoing?.length" class="col-12 text-center">
          <p class="text-muted">目前沒有進行中的聚會</p>
        </div>
        <div v-for="meeting in meetings.ongoing" :key="meeting.meeting_id" class="col-md-6 col-lg-4">
          <UserMeetingCard 
            :meeting="formatMeetingData(meeting)"
            :isJoinable="false"
            :showLeaveButton="true"
            :showManageButtons="meeting.holder_id === currentUserId"
            :showStatus="false"
            :currentUserId="currentUserId"
            @leave="leaveMeeting"
            @finish="finishMeeting"
            @cancel="cancelMeeting"
          />
        </div>
      </div>
    </div>

    <!-- 已結束的聚會 -->
    <div class="mb-5">
      <h3 class="mb-3">已結束的聚會</h3>
      <div class="row g-4">
        <div v-if="!meetings.finished?.length" class="col-12 text-center">
          <p class="text-muted">沒有已結束的聚會</p>
        </div>
        <div v-for="meeting in meetings.finished" :key="meeting.meeting_id" class="col-md-6 col-lg-4">
          <UserMeetingCard 
            :meeting="formatMeetingData(meeting)"
            :isJoinable="false"
            :showStatus="false"
            :showLeaveButton="false"
          />
        </div>
      </div>
    </div>

    <!-- 已取消的聚會 -->
    <div class="mb-5">
      <h3 class="mb-3">已取消的聚會</h3>
      <div class="row g-4">
        <div v-if="!meetings.cancelled?.length" class="col-12 text-center">
          <p class="text-muted">沒有已取消的聚會</p>
        </div>
        <div v-for="meeting in meetings.cancelled" :key="meeting.meeting_id" class="col-md-6 col-lg-4">
          <UserMeetingCard 
            :meeting="formatMeetingData(meeting)"
            :isJoinable="false"
            :showStatus="false"
            :showLeaveButton="false"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import UserMeetingCard from '@/components/UserMeetingCard.vue'

export default {
  name: 'MyMeetingsView',
  components: {
    UserMeetingCard
  },
  data() {
    return {
      meetings: {
        ongoing: [],
        finished: [],
        cancelled: []
      },
      currentUserId: null
    }
  },
  created() {
    const user = JSON.parse(localStorage.getItem('user'))
    if (user) {
      this.currentUserId = user.user_id
    }
    this.fetchMeetings()
  },
  methods: {
    formatMeetingData(meeting) {
      return {
        title: meeting.content,
        content: meeting.content,
        date: meeting.date,
        start_time: meeting.start_time,
        end_time: meeting.end_time,
        place: meeting.place || meeting.city,
        current_members: meeting.num_participant,
        max_members: meeting.max_participants,
        type: meeting.type || '未指定',
        status: meeting.status,
        meeting_id: meeting.meeting_id,
        holder_id: meeting.holder_id,
        holder_name: meeting.holder_name,
        num_participant: meeting.num_participant,
        max_participant: meeting.max_participants
      }
    },
    async fetchMeetings() {
      try {
        const user = JSON.parse(localStorage.getItem('user'))
        if (!user || !user.user_id) {
          this.$router.push('/login')
          return
        }
        const response = await fetch(`http://localhost:8800/api/my-meetings/${user.user_id}`)
        const data = await response.json()
        if (data.status === 'success') {
          console.log('My meetings:', data.meetings)
          this.meetings = {
            ongoing: data.meetings.ongoing || [],
            finished: data.meetings.finished || [],
            cancelled: data.meetings.cancelled || []
          }
        } else {
          alert(data.message)
        }
      } catch (error) {
        console.error('Error fetching meetings:', error)
        alert('獲取聚會列表失敗')
      }
    },
    async leaveMeeting(meetingId) {
      if (!confirm('確定要退出這個聚會嗎？')) {
        return
      }
      
      try {
        const user = JSON.parse(localStorage.getItem('user'))
        const response = await fetch('http://localhost:8800/api/leave-meeting', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            meeting_id: meetingId,
            user_id: user.user_id
          })
        })
        
        const data = await response.json()
        if (data.status === 'success') {
          alert('已退出聚會')
          this.fetchMeetings()
        } else {
          alert(data.message)
        }
      } catch (error) {
        console.error('Error leaving meeting:', error)
        alert('退出聚會失敗，請稍後再試')
      }
    },
    async cancelMeeting(meetingId) {
      if (!confirm('確定要取消這個聚會嗎？')) return;
      
      try {
        const response = await fetch('http://localhost:8800/api/cancel-meeting', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ meeting_id: meetingId })
        });
        
        const data = await response.json();
        if (data.status === 'success') {
          alert('聚會已取消');
          this.fetchMeetings();
        } else {
          alert(data.message);
        }
      } catch (error) {
        console.error('Error canceling meeting:', error);
        alert('取消聚會失敗');
      }
    },
    
    async finishMeeting(meetingId) {
      if (!confirm('確定要結束這個聚會嗎？')) return;
      
      try {
        const response = await fetch('http://localhost:8800/api/finish-meeting', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ meeting_id: meetingId })
        });
        
        const data = await response.json();
        if (data.status === 'success') {
          alert('聚會已結束');
          this.fetchMeetings();
        } else {
          alert(data.message);
        }
      } catch (error) {
        console.error('Error finishing meeting:', error);
        alert('結束聚會失敗');
      }
    }
  }
}
</script>

<style scoped>
.meeting-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
</style>
