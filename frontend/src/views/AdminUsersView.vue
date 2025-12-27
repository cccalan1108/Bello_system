<template>
  <div class="admin-users">
    <h2 class="mb-4">用戶管理</h2>
    
    <!-- 搜尋框 -->
    <div class="search-box mb-4">
      <input 
        type="number" 
        class="form-control" 
        v-model="searchId" 
        placeholder="輸入用戶ID搜尋"
        @input="handleSearch"
      >
    </div>
    
    <!-- 用戶列表 -->
    <div class="table-responsive">
      <table class="table table-hover">
        <thead>
          <tr>
            <th>ID</th>
            <th>帳號</th>
            <th>姓名</th>
            <th>暱稱</th>
            <th>Email</th>
            <th>城市</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.user_id">
            <td>{{ user.user_id }}</td>
            <td>{{ user.account }}</td>
            <td>{{ user.user_name }}</td>
            <td>{{ user.user_nickname }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.city }}</td>
            <td>
              <button 
                class="btn btn-primary btn-sm me-2"
                @click="showUserDetails(user.user_id)"
              >
                查看詳細
              </button>
              <button 
                class="btn btn-danger btn-sm"
                @click="confirmDeleteUser(user)"
              >
                刪除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 分頁控制 -->
    <div class="pagination-controls mt-4 d-flex justify-content-between align-items-center">
      <div>
        總共 {{ totalUsers }} 筆資料
      </div>
      <nav v-if="totalPages > 1">
        <ul class="pagination">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">上一頁</a>
          </li>
          <li v-for="page in displayedPages" 
              :key="page" 
              class="page-item"
              :class="{ active: page === currentPage }">
            <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">下一頁</a>
          </li>
        </ul>
      </nav>
    </div>
    
    <!-- 刪除確認 Modal -->
    <div class="modal fade" id="deleteConfirmModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title">⚠️ 確認刪除用戶</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="userToDelete">
            <p class="mb-3">你確定要刪除以下用戶嗎？此操作<strong>無法復原</strong>！</p>
            <div class="alert alert-warning">
              <p class="mb-1"><strong>帳號：</strong>{{ userToDelete.account }}</p>
              <p class="mb-1"><strong>姓名：</strong>{{ userToDelete.user_name }}</p>
              <p class="mb-0"><strong>Email：</strong>{{ userToDelete.email }}</p>
            </div>
            <p class="text-muted small">刪除後，該用戶的所有資料（包括聚會、聊天記錄、好友關係等）都將被刪除。</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
            <button 
              type="button" 
              class="btn btn-danger" 
              @click="deleteUser"
              :disabled="isDeleting"
            >
              {{ isDeleting ? '刪除中...' : '確認刪除' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 詳細資訊 Modal -->
    <div class="modal fade" id="userDetailsModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">用戶詳細資訊</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body" v-if="selectedUser">
              <div class="row">
                <div class="col-md-6">
                  <h6>基本資料</h6>
                  <p><strong>帳號：</strong>{{ selectedUser.basic_info.account }}</p>
                  <p><strong>姓名：</strong>{{ selectedUser.basic_info.user_name }}</p>
                  <p><strong>暱稱：</strong>{{ selectedUser.basic_info.user_nickname }}</p>
                  <p><strong>Email：</strong>{{ selectedUser.basic_info.email }}</p>
                  <p><strong>電話：</strong>{{ selectedUser.basic_info.phone }}</p>
                  <p><strong>生日：</strong>{{ selectedUser.basic_info.birthday }}</p>
                </div>
                <div class="col-md-6">
                  <h6>詳細資料</h6>
                  <p><strong>星座：</strong>{{ selectedUser.profile_info.Star_sign }}</p>
                  <p><strong>MBTI：</strong>{{ selectedUser.profile_info.Mbti }}</p>
                  <p><strong>血型：</strong>{{ selectedUser.profile_info.Blood_type }}</p>
                  <p><strong>宗教：</strong>{{ selectedUser.profile_info.Religion }}</p>
                  <p><strong>學校：</strong>{{ selectedUser.profile_info.University }}</p>
                  <p><strong>婚姻狀況：</strong>{{ selectedUser.profile_info.Married }}</p>
                </div>
              </div>
              <div class="row mt-3">
                <div class="col-12">
                  <h6>自我介紹</h6>
                  <p>{{ selectedUser.profile_info.Self_introduction }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap'
import { apiGet, apiDelete } from '@/utils/api'

export default {
  name: 'AdminUsersView',
  data() {
    return {
      users: [],
      searchId: '',
      selectedUser: null,
      userModal: null,
      deleteModal: null,
      userToDelete: null,
      isDeleting: false,
      currentPage: 1,
      totalUsers: 0,
      itemsPerPage: 100
    }
  },
  computed: {
    filteredUsers() {
      return this.users
    },
    totalPages() {
      return Math.ceil(this.totalUsers / this.itemsPerPage)
    },
    displayedPages() {
      const delta = 2
      const range = []
      for (let i = Math.max(1, this.currentPage - delta); 
           i <= Math.min(this.totalPages, this.currentPage + delta); 
           i++) {
        range.push(i)
      }
      return range
    }
  },
  methods: {
    async fetchUsers() {
      try {
        const searchParam = this.searchId ? `&search=${this.searchId}` : '';
        const data = await apiGet(
          `admin/users?page=${this.currentPage}&limit=${this.itemsPerPage}${searchParam}`
        )
        if (data.status === 'success') {
          this.users = data.users
          this.totalUsers = data.total
        } else {
          alert(data.message || '獲取用戶列表失敗')
        }
      } catch (error) {
        console.error('Error fetching users:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        } else {
          alert('獲取用戶列表失敗')
        }
      }
    },
    async showUserDetails(userId) {
      try {
        const data = await apiGet(`admin/users/${userId}`)
        if (data.status === 'success') {
          this.selectedUser = data
          this.userModal.show()
        } else {
          alert(data.message || '獲取用戶詳細資訊失敗')
        }
      } catch (error) {
        console.error('Error fetching user details:', error)
        if (error.message && error.message.includes('認證')) {
          this.$router.push('/login')
        } else {
          alert('獲取用戶詳細資訊失敗')
        }
      }
    },
    handleSearch: debounce(function() {
      this.currentPage = 1
      this.fetchUsers()
    }, 300),
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        this.fetchUsers()
      }
    },
    confirmDeleteUser(user) {
      this.userToDelete = user
      this.deleteModal.show()
    },
    async deleteUser() {
      if (!this.userToDelete) return
      
      this.isDeleting = true
      try {
        const data = await apiDelete(`admin/users/${this.userToDelete.user_id}`)
        if (data.status === 'success') {
          alert('用戶已成功刪除')
          this.deleteModal.hide()
          this.userToDelete = null
          this.fetchUsers() // 重新載入列表
        } else {
          alert(data.message || '刪除用戶失敗')
        }
      } catch (error) {
        console.error('Error deleting user:', error)
        alert(error.message || '刪除用戶失敗')
      } finally {
        this.isDeleting = false
      }
    }
  },
  watch: {
    currentPage() {
      this.fetchUsers()
    }
  },
  mounted() {
    this.userModal = new Modal(document.getElementById('userDetailsModal'))
    this.deleteModal = new Modal(document.getElementById('deleteConfirmModal'))
    this.fetchUsers()
  }
}

function debounce(fn, delay) {
  let timeout
  return function(...args) {
    clearTimeout(timeout)
    timeout = setTimeout(() => fn.apply(this, args), delay)
  }
}
</script>

<style scoped>
.admin-users {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.search-box {
  max-width: 300px;
}
</style>
