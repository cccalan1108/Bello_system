<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <div class="container">
        <router-link class="navbar-brand" :to="homeRoute">Bello</router-link>
        <div class="d-flex" v-if="!isAuthPage">
          <template v-if="!isLoggedIn">
            <router-link to="/register" class="btn btn-outline-primary">註冊新帳號</router-link>
          </template>
          <template v-else>
            <router-link :to="homeRoute" class="btn btn-secondary me-2">回到主頁</router-link>
            <button @click="handleLogout" class="btn btn-danger">登出</button>
          </template>
        </div>
      </div>
    </nav>
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      isLoggedIn: false,
      userRole: null
    }
  },
  computed: {
    homeRoute() {
      return this.userRole === 'Admin' ? '/admin-lobby' : '/lobby'
    }
  },
  created() {
    this.checkLoginStatus()
  },
  methods: {
    checkLoginStatus() {
      const user = localStorage.getItem('user')
      if (user) {
        this.isLoggedIn = true
        this.userRole = JSON.parse(user).role
      } else {
        this.isLoggedIn = false
        this.userRole = null
      }
    },
    handleLogout() {
      localStorage.removeItem('user')
      this.isLoggedIn = false
      this.userRole = null
      this.$router.push('/login')
    }
  },
  watch: {
    $route() {
      this.checkLoginStatus()
    }
  }
}
</script>

<style>
#app {
  font-family: 'Microsoft JhengHei', Arial, sans-serif;
}

.navbar {
  margin-bottom: 2rem;
}
</style>