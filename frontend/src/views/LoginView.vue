<template>
  <div class="login-form">
    <h2 class="mb-4">登入</h2>
    <form @submit.prevent="handleLogin">
      <div class="mb-3">
        <label class="form-label">帳號:</label>
        <input type="text" class="form-control custom-input" v-model="account">
      </div>
      
      <div class="mb-3">
        <label class="form-label">密碼:</label>
        <input type="password" class="form-control custom-input" v-model="password">
      </div>
      
      <div class="text-center">
        <button type="submit" class="btn btn-primary">登入</button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  name: 'LoginView',
  data() {
    return {
      account: '',
      password: ''
    }
  },
  created() {
    // 如果用戶已登入，直接導向到 lobby
    if (localStorage.getItem('user')) {
      this.$router.push('/lobby')
    }
  },
  methods: {
    async handleLogin() {
      try {
        const response = await fetch('http://localhost:8800/api/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({ 
            account: this.account, 
            password: this.password 
          }),
        })
        
        const data = await response.json()
        if (data.status === 'success') {
          localStorage.setItem('user', JSON.stringify(data.user))
          this.$router.push(data.user.role === 'Admin' ? '/admin-lobby' : '/lobby')
        } else {
          alert('帳號或密碼錯誤')
        }
      } catch (error) {
        alert('帳號或密碼錯誤')
      }
    }
  }
}
</script>

<style scoped>
.login-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}
</style>
