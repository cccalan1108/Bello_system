<template>
  <div class="profile-container">
    <h2 class="mb-4">編輯個人資料</h2>
    
    <!-- 載入中狀態 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">載入中...</span>
        </div>
        <p class="mt-3 text-muted">正在載入個人資料...</p>
      </div>
    </div>
    
    <!-- 頭像區塊 -->
    <div v-else class="avatar-section mb-4">
      <div class="avatar-wrapper" @click="toggleAvatarMenu">
        <div class="avatar-circle-large" v-if="!userData.avatar_url">
          {{ getAvatarText() }}
        </div>
        <img 
          v-else 
          :src="userData.avatar_url" 
          alt="頭像" 
          class="avatar-img-large"
        >
        <div class="avatar-overlay">
          <span class="overlay-icon">📷</span>
        </div>
      </div>
      <div class="user-display-name mt-3">
        {{ userData.user_name || '用戶' }}
      </div>
      <div class="user-account text-muted">
        @{{ userData.account || '' }}
      </div>
      
      <!-- 頭像選單 -->
      <div v-if="showAvatarMenu" class="avatar-menu">
        <div class="avatar-menu-item" @click="viewAvatar">
          <span class="menu-icon">🔍</span> 查看大頭貼
        </div>
        <div class="avatar-menu-item" @click="triggerAvatarUpload">
          <span class="menu-icon">✏️</span> 更改大頭貼
        </div>
      </div>
      
      <!-- 隱藏的文件上傳 -->
      <input 
        type="file" 
        ref="avatarInput" 
        @change="handleAvatarUpload" 
        accept="image/*" 
        style="display: none;"
      >
    </div>
    
    <!-- 查看大頭貼彈窗 -->
    <div v-if="showAvatarModal" class="avatar-modal" @click.self="closeAvatarModal">
      <div class="avatar-modal-content">
        <button class="btn-close-modal" @click="closeAvatarModal">✕</button>
        <div class="avatar-view-large" v-if="!userData.avatar_url">
          {{ getAvatarText() }}
        </div>
        <img 
          v-else 
          :src="userData.avatar_url" 
          alt="頭像" 
          class="avatar-view-img"
        >
      </div>
    </div>

    <!-- 圖片裁剪彈窗 -->
    <div v-if="showCropperModal" class="image-crop-modal">
      <div class="image-crop-modal-content">
        <div class="image-crop-header">
          <h5>裁剪頭像</h5>
          <button class="btn-close-modal" @click="closeCropper">✕</button>
        </div>
        <div class="image-crop-body">
          <div class="image-crop-container">
            <img ref="cropperImage" :src="cropperImageSrc" alt="裁剪圖片">
          </div>
        </div>
        <div class="image-crop-footer">
          <div class="image-crop-tools">
            <button class="btn btn-outline-secondary btn-sm" @click="rotateCropper(-90)" title="向左旋轉">
              ↺ 左轉
            </button>
            <button class="btn btn-outline-secondary btn-sm" @click="rotateCropper(90)" title="向右旋轉">
              ↻ 右轉
            </button>
            <button class="btn btn-outline-secondary btn-sm" @click="resetCropper" title="重置">
              ⟲ 重置
            </button>
          </div>
          <div class="image-crop-actions">
            <button class="btn btn-secondary" @click="closeCropper">取消</button>
            <button class="btn btn-primary" @click="confirmCrop" :disabled="uploadingAvatar">
              {{ uploadingAvatar ? '上傳中...' : '確認裁剪' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 基本資料區塊 -->
    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title mb-3">基本資料</h5>
        <div class="row g-3">
          <div class="col-md-6">
            <div class="mb-3">
              <label class="form-label"><strong>帳號:</strong></label>
              <input type="text" class="form-control" :value="userData.account || '未設定'" disabled>
              <small class="text-muted">帳號無法修改</small>
            </div>
            <div class="mb-3">
              <label class="form-label"><strong>姓名:</strong></label>
              <input type="text" class="form-control" v-model="userData.user_name" placeholder="請輸入姓名">
            </div>
            <div class="mb-3">
              <label class="form-label"><strong>暱稱:</strong></label>
              <input type="text" class="form-control" v-model="userData.user_nickname" placeholder="請輸入暱稱">
            </div>
          </div>
          <div class="col-md-6">
            <div class="mb-3">
              <label class="form-label"><strong>電子郵件:</strong></label>
              <input type="email" class="form-control" :value="userData.email || '未設定'" disabled>
              <small class="text-muted">電子郵件無法修改</small>
            </div>
            <div class="mb-3">
              <label class="form-label"><strong>電話:</strong></label>
              <input type="text" class="form-control" v-model="userData.phone" placeholder="請輸入電話號碼">
            </div>
            <div class="mb-3">
              <label class="form-label"><strong>生日:</strong></label>
              <input type="date" class="form-control" v-model="userData.birthday">
            </div>
          </div>
          <div class="col-md-6">
            <div class="mb-3">
              <label class="form-label"><strong>國籍:</strong></label>
              <input type="text" class="form-control" v-model="userData.nationality" placeholder="請輸入國籍">
            </div>
          </div>
          <div class="col-md-6">
            <div class="mb-3">
              <label class="form-label"><strong>城市:</strong></label>
              <input type="text" class="form-control" v-model="userData.city" placeholder="請輸入城市">
            </div>
          </div>
          <div class="col-md-6">
            <div class="mb-3">
              <label class="form-label"><strong>性別:</strong></label>
              <select class="form-select" v-model="userData.sex">
                <option value="">請選擇</option>
                <option value="男">男</option>
                <option value="女">女</option>
                <option value="其他">其他</option>
              </select>
            </div>
          </div>
        </div>

        <!-- 更新基本資料的提交按鈕 -->
        <div class="text-center mt-4">
          <button class="btn btn-primary" @click="updateBasicInfo">更新基本資料</button>
        </div>
      </div>
    </div>

    <!-- 詳細資料區塊 -->
    <div class="card">
      <div class="card-body">
        <h5 class="card-title mb-3">詳細資料</h5>
        
        <div class="row g-3">
          <!-- 選項類型的欄位 -->
          <div v-for="(field, key) in optionFields" :key="key" class="col-md-6">
            <div class="mb-3">
              <label class="form-label">{{ field.name }}:</label>
              <select class="form-select" v-model="profileData[key]">
                <option value="">請選擇</option>
                <option v-for="option in field.options" :key="option" :value="option">
                  {{ option }}
                </option>
              </select>
            </div>
          </div>
          <div v-if="profileData.Sns === 'YES'" class="mt-4">
            <h6 class="mb-3">社交媒體帳號</h6>
            <div class="row g-3">
            <div class="col-md-6">
                <label class="form-label">選擇平台:</label>
                <select class="form-select" v-model="selectedPlatform">
                <option value="">請選擇平台</option>
                <option v-for="platform in snsPlatforms" :key="platform" :value="platform">
                    {{ platform }}
                </option>
                </select>
            </div>
            <div class="col-md-6">
                <label class="form-label">帳號 ID:</label>
                <div class="d-flex">
                <input type="text" class="form-control" v-model="snsId">
                <button class="btn btn-secondary ms-2" @click="addSnsAccount">新增</button>
                </div>
            </div>
            </div>

            <!-- 顯示已添加的社交媒體帳號 -->
            <div class="mt-3">
            <div v-for="sns in snsAccounts" :key="sns.sns_type" class="d-flex align-items-center mb-2">
                <span class="me-2">{{ sns.sns_type }}: {{ sns.sns_id }}</span>
                <button class="btn btn-sm btn-danger" @click="removeSnsAccount(sns.sns_type)">刪除</button>
            </div>
            </div>
        </div>
          <!-- 文字類型的欄位 -->
          <div v-for="(field, key) in textFields" :key="key" class="col-md-6">
            <div class="mb-3">
              <label class="form-label">{{ field.name }}:</label>
              <input 
                type="text" 
                class="form-control"
                v-model="profileData[key]"
              >
            </div>
          </div>
        </div>

        <!-- 添加提交按鈕 -->
        <div class="text-center mt-4">
          <button class="btn btn-primary" @click="updateProfile">更新詳細資料</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getUser, apiGet, apiPost } from '@/utils/api'
import Cropper from 'cropperjs'
import 'cropperjs/dist/cropper.css'

export default {
  name: 'ProfileView',
  data() {
    return {
      loading: true,
      userData: {},
      profileData: {},
      showAvatarMenu: false,
      showAvatarModal: false,
      uploadingAvatar: false,
      // 裁剪相關
      showCropperModal: false,
      cropperImageSrc: '',
      cropper: null,
      optionFields: {
        Star_sign: {
          name: '星座',
          options: ['摩羯', '水瓶', '雙魚', '牡羊', '金牛', '雙子', '巨蟹', '獅子', '處女', '天秤', '天蠍', '射手']
        },
        Mbti: {
          name: 'MBTI',
          options: ['ISTP', 'ISFP', 'ESTP', 'ESFP', 'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ', 
                   'INTP', 'INTJ', 'ENTP', 'ENTJ', 'INFJ', 'INFP', 'ENFJ', 'ENFP']
        },
        Blood_type: {
          name: '血型',
          options: ['A', 'B', 'AB', 'O']
        },
        Religion: {
          name: '宗教',
          options: ['無', '佛教', '道教', '基督教', '天主教', '伊斯蘭教', '印度教', '其他']
        },
        Married: {
          name: '婚姻狀況',
          options: ['未婚', '已婚', '喪偶']
        },
        Sns: {
          name: '社交媒體狀態',
          options: ['YES', 'NO']
        }
      },
      textFields: {
        University: {
          name: '大學'
        },
        Self_introduction: {
          name: '自我介紹'
        },
        Interest: {
          name: '興趣'
        },
        Find_meeting_type: {
          name: '期望聚會類型'
        }
      },
      selectedPlatform: '',
      snsId: '',
      snsAccounts: [],
      snsPlatforms: [
        'Facebook', 'Instagram', 'Threads', 'X', 'Tiktok', 
        '小紅書', 'WhatsApp', 'LINE', 'WeChat', 'KakaoTalk'
      ]
    }
  },
  methods: {
    formatDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
    },
    
    // ======= 頭像相關方法 =======
    getAvatarText() {
      // 優先使用暱稱，其次是姓名
      const name = this.userData.user_nickname || this.userData.user_name || '用戶';
      // 取前兩個字
      return name.substring(0, 2);
    },
    
    toggleAvatarMenu() {
      this.showAvatarMenu = !this.showAvatarMenu;
    },
    
    viewAvatar() {
      this.showAvatarMenu = false;
      this.showAvatarModal = true;
    },
    
    closeAvatarModal() {
      this.showAvatarModal = false;
    },
    
    triggerAvatarUpload() {
      this.showAvatarMenu = false;
      this.$refs.avatarInput.click();
    },
    
    handleAvatarUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // 檢查文件類型
      if (!file.type.startsWith('image/')) {
        alert('請選擇圖片文件');
        return;
      }
      
      // 檢查文件大小（限制 10MB）
      if (file.size > 10 * 1024 * 1024) {
        alert('圖片大小不能超過 10MB');
        return;
      }
      
      // 讀取圖片並打開裁剪彈窗
      const reader = new FileReader();
      reader.onload = (e) => {
        this.cropperImageSrc = e.target.result;
        this.showCropperModal = true;
        
        // 等待 DOM 更新後初始化 Cropper
        this.$nextTick(() => {
          this.initCropper();
        });
      };
      reader.readAsDataURL(file);
      
      // 清空 input，允許再次選擇相同文件
      event.target.value = '';
    },
    
    // 初始化裁剪器
    initCropper() {
      if (this.cropper) {
        this.cropper.destroy();
      }
      
      const image = this.$refs.cropperImage;
      if (image) {
        this.cropper = new Cropper(image, {
          aspectRatio: 1, // 1:1 正方形
          viewMode: 1,
          dragMode: 'move',
          autoCropArea: 0.8,
          restore: false,
          guides: true,
          center: true,
          highlight: false,
          cropBoxMovable: true,
          cropBoxResizable: true,
          toggleDragModeOnDblclick: false,
          ready: () => {
            // 裁剪器準備好後的回調
          }
        });
      }
    },
    
    // 旋轉圖片
    rotateCropper(degree) {
      if (this.cropper) {
        this.cropper.rotate(degree);
      }
    },
    
    // 重置裁剪
    resetCropper() {
      if (this.cropper) {
        this.cropper.reset();
      }
    },
    
    // 關閉裁剪彈窗
    closeCropper() {
      if (this.cropper) {
        this.cropper.destroy();
        this.cropper = null;
      }
      this.showCropperModal = false;
      this.cropperImageSrc = '';
    },
    
    // 確認裁剪並上傳
    async confirmCrop() {
      if (!this.cropper) return;
      
      this.uploadingAvatar = true;
      
      try {
        // 獲取裁剪後的圖片（以 canvas 形式）
        const canvas = this.cropper.getCroppedCanvas({
          width: 400,  // 輸出寬度
          height: 400, // 輸出高度
          imageSmoothingEnabled: true,
          imageSmoothingQuality: 'high',
        });
        
        // 轉換為 base64
        const base64Data = canvas.toDataURL('image/jpeg', 0.9);
        
        // 上傳到後端
        const data = await apiPost('update-avatar', {
          avatar_data: base64Data
        });
        
        if (data.status === 'success') {
          this.userData.avatar_url = data.avatar_url || base64Data;
          alert('頭像更新成功！');
          this.closeCropper();
        } else {
          alert(data.message || '頭像更新失敗');
        }
      } catch (error) {
        console.error('Error uploading avatar:', error);
        alert('頭像上傳失敗');
      } finally {
        this.uploadingAvatar = false;
      }
    },
    
    // 點擊頁面其他地方關閉選單
    handleClickOutside(event) {
      if (this.showAvatarMenu) {
        const avatarWrapper = this.$el.querySelector('.avatar-wrapper');
        const avatarMenu = this.$el.querySelector('.avatar-menu');
        if (avatarWrapper && !avatarWrapper.contains(event.target) && 
            avatarMenu && !avatarMenu.contains(event.target)) {
          this.showAvatarMenu = false;
        }
      }
    },
    
    async fetchUserData() {
      this.loading = true;
      try {
        const user = getUser();
        
        if (!user || !user.user_id) {
          this.$router.push('/login');
          return;
        }

        // 使用 apiGet，後端會從 token 獲取 user_id
        const data = await apiGet(`user-profile/${user.user_id}`);
        console.log(data)
        if (data.status === 'success') {
          // 確保所有欄位都有預設值，避免顯示 undefined
          this.userData = {
            account: data.basic_info?.account || '',
            user_name: data.basic_info?.user_name || '',
            user_nickname: data.basic_info?.user_nickname || '',
            email: data.basic_info?.email || '',
            phone: data.basic_info?.phone || '',
            birthday: data.basic_info?.birthday || '',
            nationality: data.basic_info?.nationality || '',
            city: data.basic_info?.city || '',
            sex: data.basic_info?.sex || '',
            avatar_url: data.basic_info?.avatar_url || ''
          };
          this.profileData = data.profile_info || {};
          await this.fetchSnsAccounts();
        } else {
          alert(data.message || '獲取用戶資料失敗');
        }
      } catch (error) {
        console.error('Error fetching user data:', error);
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login');
        } else {
          alert('獲取用戶資料失敗');
        }
      } finally {
        this.loading = false;
      }
    },
    async addSnsAccount() {
      if (!this.selectedPlatform || !this.snsId) {
        alert('請選擇平台並輸入帳號 ID');
        return;
      }

      try {
        // 使用 apiPost，後端會從 token 獲取 user_id
        const data = await apiPost('add-sns', {
          platform: this.selectedPlatform,
          sns_id: this.snsId
        });

        if (data.status === 'success') {
          await this.fetchSnsAccounts();
          this.selectedPlatform = '';
          this.snsId = '';
        } else {
          alert(data.message || '新增社交媒體帳號失敗');
        }
      } catch (error) {
        console.error('Error adding SNS account:', error);
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login');
        } else {
          alert('新增社交媒體帳號失敗');
        }
      }
    },

    async fetchSnsAccounts() {
      try {
        const user = getUser();
        // 使用 apiGet，後端會從 token 獲取 user_id
        const data = await apiGet(`sns-accounts/${user.user_id}`);
        
        if (data.status === 'success') {
          this.snsAccounts = data.sns_accounts;
        }
      } catch (error) {
        console.error('Error fetching SNS accounts:', error);
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login');
        }
      }
    },

    async removeSnsAccount(platform) {
      try {
        // 使用 apiPost，後端會從 token 獲取 user_id
        const data = await apiPost('remove-sns', {
          platform: platform
        });

        if (data.status === 'success') {
          await this.fetchSnsAccounts();
        } else {
          alert(data.message || '刪除社交媒體帳號失敗');
        }
      } catch (error) {
        console.error('Error removing SNS account:', error);
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login');
        } else {
          alert('刪除社交媒體帳號失敗');
        }
      }
    },

    async updateBasicInfo() {
      try {
        const updates = [];
        
        // 將基本資料轉換為 updates 陣列
        if (this.userData.user_name) {
          updates.push({ field: 'User_name', value: this.userData.user_name });
        }
        if (this.userData.user_nickname) {
          updates.push({ field: 'User_nickname', value: this.userData.user_nickname });
        }
        if (this.userData.phone) {
          updates.push({ field: 'Phone', value: this.userData.phone });
        }
        if (this.userData.birthday) {
          updates.push({ field: 'Birthday', value: this.userData.birthday });
        }
        if (this.userData.nationality) {
          updates.push({ field: 'Nationality', value: this.userData.nationality });
        }
        if (this.userData.city) {
          updates.push({ field: 'City', value: this.userData.city });
        }
        if (this.userData.sex) {
          updates.push({ field: 'Sex', value: this.userData.sex });
        }

        if (updates.length === 0) {
          alert('請至少填寫一項基本資料');
          return;
        }

        // 使用 apiPost，後端會從 token 獲取 user_id
        const data = await apiPost('update-profile', {
          updates: updates
        });

        if (data.status === 'success') {
          alert('基本資料更新成功！');
          await this.fetchUserData();
        } else {
          alert(data.message || '更新基本資料失敗');
        }
      } catch (error) {
        console.error('Error updating basic info:', error);
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login');
        } else {
          alert('更新基本資料失敗');
        }
      }
    },

    async updateProfile() {
      try {
        const updates = [];
        
        // 將 profileData 轉換為 updates 陣列
        for (const [field, value] of Object.entries(this.profileData)) {
          if (value !== undefined && value !== null && value !== '') {
            updates.push({ field, value });
          }
        }

        if (updates.length === 0) {
          alert('請至少填寫一項詳細資料');
          return;
        }

        // 使用 apiPost，後端會從 token 獲取 user_id
        const data = await apiPost('update-profile', {
          updates: updates
        });

        if (data.status === 'success') {
          alert('詳細資料更新成功！');
          if (this.profileData.Sns === 'YES') {
            this.fetchUserData();
          }
        } else {
          alert(data.message || '更新資料失敗');
        }
      } catch (error) {
        console.error('Error updating profile:', error);
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login');
        } else {
          alert('更新資料失敗');
        }
      }
    }
  },
  created() {
    this.fetchUserData();
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  }
}
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

/* ======= 載入狀態樣式 ======= */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.loading-spinner {
  text-align: center;
}

.loading-spinner .spinner-border {
  width: 3rem;
  height: 3rem;
}

/* ======= 頭像區塊樣式 ======= */
.avatar-section {
  text-align: center;
  position: relative;
  padding: 30px 0;
  background: #fff;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border: 1px solid #e2e8f0;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.avatar-wrapper:hover {
  transform: scale(1.05);
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.avatar-circle-large {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 42px;
  border: 4px solid #fff;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.avatar-img-large {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #fff;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.overlay-icon {
  font-size: 28px;
}

.user-display-name {
  color: #2d3748;
  font-size: 1.4rem;
  font-weight: 600;
}

.user-account {
  color: #718096;
  font-size: 0.9rem;
}

/* 頭像選單 */
.avatar-menu {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  overflow: hidden;
  z-index: 100;
  min-width: 160px;
  margin-top: 10px;
}

.avatar-menu::before {
  content: '';
  position: absolute;
  top: -8px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-bottom: 8px solid #fff;
}

.avatar-menu-item {
  padding: 12px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background 0.2s ease;
  color: #333;
  font-size: 0.95rem;
}

.avatar-menu-item:hover {
  background: #f0f4f8;
}

.avatar-menu-item:not(:last-child) {
  border-bottom: 1px solid #eee;
}

.menu-icon {
  margin-right: 10px;
  font-size: 1.1rem;
}

/* 查看大頭貼彈窗 */
.avatar-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.avatar-modal-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.btn-close-modal {
  position: absolute;
  top: -40px;
  right: -10px;
  background: none;
  border: none;
  color: #fff;
  font-size: 28px;
  cursor: pointer;
  padding: 5px 10px;
  transition: transform 0.2s;
}

.btn-close-modal:hover {
  transform: scale(1.2);
}

.avatar-view-large {
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 100px;
  border: 6px solid #fff;
  box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}

.avatar-view-img {
  max-width: 400px;
  max-height: 400px;
  border-radius: 50%;
  object-fit: cover;
  border: 6px solid #fff;
  box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}

/* ======= 卡片樣式 ======= */
.card {
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card-title {
  color: #2d3748;
  font-weight: 600;
}

.form-label {
  font-weight: 500;
  color: #4a5568;
}

.form-control, .form-select {
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 8px 12px;
}

.form-control:focus, .form-select:focus {
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
}

/* ======= 圖片裁剪彈窗樣式 ======= */
.image-crop-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
}

.image-crop-modal-content {
  background: #fff;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

.image-crop-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
  background: #fff;
}

.image-crop-header h5 {
  margin: 0;
  color: #2d3748;
  font-weight: 600;
}

.image-crop-header .btn-close-modal {
  position: static;
  color: #718096;
  font-size: 20px;
  background: none;
  border: none;
  cursor: pointer;
}

.image-crop-header .btn-close-modal:hover {
  color: #2d3748;
}

.image-crop-body {
  flex: 1;
  padding: 20px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a2e;
  min-height: 350px;
}

.image-crop-container {
  width: 100%;
  max-height: 400px;
}

.image-crop-container img {
  display: block;
  max-width: 100%;
  max-height: 400px;
}

.image-crop-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-top: 1px solid #e2e8f0;
  background: #fff;
}

.image-crop-tools {
  display: flex;
  gap: 8px;
}

.image-crop-tools .btn {
  display: flex;
  align-items: center;
  gap: 4px;
}

.image-crop-actions {
  display: flex;
  gap: 10px;
}

/* Cropper.js 自定義樣式 - 裁剪區域外的遮罩 */
:deep(.cropper-modal) {
  background-color: rgba(0, 0, 0, 0.7) !important;
}

/* 裁剪框樣式 */
:deep(.cropper-view-box) {
  border-radius: 50%;
  box-shadow: 0 0 0 1px #39f;
  outline: 0;
}

:deep(.cropper-face) {
  border-radius: 50%;
  background-color: transparent;
}

:deep(.cropper-line) {
  background-color: #39f;
}

:deep(.cropper-point) {
  background-color: #39f;
  width: 10px;
  height: 10px;
  opacity: 0.9;
}

/* 裁剪框虛線 */
:deep(.cropper-dashed) {
  border-color: rgba(255, 255, 255, 0.5);
}
</style>
