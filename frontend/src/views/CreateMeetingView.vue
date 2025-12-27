<template>
    <div class="create-meeting-form">
      <h2 class="mb-4">建立新聚會</h2>
      <form @submit.prevent="handleSubmit">
        <div class="mb-3">
          <label class="form-label required">聚會類型:</label>
          <select class="form-select custom-input" v-model="formData.content" required>
            <option value="">請選擇聚會類型</option>
            <option v-for="type in meetingTypes" :key="type" :value="type">
              {{ type }}
            </option>
          </select>
        </div>
  
        <div class="mb-3">
          <label class="form-label required">語言:</label>
          <div class="d-flex flex-wrap gap-2">
            <div v-for="lang in languages" :key="lang" class="form-check">
              <input 
                type="checkbox" 
                class="form-check-input" 
                :value="lang"
                v-model="formData.languages"
              >
              <label class="form-check-label">{{ lang }}</label>
            </div>
          </div>
        </div>
  
        <div class="mb-3">
          <label class="form-label required">地點:</label>
          <input 
            type="text" 
            class="form-control custom-input" 
            ref="placeInput"
            v-model="placeInputValue"
            placeholder="搜尋地點名稱或地址..."
            required
          >
          <div v-if="formData.address" class="selected-place-info mt-2">
            <small class="text-muted">
              📍 {{ formData.address }}
            </small>
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label required">城市:</label>
          <input type="text" class="form-control custom-input" v-model="formData.city" required>
          <small class="form-text text-muted">選擇地點後會自動填入，也可手動修改</small>
        </div>
  
        <div class="row">
          <div class="col-md-4">
            <div class="mb-3">
              <label class="form-label required">日期:</label>
              <input type="date" class="form-control custom-input" v-model="formData.date" required>
            </div>
          </div>
          <div class="col-md-4">
            <div class="mb-3">
              <label class="form-label required">開始時間:</label>
              <input type="time" class="form-control custom-input" v-model="formData.start_time" required>
            </div>
          </div>
          <div class="col-md-4">
            <div class="mb-3">
              <label class="form-label required">結束時間:</label>
              <input type="time" class="form-control custom-input" v-model="formData.end_time" required>
            </div>
          </div>
        </div>
  
        <div class="mb-4">
          <label class="form-label required">人數上限:</label>
          <input 
            type="number" 
            class="form-control custom-input" 
            v-model="formData.max_participants"
            min="2"
            max="20"
            required
          >
        </div>

        <div class="mb-3">
          <div class="form-check">
            <input 
              type="checkbox" 
              class="form-check-input" 
              id="enablePassword"
              v-model="enablePassword"
            >
            <label class="form-check-label" for="enablePassword">
              🔒 設定聚會密碼（其他人需輸入密碼才能加入）
            </label>
          </div>
        </div>

        <div v-if="enablePassword" class="mb-4">
          <label class="form-label">聚會密碼：</label>
          <input 
            type="password" 
            class="form-control custom-input" 
            v-model="formData.password"
            placeholder="輸入聚會密碼"
            minlength="4"
            maxlength="20"
          >
          <div class="form-text">密碼長度需為 4-20 個字元</div>
        </div>
  
        <div class="d-grid gap-2">
          <button type="submit" class="btn btn-primary">建立聚會</button>
          <router-link to="/lobby" class="btn btn-outline-secondary">返回</router-link>
        </div>
      </form>
    </div>
  </template>
  
  <script>
import { apiPost, getUser } from '@/utils/api'
import { loadGoogleMapsAPI } from '@/utils/googleMaps'

  export default {
    name: 'CreateMeetingView',
    data() {
      return {
        meetingTypes: ['午餐', '咖啡/下午茶', '晚餐', '喝酒', '語言交換'],
        languages: ['中文', '台語', '客語', '原住民語', '英文', '日文', '韓文', 
                   '法文', '德文', '西班牙文', '俄文', '阿拉伯文', '泰文', '越南文', '印尼文'],
        enablePassword: false,
        placeInputValue: '',
        autocomplete: null,
        mapsApiLoaded: false,
        formData: {
          content: '',
          languages: [],
          city: '',
          place: '',
          address: '',
          latitude: null,
          longitude: null,
          date: '',
          start_time: '',
          end_time: '',
          max_participants: 2,
          holder_id: null,
          password: null
        }
      }
    },
    created() {
      // 使用新的 getUser 函數
      const user = getUser()
      if (!user || !user.user_id) {
        this.$router.push('/login')
        return
      }
      
      this.formData.holder_id = user.user_id
    },
    async mounted() {
      try {
        await loadGoogleMapsAPI()
        this.mapsApiLoaded = true
        this.initAutocomplete()
      } catch (error) {
        console.error('Google Maps API 載入失敗:', error)
        // API 載入失敗時，用戶仍可手動輸入地點
      }
    },
    methods: {
      initAutocomplete() {
        // 檢查 Google Maps API 是否已載入
        if (typeof google === 'undefined' || !google.maps || !google.maps.places) {
          console.warn('Google Maps API 未載入，地點自動完成功能無法使用')
          return
        }

        const input = this.$refs.placeInput
        if (!input) return

        this.autocomplete = new google.maps.places.Autocomplete(input, {
          types: ['establishment', 'geocode'],
          componentRestrictions: { country: 'tw' },
          fields: ['name', 'formatted_address', 'geometry', 'address_components']
        })

        this.autocomplete.addListener('place_changed', () => {
          const place = this.autocomplete.getPlace()
          
          if (!place.geometry) {
            console.warn('No geometry for place')
            return
          }

          // 填入地點名稱
          this.formData.place = place.name || this.placeInputValue
          this.placeInputValue = place.name || this.placeInputValue
          
          // 填入完整地址
          this.formData.address = place.formatted_address || ''
          
          // 填入座標
          this.formData.latitude = place.geometry.location.lat()
          this.formData.longitude = place.geometry.location.lng()

          // 自動提取城市
          if (place.address_components) {
            for (const component of place.address_components) {
              if (component.types.includes('administrative_area_level_1') || 
                  component.types.includes('locality')) {
                this.formData.city = component.long_name
                break
              }
            }
          }

          console.log('Place selected:', {
            name: this.formData.place,
            address: this.formData.address,
            city: this.formData.city,
            lat: this.formData.latitude,
            lng: this.formData.longitude
          })
        })
      },
      async handleSubmit() {
        if (this.formData.languages.length === 0) {
          alert('請至少選擇一種語言')
          return
        }

        // 如果用戶手動輸入但沒選擇建議，使用輸入值作為地點名稱
        if (!this.formData.place && this.placeInputValue) {
          this.formData.place = this.placeInputValue
        }

        if (!this.formData.place) {
          alert('請輸入聚會地點')
          return
        }

        // 驗證密碼
        if (this.enablePassword) {
          if (!this.formData.password || this.formData.password.length < 4) {
            alert('請輸入至少 4 個字元的密碼')
            return
          }
          if (this.formData.password.length > 20) {
            alert('密碼不能超過 20 個字元')
            return
          }
        } else {
          // 如果未啟用密碼，確保 password 為 null
          this.formData.password = null
        }
  
        try {
          // 使用新的 apiPost 函數，會自動添加 token
          const data = await apiPost('create-meeting', this.formData)
          
          if (data.status === 'success') {
            alert('聚會建立成功！')
            this.$router.push('/my-meetings')
          } else {
            alert(data.message || '建立聚會失敗')
          }
        } catch (error) {
          console.error('建立聚會錯誤:', error)
          if (error.message && error.message.includes('token')) {
            alert('認證失敗，請重新登入')
            this.$router.push('/login')
          } else {
            alert('建立聚會失敗，請稍後再試')
          }
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .create-meeting-form {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    background: linear-gradient(145deg, #ffffff 0%, #fff9f5 100%);
    border-radius: 24px;
    box-shadow: 0 8px 32px rgba(255, 107, 107, 0.1);
    animation: fadeInUp 0.5s ease;
  }

  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  h2 {
    font-family: 'Nunito', sans-serif;
    font-weight: 800;
    color: #343A40;
    text-align: center;
    margin-bottom: 2rem;
  }

  h2::before {
    content: '🎉 ';
  }

  h2::after {
    content: ' ✨';
  }
  
  .form-label {
    font-family: 'Nunito', sans-serif;
    font-weight: 600;
    color: #495057;
  }

  .required:after {
    content: " *";
    color: #FF6B6B;
  }
  
  .custom-input {
    font-family: 'Nunito', sans-serif;
    background-color: #ffffff;
    border: 2px solid #E9ECEF;
    border-radius: 12px;
    padding: 0.75rem 1rem;
    transition: all 0.3s ease;
  }
  
  .custom-input:focus {
    background-color: #fff;
    border-color: #FF6B6B;
    box-shadow: 0 0 0 4px rgba(255, 107, 107, 0.15);
    outline: none;
  }

  .custom-input::placeholder {
    color: #CED4DA;
  }

  .form-select.custom-input {
    cursor: pointer;
  }

  .form-check-input {
    width: 1.2rem;
    height: 1.2rem;
    cursor: pointer;
  }

  .form-check-input:checked {
    background-color: #FF6B6B;
    border-color: #FF6B6B;
  }

  .form-check-label {
    font-family: 'Nunito', sans-serif;
    cursor: pointer;
    transition: color 0.2s;
  }

  .form-check-label:hover {
    color: #FF6B6B;
  }

  .selected-place-info {
    padding: 0.75rem 1rem;
    background: linear-gradient(135deg, #e8f8f5 0%, #d4efdf 100%);
    border-radius: 12px;
    border-left: 4px solid #4ECDC4;
    font-size: 0.9rem;
  }

  .btn-primary {
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
    border: none;
    border-radius: 50px;
    padding: 0.8rem 2rem;
    font-size: 1.1rem;
    box-shadow: 0 4px 20px rgba(255, 107, 107, 0.3);
    transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  }

  .btn-primary:hover {
    background: linear-gradient(135deg, #E85555 0%, #FF6B6B 100%);
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 8px 30px rgba(255, 107, 107, 0.4);
  }

  .btn-outline-secondary {
    font-family: 'Nunito', sans-serif;
    font-weight: 600;
    border: 2px solid #DEE2E6;
    border-radius: 50px;
    padding: 0.8rem 2rem;
    color: #6C757D;
    transition: all 0.3s ease;
  }

  .btn-outline-secondary:hover {
    border-color: #FF6B6B;
    color: #FF6B6B;
    background: rgba(255, 107, 107, 0.1);
  }

  /* 語言選擇區塊 - 簡潔風格 */
  .form-check {
    padding: 0.4rem 0.8rem;
    border-radius: 8px;
  }

  .form-check:has(.form-check-input:checked) {
    background: #FFE5E5;
    border-radius: 20px;
  }

  .form-text {
    color: #6C757D;
    font-size: 0.85rem;
  }

  /* 密碼設定區塊 */
  .form-check-label[for="enablePassword"] {
    font-weight: 600;
  }
  </style>