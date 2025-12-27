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
            @show-map="handleShowMap"
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
            @show-map="handleShowMap"
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
            @show-map="handleShowMap"
          />
        </div>
      </div>
    </div>

    <!-- 地圖彈窗 -->
    <MapModal
      :show="showMapModal"
      :place-name="mapData.place"
      :address="mapData.address"
      :latitude="mapData.latitude"
      :longitude="mapData.longitude"
      @close="closeMapModal"
    />
  </div>
</template>

<script>
import UserMeetingCard from '@/components/UserMeetingCard.vue'
import MapModal from '@/components/MapModal.vue'
import { getUser, apiGet, apiPost } from '@/utils/api'

export default {
  name: 'MyMeetingsView',
  components: {
    UserMeetingCard,
    MapModal
  },
  data() {
    return {
      meetings: {
        ongoing: [],
        finished: [],
        cancelled: []
      },
      currentUserId: null,
      showMapModal: false,
      mapData: {
        place: '',
        address: '',
        latitude: null,
        longitude: null
      }
    }
  },
  created() {
    const user = getUser()
    if (user) {
      this.currentUserId = user.user_id
    } else {
      this.$router.push('/login')
      return
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
        address: meeting.address,
        latitude: meeting.latitude,
        longitude: meeting.longitude,
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
    handleShowMap(data) {
      this.mapData = {
        place: data.place || '',
        address: data.address || '',
        latitude: data.latitude,
        longitude: data.longitude
      }
      this.showMapModal = true
    },
    closeMapModal() {
      this.showMapModal = false
    },
    async fetchMeetings() {
      try {
        const user = getUser()
        if (!user || !user.user_id) {
          this.$router.push('/login')
          return
        }
        // 使用 apiGet 自動添加 token
        const data = await apiGet(`my-meetings/${user.user_id}`)
        if (data.status === 'success') {
          console.log('My meetings:', data.meetings)
          this.meetings = {
            ongoing: data.meetings.ongoing || [],
            finished: data.meetings.finished || [],
            cancelled: data.meetings.cancelled || []
          }
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
    async leaveMeeting(meetingId) {
      if (!confirm('確定要退出這個聚會嗎？')) {
        return
      }
      
      try {
        // 使用 apiPost 自動添加 token，不需要傳 user_id（後端會從 token 獲取）
        const data = await apiPost('leave-meeting', {
          meeting_id: meetingId
        })
        
        if (data.status === 'success') {
          alert('已退出聚會')
          this.fetchMeetings()
        } else {
          alert(data.message || '退出聚會失敗')
        }
      } catch (error) {
        console.error('Error leaving meeting:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        } else {
          alert('退出聚會失敗，請稍後再試')
        }
      }
    },
    async cancelMeeting(meetingId) {
      if (!confirm('確定要取消這個聚會嗎？')) return;
      
      try {
        // 使用 apiPost 自動添加 token
        const data = await apiPost('cancel-meeting', {
          meeting_id: meetingId
        });
        
        if (data.status === 'success') {
          alert('聚會已取消');
          this.fetchMeetings();
        } else {
          alert(data.message || '取消聚會失敗');
        }
      } catch (error) {
        console.error('Error canceling meeting:', error);
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login');
        } else {
          alert('取消聚會失敗');
        }
      }
    },
    
    async finishMeeting(meetingId) {
      if (!confirm('確定要結束這個聚會嗎？')) return;
      
      try {
        // 使用 apiPost 自動添加 token
        const data = await apiPost('finish-meeting', {
          meeting_id: meetingId
        });
        
        if (data.status === 'success') {
          alert('聚會已結束');
          this.fetchMeetings();
        } else {
          alert(data.message || '結束聚會失敗');
        }
      } catch (error) {
        console.error('Error finishing meeting:', error);
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login');
        } else {
          alert('結束聚會失敗');
        }
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
