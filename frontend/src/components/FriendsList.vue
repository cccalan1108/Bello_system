<template>
  <div class="friends-list">
    <div class="friends-header">
      <h5>好友列表</h5>
      <span class="badge bg-primary">{{ friends.length }}</span>
    </div>
    
    <div v-if="loading" class="text-center py-3">
      <div class="spinner-border spinner-border-sm" role="status">
        <span class="visually-hidden">載入中...</span>
      </div>
    </div>
    
    <div v-else-if="friends.length === 0" class="no-friends">
      <p class="text-muted">還沒有好友</p>
      <button class="btn btn-outline-primary btn-sm" @click="$emit('show-add-friend')">
        添加好友
      </button>
    </div>
    
    <div v-else class="friends-items">
      <div 
        v-for="friend in friends" 
        :key="friend.user_id"
        class="friend-item"
        @click="$emit('start-chat', friend)"
      >
        <div class="friend-avatar">
          <img 
            v-if="friend.avatar_url" 
            :src="friend.avatar_url" 
            class="avatar-img"
            alt="avatar"
          />
          <div v-else class="avatar-circle">
            {{ friend.user_name?.charAt(0) }}
          </div>
          <span 
            class="online-indicator" 
            :class="{ 'online': friend.is_online }"
          ></span>
        </div>
        <div class="friend-info">
          <div class="friend-name">{{ friend.user_name }}</div>
          <small class="friend-status" :class="{ 'text-success': friend.is_online }">
            {{ friend.is_online ? '在線' : '離線' }}
          </small>
        </div>
        <div class="friend-actions">
          <button 
            class="btn btn-sm btn-outline-primary"
            @click.stop="$emit('start-chat', friend)"
            title="開始聊天"
          >
            <i class="bi bi-chat-dots"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FriendsList',
  props: {
    friends: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['start-chat', 'show-add-friend']
}
</script>

<style scoped>
.friends-list {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden;
}

.friends-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.friends-header h5 {
  margin: 0;
  font-weight: 600;
}

.no-friends {
  padding: 30px;
  text-align: center;
}

.friends-items {
  max-height: 400px;
  overflow-y: auto;
}

.friend-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f0f0f0;
}

.friend-item:hover {
  background-color: #f8f9fa;
}

.friend-item:last-child {
  border-bottom: none;
}

.friend-avatar {
  position: relative;
  margin-right: 12px;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
}

.avatar-img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.online-indicator {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ccc;
  border: 2px solid #fff;
}

.online-indicator.online {
  background: #28a745;
}

.friend-info {
  flex: 1;
}

.friend-name {
  font-weight: 500;
  color: #333;
}

.friend-status {
  color: #999;
  font-size: 12px;
}

.friend-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.friend-item:hover .friend-actions {
  opacity: 1;
}

.btn-outline-primary {
  border-color: #667eea;
  color: #667eea;
}

.btn-outline-primary:hover {
  background-color: #667eea;
  color: white;
}
</style>

