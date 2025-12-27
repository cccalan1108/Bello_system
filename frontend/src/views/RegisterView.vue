<template>
  <div class="register-form">
    <h2 class="mb-4 text-center">註冊</h2>
    <form @submit.prevent="handleRegister">
      <div class="row">
        <!-- 左列 -->
        <div class="col-md-6">
          <div class="mb-3">
            <label class="form-label required">帳號:</label>
            <input type="text" class="form-control custom-input" v-model="formData.account" required>
          </div>
          
          <div class="mb-3">
            <label class="form-label required">密碼:</label>
            <input type="password" class="form-control custom-input" v-model="formData.password" required>
          </div>
          
          <div class="mb-3">
            <label class="form-label required">姓名:</label>
            <input type="text" class="form-control custom-input" v-model="formData.user_name" required>
          </div>
          
          <div class="mb-3">
            <label class="form-label required">暱稱:</label>
            <input type="text" class="form-control custom-input" v-model="formData.user_nickname" required>
          </div>

          <div class="mb-3">
            <label class="form-label required">國籍:</label>
            <input type="text" class="form-control custom-input" v-model="formData.nationality" required>
          </div>
        </div>

        <!-- 右列 -->
        <div class="col-md-6">
          <div class="mb-3">
            <label class="form-label required">城市:</label>
            <input type="text" class="form-control custom-input" v-model="formData.city" required>
          </div>

          <div class="mb-3">
            <label class="form-label required">電話:</label>
            <input type="tel" class="form-control custom-input" v-model="formData.phone" required>
          </div>

          <div class="mb-3">
            <label class="form-label required">Email:</label>
            <input type="email" class="form-control custom-input" v-model="formData.email" required>
          </div>

          <div class="mb-3">
            <label class="form-label required">性別:</label>
            <select class="form-select custom-input" v-model="formData.sex" required>
              <option value="">請選擇</option>
              <option value="男">男</option>
              <option value="女">女</option>
            </select>
          </div>

          <div class="mb-3">
            <label class="form-label required">生日:</label>
            <input type="date" class="form-control custom-input" v-model="formData.birthday" required>
          </div>
        </div>
      </div>
      <div class="mb-3">
        <label class="form-label">管理者驗證碼 (選填):</label>
        <input 
        type="password" 
        class="form-control custom-input" 
        v-model="formData.admin_auth_code"
        placeholder="如果要註冊為管理者，請輸入驗證碼"
        >
      </div>
      <div class="text-center mt-4">
        <button type="submit" class="btn btn-primary btn-lg">註冊</button>
      </div>
    </form>
  </div>
</template>

<script>
import { apiUrl } from '@/config/api'
export default {
  name: 'RegisterView',
  data() {
    return {
      formData: {
        account: '',
        password: '',
        user_name: '',
        user_nickname: '',
        nationality: '',
        city: '',
        phone: '',
        email: '',
        sex: '',
        birthday: '',
        admin_auth_code: ''
      }
    }
  },
  methods: {
    async handleRegister() {
      try {
        // 基本驗證
        if (!this.formData.birthday) {
          alert('請選擇生日日期')
          return
        }

        // 轉換日期格式為 YYYY-MM-DD
        const formattedData = {
          ...this.formData,
          birthday: new Date(this.formData.birthday).toISOString().split('T')[0]
        }

        const response = await fetch(apiUrl('signup'), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formattedData),
        })
        
        // 檢查響應狀態
        if (!response.ok) {
          // 如果不是 JSON 響應，嘗試獲取文本
          const text = await response.text()
          let errorMessage = '註冊失敗，請稍後再試'
          
          try {
            // 嘗試解析為 JSON
            const errorData = JSON.parse(text)
            errorMessage = errorData.message || errorMessage
          } catch (e) {
            // 如果不是 JSON，使用狀態碼信息
            if (response.status === 404) {
              errorMessage = '無法連接到伺服器，請確認後端服務是否運行'
            } else if (response.status === 500) {
              errorMessage = '伺服器錯誤，請稍後再試'
            }
          }
          
          alert(errorMessage)
          return
        }
        
        const data = await response.json()
        if (data.status === 'success') {
          alert('註冊成功！')
          this.$router.push('/login')
        } else {
          alert(data.message || '註冊失敗')
        }
      } catch (error) {
        console.error('註冊錯誤:', error)
        if (error instanceof SyntaxError) {
          alert('無法解析伺服器響應，請確認後端服務是否正常運行')
        } else {
          alert('註冊失敗，請稍後再試')
        }
      }
    }
  }
}
</script>

<style scoped>
.register-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.required:after {
  content: " *";
  color: red;
}

.custom-input {
  background-color: #f8f9fa;
  border: 2px solid #dee2e6;
  padding: 0.5rem;
}

.custom-input:focus {
  background-color: #fff;
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}

.btn-primary {
  padding: 0.5rem 2rem;
}
</style>
