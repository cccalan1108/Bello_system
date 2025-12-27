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
          @show-map="handleShowMap"
        />
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

    <!-- 密碼輸入 Modal -->
    <div v-if="showPasswordModal" class="modal-overlay" @click.self="closePasswordModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">🔒 請輸入聚會密碼</h5>
            <button type="button" class="btn-close" @click="closePasswordModal"></button>
          </div>
          <div class="modal-body">
            <input 
              type="password" 
              class="form-control"
              v-model="joinPassword"
              placeholder="輸入密碼"
              @keyup.enter="confirmJoinWithPassword"
            >
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closePasswordModal">取消</button>
            <button type="button" class="btn btn-primary" @click="confirmJoinWithPassword">確認加入</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import UserMeetingCard from '@/components/UserMeetingCard.vue'
import MapModal from '@/components/MapModal.vue'
import { getUser, apiGet, apiPost } from '@/utils/api'

export default {
  name: 'MeetingListView',
  components: {
    UserMeetingCard,
    MapModal
  },
  data() {
    return {
      meetings: [],
      showPasswordModal: false,
      joinPassword: '',
      pendingMeetingId: null,
      showMapModal: false,
      mapData: {
        place: '',
        address: '',
        latitude: null,
        longitude: null
      }
    }
  },
  methods: {
    formatMeetingData(meeting) {
      console.log('Original meeting data:', meeting);
      const formattedData = {
        content: meeting.type,
        date: meeting.date,
        start_time: meeting.start_time,
        end_time: meeting.end_time,
        place: meeting.place,
        city: meeting.city,
        address: meeting.address,
        latitude: meeting.latitude,
        longitude: meeting.longitude,
        num_participant: meeting.current_members,
        max_participants: meeting.max_members,
        status: meeting.status,
        meeting_id: meeting.id,
        holder_id: meeting.holder_id,
        holder_name: meeting.holder_name,
        has_password: meeting.has_password
      };
      console.log('Formatted meeting data:', formattedData);
      return formattedData;
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
        
        // 使用 apiGet 自動添加 token，後端會從 token 獲取 user_id
        const data = await apiGet('list-meeting')
        if (data.status === 'success') {
          this.meetings = data.meetings.map(meeting => this.formatMeetingData(meeting))
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
    handleJoinMeeting(meetingId) {
      console.log('Handling join meeting for ID:', meetingId);
      if (!meetingId) {
        console.error('聚會ID不存在');
        alert('無效的聚會ID');
        return;
      }
      
      // 檢查此聚會是否需要密碼
      const meeting = this.meetings.find(m => m.meeting_id === meetingId)
      if (meeting && meeting.has_password) {
        // 需要密碼，顯示密碼輸入彈窗
        this.pendingMeetingId = meetingId
        this.joinPassword = ''
        this.showPasswordModal = true
      } else {
        // 不需要密碼，直接加入
        this.joinMeeting(meetingId, null)
      }
    },
    closePasswordModal() {
      this.showPasswordModal = false
      this.joinPassword = ''
      this.pendingMeetingId = null
    },
    confirmJoinWithPassword() {
      if (!this.joinPassword) {
        alert('請輸入密碼')
        return
      }
      this.joinMeeting(this.pendingMeetingId, this.joinPassword)
    },
    async joinMeeting(meetingId, password) {
      try {
        // 使用 apiPost 自動添加 token，不需要傳 user_id（後端會從 token 獲取）
        const data = await apiPost('join-meeting', {
          meeting_id: meetingId,
          password: password
        })

        if (data.status === 'success') {
          this.closePasswordModal()
          alert('成功加入聚會！')
          this.fetchMeetings()
        } else {
          alert(data.message || '加入聚會失敗')
        }
      } catch (error) {
        console.error('Error joining meeting:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        } else if (error.message && error.message.includes('密碼')) {
          alert('密碼錯誤，請重新輸入')
        } else {
          alert(error.message || '加入聚會失敗，請稍後再試')
        }
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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}

.modal-dialog {
  max-width: 400px;
  width: 90%;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  margin: 0;
  font-size: 1.1rem;
}

.modal-body {
  padding: 1rem;
}

.modal-footer {
  padding: 1rem;
  border-top: 1px solid #dee2e6;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
</style>
