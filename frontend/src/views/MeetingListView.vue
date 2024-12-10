<template>
  <div class="meeting-list">
    <h2 class="mb-4">可參加的聚會</h2>
    <div class="row g-4">
      <div v-if="meetings.length === 0" class="col-12 text-center">
        <p class="text-muted">目前沒有可參加的聚會</p>
      </div>
      <div v-for="meeting in meetings" :key="meeting.meeting_id" class="col-md-6 col-lg-4">
        <UserMeetingCard 
          :meeting="meeting"
          :isJoinable="true"
          @join-meeting="handleJoinMeeting"
        />
      </div>
    </div>
  </div>
</template>

<script>
import UserMeetingCard from '@/components/UserMeetingCard.vue'

export default {
  name: 'MeetingListView',
  components: {
    UserMeetingCard
  },
  data() {
    return {
      meetings: []
    }
  },
  methods: {
    formatMeetingData(meeting) {
      console.log('Original meeting data:', meeting);
      const formattedData = {
        date: meeting.date,
        start_time: meeting.start_time,
        end_time: meeting.end_time,
        place: meeting.place,
        city: meeting.city,
        num_participant: meeting.current_members,
        max_participants: meeting.max_members,
        status: meeting.status,
        meeting_id: meeting.id,
        holder_id: meeting.holder_id,
        holder_name: meeting.holder_name
      };
      console.log('Formatted meeting data:', formattedData);
      return formattedData;
    },
    async fetchMeetings() {
      try {
        const user = JSON.parse(localStorage.getItem('user'))
        if (!user || !user.user_id) {
          this.$router.push('/login')
          return
        }
        
        const response = await fetch(`http://localhost:8800/api/list-meeting?user_id=${user.user_id}`)
        const text = await response.text()
        
        try {
          const data = JSON.parse(text)
          if (data.status === 'success') {
            this.meetings = data.meetings.map(meeting => this.formatMeetingData(meeting))
          } else {
            alert(data.message)
          }
        } catch (parseError) {
          console.error('JSON parsing error:', parseError)
          alert('數據格式錯誤')
        }
      } catch (error) {
        console.error('Error fetching meetings:', error)
        alert('獲取聚會列表失敗')
      }
    },
    async handleJoinMeeting(meetingId) {
      console.log('Handling join meeting for ID:', meetingId);
      if (!meetingId) {
        console.error('聚會ID不存在');
        alert('無效的聚會ID');
        return;
      }
      
      try {
        const user = JSON.parse(localStorage.getItem('user'))
        console.log('Current user:', user);
        if (!user || !user.user_id) {
          alert('請先登入')
          this.$router.push('/login')
          return
        }

        const response = await fetch('http://localhost:8800/api/join-meeting', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            meeting_id: meetingId,
            user_id: user.user_id
          })
        })

        const data = await response.json()
        if (data.status === 'success') {
          alert('成功加入聚會！')
          this.fetchMeetings()
        } else {
          alert(data.message || '加入聚會失敗')
        }
      } catch (error) {
        console.error('Error joining meeting:', error)
        alert('加入聚會失敗，請稍後再試')
      }
    }
  },
  created() {
    this.fetchMeetings()
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
