<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <h1 class="error-code">404</h1>
      <h2 class="error-title">頁面不存在</h2>
      <p class="error-message">抱歉，您訪問的頁面不存在或已被移除。</p>
      <div class="error-actions">
        <router-link to="/" class="btn btn-primary">回到首頁</router-link>
        <button @click="$router.go(-1)" class="btn btn-outline-secondary">返回上一頁</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFoundView'
}
</script>

<style scoped>
.not-found-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 200px);
  padding: 20px;
}

.not-found-content {
  text-align: center;
  max-width: 500px;
}

.error-code {
  font-size: 8rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
  line-height: 1;
}

.error-title {
  font-size: 2rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
}

.error-message {
  font-size: 1.1rem;
  color: #718096;
  margin-bottom: 2rem;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}
</style>

