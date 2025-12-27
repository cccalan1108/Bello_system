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
    
    <!-- 分隔線 -->
    <div class="divider my-4">
      <span>或</span>
    </div>
    
    <!-- Google 登入按鈕 -->
    <div class="text-center">
      <!-- LINE 內嵌瀏覽器提示 -->
      <div v-if="isLineBrowser || showLineWarning" class="line-browser-warning alert alert-warning">
        <p class="mb-2"><strong>⚠️ 檢測到內嵌瀏覽器</strong></p>
        <p class="mb-2 small">Google 登入在內嵌瀏覽器（如 LINE、Facebook）中無法使用。請使用以下方式：</p>
        <button 
          class="btn btn-sm btn-primary" 
          @click="showUrlModal = true"
        >
          在外部瀏覽器開啟
        </button>
        <button 
          v-if="!isLineBrowser"
          class="btn btn-sm btn-outline-secondary mt-2 d-block mx-auto" 
          @click="showLineWarning = false"
        >
          我仍要嘗試
        </button>
      </div>
      
      <!-- URL 複製彈窗 -->
      <div v-if="showUrlModal" class="url-modal-overlay" @click.self="showUrlModal = false">
        <div class="url-modal">
          <div class="url-modal-header">
            <h5>{{ getDomain() }}</h5>
            <button class="btn-close-modal" @click="showUrlModal = false">✕</button>
          </div>
          <div class="url-modal-body">
            <p class="mb-3">請複製以下網址，並在外部瀏覽器（如 Chrome、Safari）中開啟：</p>
            <div class="url-input-group">
              <input 
                type="text" 
                :value="getExternalUrl()" 
                readonly 
                class="form-control url-input"
                ref="urlInput"
                id="external-url-input"
              >
              <button 
                class="btn btn-primary btn-copy" 
                @click="copyToClipboard"
                :class="{ 'btn-success': urlCopied }"
              >
                {{ urlCopied ? '✓ 已複製' : '複製' }}
              </button>
            </div>
            <p class="mt-3 small text-muted">
              或者點擊選單，選擇「在瀏覽器中開啟」
            </p>
          </div>
          <div class="url-modal-footer">
            <button class="btn btn-primary" @click="showUrlModal = false">確定</button>
          </div>
        </div>
      </div>
      
      <!-- 正常 Google 登入按鈕 -->
      <div v-else>
        <div id="google-signin-btn" class="google-btn-container"></div>
        <p v-if="googleLoading" class="text-muted mt-2">正在載入 Google 登入...</p>
        <p v-if="googleError" class="text-danger mt-2">{{ googleError }}</p>
        <button 
          v-if="googleError && (googleError.includes('403') || googleError.includes('disallowed'))"
          class="btn btn-sm btn-warning mt-2" 
          @click="showLineWarning = true"
        >
          在內嵌瀏覽器中遇到問題？點擊這裡
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { apiUrl } from '@/config/api'
import { getUser, setAuth, apiGet, apiPost } from '@/utils/api'

export default {
  name: 'LoginView',
  data() {
    return {
      account: '',
      password: '',
      googleClientId: null,
      googleLoading: true,
      googleError: '',
      isLineBrowser: false,
      showLineWarning: false,
      showUrlModal: false,
      urlCopied: false,
      sdkWaitAttempts: 0
    }
  },
  mounted() {
    // 檢查是否已登入，如果已登入則重定向
    this.checkLoginAndRedirect()
    
    this.detectLineBrowser()
    if (!this.isLineBrowser) {
      this.initGoogleSignIn()
    } else {
      this.googleLoading = false
    }
  },
  methods: {
    checkLoginAndRedirect() {
      // 檢查是否已登入
      const user = getUser()
      if (user) {
        // 已登入，重定向到對應的首頁
        const homeRoute = user.role === 'Admin' ? '/admin-lobby' : '/lobby'
        this.$router.replace(homeRoute)
      }
    },
    
    detectLineBrowser() {
      // 檢測是否為 LINE 內嵌瀏覽器
      const userAgent = navigator.userAgent || navigator.vendor || window.opera
      
      // 調試：輸出 User-Agent 以便檢查
      console.log('User-Agent:', userAgent)
      
      // LINE 內嵌瀏覽器的多種檢測方式
      // 1. 直接檢測 LINE 相關標識
      const hasLine = /Line|LINE/i.test(userAgent)
      
      // 2. 檢測 LINE 特定的 User-Agent 模式
      // LINE iOS: 通常包含 "Line/" 或 "LINE/"
      // LINE Android: 可能包含 "Line/" 或特定的版本號
      const isLineIOS = /Line\/|LINE\//i.test(userAgent)
      const isLineAndroid = /Line\/\d|LINE\/\d/i.test(userAgent)
      
      // 3. 檢測是否在 LINE 的 WebView 中（通過 referrer 或其他方式）
      const referrer = document.referrer || ''
      const isLineWebView = referrer.includes('line.me') || 
                           referrer.includes('line.naver.jp') ||
                           referrer.includes('line-apps.com')
      
      // 4. 檢測 window 對象的特殊屬性（某些內嵌瀏覽器會設置）
      const hasLineWindowProps = window.Line || window.LINE || window.__LINE__
      
      // 5. 檢測其他可能被封鎖的內嵌瀏覽器
      const isFacebookBrowser = /FBAN|FBAV|FB_IAB|FB4A/i.test(userAgent)
      const isInstagramBrowser = /Instagram/i.test(userAgent)
      const isTwitterBrowser = /Twitter/i.test(userAgent)
      
      // 綜合判斷：如果是 LINE 相關且不是標準瀏覽器
      this.isLineBrowser = (hasLine || isLineIOS || isLineAndroid || isLineWebView || hasLineWindowProps) ||
                          isFacebookBrowser || isInstagramBrowser || isTwitterBrowser
      
      // 如果檢測到，輸出調試信息
      if (this.isLineBrowser) {
        console.log('檢測到內嵌瀏覽器:', {
          hasLine,
          isLineIOS,
          isLineAndroid,
          isLineWebView,
          hasLineWindowProps,
          isFacebookBrowser,
          isInstagramBrowser,
          isTwitterBrowser,
          userAgent,
          referrer
        })
      } else {
        // 即使沒檢測到，也輸出 User-Agent 以便調試
        console.log('未檢測到內嵌瀏覽器，User-Agent:', userAgent, 'Referrer:', referrer)
      }
    },
    
    getExternalUrl() {
      // 獲取完整的登入頁面 URL
      // 確保使用正確的協議和域名
      const origin = window.location.origin
      const path = '/login'
      return `${origin}${path}`
    },
    
    getDomain() {
      // 獲取域名（不包含協議）
      return window.location.hostname
    },
    
    async copyToClipboard() {
      try {
        const urlInput = this.$refs.urlInput
        if (urlInput) {
          urlInput.select()
          urlInput.setSelectionRange(0, 99999) // 對於移動設備
          
          // 使用 Clipboard API
          if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(this.getExternalUrl())
          } else {
            // 降級方案：使用 document.execCommand
            document.execCommand('copy')
          }
          
          this.urlCopied = true
          setTimeout(() => {
            this.urlCopied = false
          }, 2000)
        }
      } catch (error) {
        console.error('Failed to copy:', error)
        // 如果複製失敗，至少選中文字讓用戶可以手動複製
        const urlInput = this.$refs.urlInput
        if (urlInput) {
          urlInput.select()
        }
        alert('無法自動複製，請手動選中並複製網址')
      }
    },
    
    async initGoogleSignIn() {
      try {
        // 從後端獲取 Google Client ID
        const response = await apiGet('auth/google/client-id')
        
        if (response.status === 'success' && response.client_id) {
          this.googleClientId = response.client_id
          this.googleLoading = false
          
          // 等待 Google SDK 載入完成
          this.waitForGoogleSDK()
        } else {
          this.googleLoading = false
          this.googleError = 'Google 登入未配置'
        }
      } catch (error) {
        console.error('Failed to get Google Client ID:', error)
        this.googleLoading = false
        this.googleError = 'Google 登入暫時不可用'
      }
    },
    
    waitForGoogleSDK() {
      // 如果已經顯示警告，不需要渲染按鈕
      if (this.isLineBrowser || this.showLineWarning) {
        return
      }
      
      // 檢查 Google SDK 是否已載入
      if (window.google && window.google.accounts) {
        this.renderGoogleButton()
      } else {
        // 等待 SDK 載入，但設置超時避免無限循環
        const maxAttempts = 50 // 最多嘗試 5 秒
        if (!this.sdkWaitAttempts) {
          this.sdkWaitAttempts = 0
        }
        this.sdkWaitAttempts++
        
        if (this.sdkWaitAttempts < maxAttempts) {
          setTimeout(() => this.waitForGoogleSDK(), 100)
        } else {
          console.error('Google SDK failed to load after timeout')
          this.googleLoading = false
          this.googleError = 'Google 登入載入超時，請重新整理頁面'
        }
      }
    },
    
    renderGoogleButton() {
      if (!this.googleClientId) return
      
      // 檢查元素是否存在（可能在 v-else 區塊中不可見）
      const buttonElement = document.getElementById('google-signin-btn')
      if (!buttonElement) {
        console.warn('Google sign-in button element not found')
        return
      }
      
      try {
        window.google.accounts.id.initialize({
          client_id: this.googleClientId,
          callback: this.handleGoogleCallback,
          auto_select: false,
          cancel_on_tap_outside: true
        })
        
        window.google.accounts.id.renderButton(
          buttonElement,
          {
            theme: 'outline',
            size: 'large',
            width: 300,
            text: 'signin_with',
            shape: 'rectangular',
            logo_alignment: 'left'
          }
        )
      } catch (error) {
        console.error('Failed to render Google button:', error)
        // 如果渲染失敗，可能是內嵌瀏覽器
        this.showLineWarning = true
        this.googleLoading = false
        this.googleError = '無法載入 Google 登入按鈕，可能是在內嵌瀏覽器中'
      }
    },
    
    async handleGoogleCallback(response) {
      try {
        // 發送 Google credential 到後端驗證
        const result = await apiPost('auth/google', {
          credential: response.credential
        })
        
        if (result.status === 'success' && result.token) {
          // 存儲 token 和用戶信息
          setAuth(result.token, result.user)
          this.$router.push(result.user.role === 'Admin' ? '/admin-lobby' : '/lobby')
        } else {
          alert(result.message || 'Google 登入失敗')
        }
      } catch (error) {
        console.error('Google login error:', error)
        const errorMessage = error.message || error.toString() || ''
        
        // 檢查是否是內嵌瀏覽器相關的錯誤
        if (errorMessage.includes('403') || 
            errorMessage.includes('disallowed_useragent') ||
            errorMessage.includes('disallowed_useragent')) {
          this.showLineWarning = true
          this.googleError = 'Google 登入在內嵌瀏覽器中無法使用'
        } else {
          alert('Google 登入失敗，請稍後再試')
        }
      }
    },
    
    async handleLogin() {
      try {
        const response = await fetch(apiUrl('login'), {
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
        if (data.status === 'success' && data.token) {
          // 存儲 token 和用戶信息
          setAuth(data.token, data.user)
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

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: #6c757d;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #dee2e6;
}

.divider span {
  padding: 0 15px;
}

.google-btn-container {
  display: flex;
  justify-content: center;
  min-height: 44px;
}

.line-browser-warning {
  text-align: left;
  border-left: 4px solid #ffc107;
  background-color: #fff3cd;
  border-color: #ffc107;
}

.line-browser-warning p {
  margin-bottom: 0.5rem;
}

.line-browser-warning .small {
  font-size: 0.875rem;
  color: #856404;
}

/* URL 複製彈窗樣式 */
.url-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.url-modal {
  background: #fff;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.url-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8f9fa;
}

.url-modal-header h5 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #2d3748;
}

.url-modal-header .btn-close-modal {
  background: none;
  border: none;
  color: #718096;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.url-modal-header .btn-close-modal:hover {
  color: #2d3748;
}

.url-modal-body {
  padding: 20px;
}

.url-input-group {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.url-input {
  flex: 1;
  font-size: 0.9rem;
  padding: 8px 12px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
}

.btn-copy {
  white-space: nowrap;
  min-width: 80px;
}

.url-modal-footer {
  padding: 16px 20px;
  border-top: 1px solid #e2e8f0;
  background: #f8f9fa;
  text-align: right;
}
</style>
