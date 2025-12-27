// Google Maps API 動態載入工具

let isLoading = false
let isLoaded = false
let loadPromise = null

/**
 * 動態載入 Google Maps JavaScript API
 * @returns {Promise} 載入完成後 resolve
 */
export function loadGoogleMapsAPI() {
  // 如果已經載入完成，直接返回
  if (isLoaded && window.google && window.google.maps) {
    return Promise.resolve()
  }

  // 如果正在載入中，返回同一個 Promise
  if (isLoading && loadPromise) {
    return loadPromise
  }

  // 從環境變數取得 API Key
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY

  if (!apiKey) {
    console.error('VITE_GOOGLE_MAPS_API_KEY 未設定')
    return Promise.reject(new Error('Google Maps API Key 未設定'))
  }

  isLoading = true

  loadPromise = new Promise((resolve, reject) => {
    // 檢查是否已經有 script 標籤
    if (document.querySelector('script[src*="maps.googleapis.com"]')) {
      // 等待載入完成
      const checkLoaded = setInterval(() => {
        if (window.google && window.google.maps) {
          clearInterval(checkLoaded)
          isLoaded = true
          isLoading = false
          resolve()
        }
      }, 100)
      return
    }

    // 創建 script 標籤
    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&language=zh-TW`
    script.async = true
    script.defer = true

    script.onload = () => {
      isLoaded = true
      isLoading = false
      resolve()
    }

    script.onerror = (error) => {
      isLoading = false
      reject(new Error('Google Maps API 載入失敗'))
    }

    document.head.appendChild(script)
  })

  return loadPromise
}

/**
 * 檢查 Google Maps API 是否已載入
 * @returns {boolean}
 */
export function isGoogleMapsLoaded() {
  return isLoaded && window.google && window.google.maps
}

