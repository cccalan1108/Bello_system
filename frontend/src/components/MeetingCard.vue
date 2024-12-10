<template>
  <div class="card h-100">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-start mb-2">
        <h5 class="card-title mb-0">{{ meeting.content }}</h5>
        <span class="badge bg-primary">舉辦者：{{ meeting.holder_name }}</span>
      </div>
      
      <p class="card-text">
        <small>
          日期：{{ formatDate(meeting.event_date) }}<br>
          地點：{{ meeting.event_place }}<br>
          人數：{{ meeting.num_participant }}/{{ meeting.max_participant }}<br>
          狀態：{{ getStatusText(meeting.status) }}
        </small>
      </p>
      
      <!-- 管理員控制項 -->
      <div v-if="showAdminControls && meeting.status === 'Ongoing'" class="admin-controls">
        <button @click="$emit('finish', meeting.meeting_id)" 
                class="btn btn-warning btn-sm me-2">
          結束聚會
        </button>
        <button @click="$emit('cancel', meeting.meeting_id)" 
                class="btn btn-danger btn-sm me-2">
          取消聚會
        </button>
      </div>

      <!-- 參與者列表 -->
      <div v-if="showAdminControls" class="participants-list mt-3">
        <h6>參與者列表：</h6>
        <ul class="list-unstyled">
          <li v-for="participant in meeting.participants" :key="participant.user_id" 
              class="d-flex justify-content-between align-items-center mb-1">
            <span>
              {{ participant.user_name }}
              <span v-if="participant.user_id === meeting.holder_id" 
                    class="badge bg-primary ms-1">
                舉辦者
              </span>
            </span>
            <button v-if="meeting.status === 'Ongoing' && participant.user_id !== meeting.holder_id"
                    @click="$emit('remove-user', meeting.meeting_id, participant.user_id)" 
                    class="btn btn-danger btn-sm">
              移除
            </button>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    meeting: {
      type: Object,
      required: true
    },
    showAdminControls: {
      type: Boolean,
      default: false
    },
    canManage: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    formatDate(date) {
      return new Date(date).toLocaleDateString('zh-TW')
    },
    getStatusText(status) {
      const statusMap = {
        'Ongoing': '進行中',
        'Finished': '已結束',
        'Cancelled': '已取消'
      }
      return statusMap[status] || status
    }
  }
}
</script>

<style scoped>
.participants-list li {
  padding: 0.25rem 0;
}
</style>
