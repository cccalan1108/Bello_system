// API 工具函數
// 統一管理所有 API 請求

import { apiUrl } from '@/config/api'

/**
 * 獲取存儲的 token
 */
export function getToken() {
  return localStorage.getItem('token')
}

/**
 * 獲取存儲的用戶信息
 */
export function getUser() {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
}

/**
 * 設置 token 和用戶信息
 */
export function setAuth(token, user) {
  localStorage.setItem('token', token)
  localStorage.setItem('user', JSON.stringify(user))
}

/**
 * 清除認證信息
 */
export function clearAuth() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

/**
 * 發送 API 請求的通用函數
 * @param {string} endpoint - API 端點（例如：'login', 'user-profile/1'）
 * @param {object} options - fetch 選項
 * @param {boolean} requireAuth - 是否需要認證（預設為 true）
 * @returns {Promise} fetch 響應
 */
export async function apiRequest(endpoint, options = {}, requireAuth = true) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  // 如果需要認證，自動添加 token
  if (requireAuth) {
    const token = getToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  }

  const response = await fetch(apiUrl(endpoint), {
    ...options,
    headers,
  })

  // 如果 token 過期或無效，清除認證信息
  if (response.status === 401 && requireAuth) {
    clearAuth()
    // 觸發自定義事件，讓組件處理重定向
    // 這樣可以避免在 apiRequest 中直接操作 window.location
    // 組件可以通過路由守衛或監聽事件來處理重定向
    window.dispatchEvent(new CustomEvent('auth-expired'))
    
    // 如果不在登入頁面，使用 window.location 進行重定向
    // 這是因為此時可能還沒有 router 實例
    if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
      // 使用 setTimeout 避免在請求過程中立即重定向
      setTimeout(() => {
        window.location.href = '/login'
      }, 100)
    }
  }

  return response
}

/**
 * GET 請求
 */
export async function apiGet(endpoint) {
  const response = await apiRequest(endpoint, { method: 'GET' })
  
  // 檢查響應狀態
  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('認證失敗，請重新登入')
    }
    
    try {
      const errorData = await response.json()
      throw new Error(errorData.message || '請求失敗')
    } catch (e) {
      if (e instanceof Error && e.message.includes('認證')) {
        throw e
      }
      throw new Error(`請求失敗: ${response.status} ${response.statusText}`)
    }
  }
  
  return response.json()
}

/**
 * POST 請求
 */
export async function apiPost(endpoint, data, contentType = 'application/json') {
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': contentType,
    },
  }

  if (contentType === 'application/json') {
    options.body = JSON.stringify(data)
  } else if (contentType === 'application/x-www-form-urlencoded') {
    options.body = new URLSearchParams(data)
  } else {
    options.body = data
  }

  const response = await apiRequest(endpoint, options)
  
  // 檢查響應狀態
  if (!response.ok) {
    // 如果是 401，已經在 apiRequest 中處理了重定向
    if (response.status === 401) {
      throw new Error('認證失敗，請重新登入')
    }
    
    // 嘗試解析錯誤訊息
    try {
      const errorData = await response.json()
      throw new Error(errorData.message || '請求失敗')
    } catch (e) {
      if (e instanceof Error && e.message.includes('認證')) {
        throw e
      }
      throw new Error(`請求失敗: ${response.status} ${response.statusText}`)
    }
  }
  
  return response.json()
}

/**
 * PUT 請求
 */
export async function apiPut(endpoint, data) {
  const response = await apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  return response.json()
}

/**
 * DELETE 請求
 */
export async function apiDelete(endpoint) {
  const response = await apiRequest(endpoint, { method: 'DELETE' })
  return response.json()
}

