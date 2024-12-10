<template>
  <div class="profile-container">
    <h2 class="mb-4">編輯個人資料</h2>
    
    <!-- 基本資料區塊 -->
    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title mb-3">基本資料</h5>
        <div class="row">
          <div class="col-md-6">
            <p><strong>帳號:</strong> {{ userData.account }}</p>
            <p><strong>姓名:</strong> {{ userData.user_name }}</p>
            <p><strong>暱稱:</strong> {{ userData.user_nickname }}</p>
          </div>
          <div class="col-md-6">
            <p><strong>電子郵件:</strong> {{ userData.email }}</p>
            <p><strong>電話:</strong> {{ userData.phone }}</p>
            <p><strong>生日:</strong> {{ formatDate(userData.birthday) }}</p>
          </div>
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
          <button class="btn btn-primary" @click="updateProfile">更新資料</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProfileView',
  data() {
    return {
      userData: {},
      profileData: {},
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
    async fetchUserData() {
      try {
        const user = JSON.parse(localStorage.getItem('user'));
        
        if (!user || !user.user_id) {
          this.$router.push('/login');
          return;
        }

        const response = await fetch(`http://localhost:8800/api/user-profile/${user.user_id}`);
        console.log(response)
        const data = await response.json();
        console.log(data)
        if (data.status === 'success') {
          this.userData = data.basic_info;
          this.profileData = data.profile_info;
        } else {
          alert(data.message);
        }
      } catch (error) {
        console.error('Error fetching user data:', error);
        alert('獲取用戶資料失敗');
      }
    },
    async addSnsAccount() {
      if (!this.selectedPlatform || !this.snsId) {
        alert('請選擇平台並輸入帳號 ID');
        return;
      }

      try {
        const user = JSON.parse(localStorage.getItem('user'));
        const response = await fetch('http://localhost:8800/api/add-sns', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: user.user_id,
            platform: this.selectedPlatform,
            sns_id: this.snsId
          })
        });

        const data = await response.json();
        if (data.status === 'success') {
          await this.fetchSnsAccounts();
          this.selectedPlatform = '';
          this.snsId = '';
        } else {
          alert(data.message);
        }
      } catch (error) {
        console.error('Error adding SNS account:', error);
        alert('新增社交媒體帳號失敗');
      }
    },

    async fetchSnsAccounts() {
      try {
        const user = JSON.parse(localStorage.getItem('user'));
        const response = await fetch(`http://localhost:8800/api/sns-accounts/${user.user_id}`);
        const data = await response.json();
        
        if (data.status === 'success') {
          this.snsAccounts = data.sns_accounts;
        }
      } catch (error) {
        console.error('Error fetching SNS accounts:', error);
      }
    },

    async removeSnsAccount(platform) {
      try {
        const user = JSON.parse(localStorage.getItem('user'));
        const response = await fetch('http://localhost:8800/api/remove-sns', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: user.user_id,
            platform: platform
          })
        });

        const data = await response.json();
        if (data.status === 'success') {
          await this.fetchSnsAccounts();
        } else {
          alert(data.message);
        }
      } catch (error) {
        console.error('Error removing SNS account:', error);
        alert('刪除社交媒體帳號失敗');
      }
    },

    async updateProfile() {
      try {
        const user = JSON.parse(localStorage.getItem('user'));
        const updates = [];
        
        // 將 profileData 轉換為 updates 陣列
        for (const [field, value] of Object.entries(this.profileData)) {
          if (value !== undefined && value !== null && value !== '') {
            updates.push({ field, value });
          }
        }

        const response = await fetch('http://localhost:8800/api/update-profile', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: user.user_id,
            updates: updates
          })
        });

        const data = await response.json();
        if (data.status === 'success') {
          alert('更新成功！');
          if (this.profileData.Sns === 'YES') {
            this.fetchUserData();
          }
        } else {
          alert(data.message);
        }
      } catch (error) {
        console.error('Error updating profile:', error);
        alert('更新資料失敗');
      }
    }
  },
  created() {
    this.fetchUserData();
  }
}
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

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
</style>
