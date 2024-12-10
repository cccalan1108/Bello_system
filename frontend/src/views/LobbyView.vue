<template>
    <div class="lobby-container">
      <div class="row g-4">
        <div v-for="(option, index) in options" :key="index" class="col-md-6">
          <router-link :to="option.path" class="card-link">
            <div class="card h-100 lobby-card">
              <div class="card-body">
                <h5 class="card-title mb-2">{{ option.title }}</h5>
                <p class="card-text text-muted">{{ option.description }}</p>
                <i class="bi bi-arrow-right card-arrow"></i>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'LobbyView',
    data() {
      return {
        options: [
          {
            title: '新增聚會',
            description: '建立新的聚會',
            path: '/create-meeting'
          },
          {
            title: '所有聚會',
            description: '瀏覽所有可參加的聚會',
            path: '/meetings'
          },
          {
            title: '我的聚會',
            description: '查看我參加和舉辦的聚會',
            path: '/my-meetings'
          },
          {
            title: '私人聊天',
            description: '與其他用戶進行私人對話',
            path: '/chat'
          },
          {
            title: '聚會聊天',
            description: '與聚會成員進行群組對話',
            path: '/meeting-chat'
          },
          {
            title: '個人資料',
            description: '編輯個人資料',
            path: '/profile'
          }
        ]
      }
    }
  }
  </script>
  
  <style scoped>
  .lobby-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .card-link {
    text-decoration: none;
    color: inherit;
  }
  
  .lobby-card {
    transition: all 0.3s ease;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    position: relative;
    overflow: hidden;
  }
  
  .lobby-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border-color: #cbd5e0;
  }
  
  .card-title {
    font-size: 1.25rem;
    color: #2d3748;
  }
  
  .card-text {
    font-size: 0.9rem;
    color: #718096;
  }
  
  .card-arrow {
    position: absolute;
    right: 20px;
    bottom: 20px;
    font-size: 1.5rem;
    color: #a0aec0;
    transition: transform 0.3s ease;
  }
  
  .lobby-card:hover .card-arrow {
    transform: translateX(5px);
    color: #4a5568;
  }
  </style>