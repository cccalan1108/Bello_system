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
                class="btn btn-primary btn-sm"
                @click="showUserDetails(user.user_id)"
              >
                查看詳細
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

export default {
  name: 'AdminUsersView',
  data() {
    return {
      users: [],
      searchId: '',
      selectedUser: null,
      userModal: null,
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
        const response = await fetch(
          `http://localhost:8800/api/admin/users?page=${this.currentPage}&limit=${this.itemsPerPage}${searchParam}`
        )
        const data = await response.json()
        if (data.status === 'success') {
          this.users = data.users
          this.totalUsers = data.total
        } else {
          alert(data.message)
        }
      } catch (error) {
        console.error('Error fetching users:', error)
        alert('獲取用戶列表失敗')
      }
    },
    async showUserDetails(userId) {
      try {
        const response = await fetch(`http://localhost:8800/api/admin/users/${userId}`)
        const data = await response.json()
        if (data.status === 'success') {
          this.selectedUser = data
          this.userModal.show()
        } else {
          alert(data.message)
        }
      } catch (error) {
        console.error('Error fetching user details:', error)
        alert('獲取用戶詳細資訊失敗')
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
    }
  },
  watch: {
    currentPage() {
      this.fetchUsers()
    }
  },
  mounted() {
    this.userModal = new Modal(document.getElementById('userDetailsModal'))
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
