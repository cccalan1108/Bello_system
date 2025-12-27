<template>
    <div class="admin-lobby">
      <h1>管理員控制台</h1>
      
      <div class="admin-functions">
        <div class="function-group">
          <h2>聚會管理</h2>
          <button @click="navigateTo('admin-meetings')" class="admin-btn">
            瀏覽所有聚會
          </button>
        </div>
  
        <div class="function-group">
          <h2>用戶管理</h2>
          <button @click="navigateTo('admin-users')" class="admin-btn">
            瀏覽所有用戶
          </button>
        </div>
  
        <div class="function-group">
          <h2>聊天記錄</h2>
          <button @click="navigateTo('admin-user-chat-records')" class="admin-btn">
            查看用戶聊天記錄
          </button>
          <button @click="navigateTo('admin-meeting-chat-records')" class="admin-btn">
            查看聚會聊天記錄
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { getUser } from '@/utils/api'
  
  export default {
    name: 'AdminLobby',
    methods: {
      navigateTo(route) {
        console.log('Navigating to route:', route)
        const routeMap = {
          'admin-meetings': '/admin-meetings',
          'admin-users': '/admin-users',
          'admin-user-chat-records': '/admin/user-chat-records',
          'admin-meeting-chat-records': '/admin/meeting-chat-records'
        }
        console.log('Mapped path:', routeMap[route])
        this.$router.push(routeMap[route])
          .then(() => {
            console.log('Navigation successful')
          })
          .catch(err => {
            console.error('Navigation failed:', err)
          })
      }
    },
    created() {
      // 檢查用戶是否為管理員
      const user = getUser()
      if (!user || user.role !== 'Admin') {
        this.$router.push('/login')
      }
    }
  }
  </script>
  
  <style scoped>
  .admin-lobby {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .admin-functions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
  }
  
  .function-group {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  
  .function-group h2 {
    color: #343a40;
    margin-bottom: 15px;
    font-size: 1.5rem;
  }
  
  .admin-btn {
    display: block;
    width: 100%;
    padding: 12px;
    margin-bottom: 10px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.3s;
  }
  
  .admin-btn:hover {
    background-color: #0056b3;
  }
  </style>