# 💬 Bello — 交友聚會邀約與即時聊天系統

Bello 是一款以資料庫為核心設計的網頁交友系統，旨在提供一個輕鬆又安全的平台，讓使用者能夠發起或參與如午餐、咖啡、語言交換等實體聚會，並支援跨語言交流。系統分為 User 與 Admin 兩大角色，使用者可以自由註冊帳號、編輯個人資料、舉辦與參加聚會，並透過平台內建聊天室與其他人溝通，而管理員則能控管聚會內容與使用者行為，維護平台秩序。

## 🌐 線上版本

**Deploy Link:** [https://bello-system.vercel.app](https://bello-system.vercel.app)

## ✨ 主要功能

### 使用者功能
- **使用者認證系統**
  - 使用者註冊與登入
  - 角色權限管理 (User/Admin)
  - 安全的密碼驗證機制

- **聚會管理系統**
  - 建立新聚會 (支援 5 種聚會類型：午餐、咖啡/下午茶、晚餐、喝酒、語言交換)
  - 瀏覽所有可參加的聚會
  - 參與與離開聚會
  - 管理自己舉辦的聚會 (取消、完成)
  - 多語言篩選功能 (支援 15 種語言)
  - 聚會狀態管理 (進行中、已完成、已取消)

- **個人資料管理**
  - 編輯基本資料 (姓名、暱稱、城市、電話、Email 等)
  - 編輯詳細資料 (星座、MBTI、血型、宗教、婚姻狀況等)
  - SNS 帳號管理 (支援 10 種社群平台)

- **即時聊天系統**
  - 私人一對一聊天
  - 聚會群組聊天
  - 使用者搜尋與配對
  - 聊天記錄查詢

### 管理員功能
- **聚會管理**
  - 查看所有聚會
  - 強制取消或完成聚會
  - 聚會統計與分析

- **使用者管理**
  - 查看所有使用者列表
  - 查看使用者詳細資訊
  - 移除使用者帳號

- **聊天記錄管理**
  - 查看私人聊天記錄
  - 查看聚會聊天記錄
  - 聊天記錄查詢與篩選

## 🛠️ 技術棧

### 前端
- **框架與工具**
  - Vue.js 3.5.13 (Composition API)
  - Vue Router 4.4.5 (路由管理)
  - Pinia 2.2.6 (狀態管理)
  - Vite 6.0.1 (建置工具)

- **UI 框架**
  - Bootstrap 5.3.3
  - Bootstrap Vue Next 0.26.10

- **HTTP 客戶端**
  - Axios 1.7.9

### 後端
- **框架**
  - Flask 3.1.0
  - Flask-CORS 5.0.0 (跨域資源共享)

- **資料庫**
  - PostgreSQL 16.6
  - psycopg2-binary 2.9.10 (資料庫驅動)

- **工具**
  - python-dotenv 1.0.1 (環境變數管理)

### 資料庫設計
- **9 張資料表**
  - `USER`: 使用者基本資料
  - `USER_DETAIL`: 使用者詳細資料
  - `USER_ROLE`: 使用者角色 (User/Admin)
  - `MEETING`: 聚會資料
  - `MEETING_LANGUAGE`: 聚會語言
  - `PARTICIPATION`: 參與記錄
  - `SNS_DETAIL`: 社群媒體帳號
  - `CHATTING_ROOM`: 聚會聊天室
  - `PRIVATE_MESSAGE`: 私人訊息

- **資料完整性**
  - 外鍵約束 (ON DELETE CASCADE)
  - CHECK 約束 (確保資料值符合規範)
  - UNIQUE 約束 (Account, Email)
  - 複合主鍵設計

## 📋 專案實作內容

在此專案中，我與組員負責從資料建模、後端資料庫設計、前端頁面開發到前後端串接的全流程，實作內容包括：

- 設計 ER diagram、Relational Schema 與 4NF 正規化資料表
- 實作 9 張資料表及複合索引與外鍵約束
- 撰寫 SQL 指令實現註冊、登入、聚會建立與查詢、聊天室互動等功能
- 使用 Python 與 PostgreSQL 串接實作後端邏輯
- 前端介面使用 Vue.js 開發並配合後端串接資料
- 匯入模擬資料（10,000 筆）並進行效能測試與資料庫分區優化

本系統最終具備完整註冊登入、語言篩選、多語聊天室、一對一私訊、參與紀錄等功能，並成功整合使用者互動與聚會管理邏輯。透過這次期末專案，我深刻理解了資料庫從資料建模、正規化、查詢設計到系統整合的全流程，也首次實作了具備實用價值的交友服務原型。

## 🚀 快速開始

### 環境需求

- **作業系統**: Windows 11 / macOS / Linux
- **Python**: 3.10.9 或以上
- **PostgreSQL**: 16.6 或以上
- **Node.js**: 21.5.0 或以上
- **npm**: 與 Node.js 一起安裝

### 後端設置 (127.0.0.1:8800)

1. **環境變數設定**
   ```bash
   cd backend
   cp .env.example .env
   ```
   編輯 `.env` 檔案，填入相關資訊：
   - 資料庫連線資訊 (host, port, database, user, password)
   - 前端 port 已預設為 5173
   - 後端 port 已預設為 8800

2. **安裝 Python 套件**
   ```bash
   pip install -r requirements.txt
   ```

3. **資料庫初始化**
   ```bash
   # 確保 PostgreSQL 服務已啟動
   # 預設資料庫密碼為 0000，如需更改請至以下檔案修改：
   # - DB_utils.py 第 14 行
   # - config.py 第 10 行
   # - .env 檔案
   
   psql -U <username> -f init_bello_db.sql
   ```
   
   **注意**: 如果資料庫已存在，建議先刪除舊資料庫：
   ```sql
   DROP DATABASE bello;
   ```
   然後重新執行初始化腳本。

4. **啟動後端服務**
   ```bash
   python main.py
   ```
   
   後端服務將在 `http://127.0.0.1:8800` 啟動

### 前端設置 (127.0.0.1:5173)

1. **安裝 Node.js 套件**
   ```bash
   cd frontend
   npm install
   ```

2. **啟動開發伺服器**
   ```bash
   npm run dev
   ```
   
   前端服務將在 `http://127.0.0.1:5173` 啟動

3. **建置生產版本** (可選)
   ```bash
   npm run build
   npm run preview
   ```

### 測試建議

- **多使用者測試**: 建議使用不同瀏覽器或無痕視窗登入不同帳號進行測試
- **聊天功能測試**: 需要至少兩個使用者同時在線才能完整測試聊天功能
- **管理員測試**: 建議準備三個視窗 (2 個使用者 + 1 個管理員) 進行完整功能測試

## 📁 專案結構

```
Bello_system/
├── backend/                 # 後端 Flask 應用
│   ├── actions/            # API 端點實作
│   │   ├── auth/          # 認證相關 API
│   │   │   ├── login.py
│   │   │   ├── signup.py
│   │   │   └── exit.py
│   │   ├── meeting/       # 聚會管理 API
│   │   │   ├── create_meeting.py
│   │   │   ├── list_meeting.py
│   │   │   ├── join_meeting.py
│   │   │   ├── leave_meeting.py
│   │   │   ├── cancel_meeting.py
│   │   │   ├── finish_meeting.py
│   │   │   └── my_meetings.py
│   │   ├── profile/       # 個人資料 API
│   │   │   ├── get_profile.py
│   │   │   ├── update_profile.py
│   │   │   └── sns_management.py
│   │   ├── chat/          # 聊天功能 API
│   │   │   ├── private_chat.py
│   │   │   ├── meeting_chat.py
│   │   │   └── search_user.py
│   │   └── admin/         # 管理員功能 API
│   │       ├── meetings.py
│   │       ├── users.py
│   │       ├── cancel_meeting.py
│   │       ├── finish_meeting.py
│   │       ├── remove_user.py
│   │       ├── chat_partners.py
│   │       ├── chat_history.py
│   │       └── meeting_chat.py
│   ├── app.py             # Flask 應用主程式
│   ├── main.py            # 應用程式入口
│   ├── config.py          # 設定檔
│   ├── DB_utils.py        # 資料庫管理類別
│   ├── init_bello_db.sql  # 資料庫初始化腳本
│   ├── requirements.txt   # Python 依賴套件
│   ├── users.csv          # 模擬資料 (10,000 筆)
│   └── .env.example       # 環境變數範例
│
├── frontend/              # 前端 Vue.js 應用
│   ├── src/
│   │   ├── views/        # 頁面元件
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   ├── LobbyView.vue
│   │   │   ├── CreateMeetingView.vue
│   │   │   ├── MeetingListView.vue
│   │   │   ├── MyMeetingsView.vue
│   │   │   ├── ProfileView.vue
│   │   │   ├── ChatView.vue
│   │   │   ├── MeetingChatView.vue
│   │   │   ├── AdminLobbyView.vue
│   │   │   ├── AdminMeetingsView.vue
│   │   │   ├── AdminUsersView.vue
│   │   │   ├── AdminUserChatRecordsView.vue
│   │   │   └── AdminMeetingChatRecordsView.vue
│   │   ├── components/   # 可重用元件
│   │   │   ├── MeetingCard.vue
│   │   │   └── UserMeetingCard.vue
│   │   ├── router/       # 路由設定
│   │   │   └── index.js
│   │   ├── stores/       # Pinia 狀態管理
│   │   │   └── counter.js
│   │   ├── assets/       # 靜態資源
│   │   ├── App.vue       # 根元件
│   │   └── main.js       # 應用程式入口
│   ├── package.json      # Node.js 依賴套件
│   ├── vite.config.js    # Vite 設定檔
│   └── index.html        # HTML 模板
│
├── plan.md               # 專案計劃文件
└── README.md             # 專案說明文件
```

## 🔌 API 端點說明

### 認證相關
- `POST /api/login` - 使用者登入
- `POST /api/signup` - 使用者註冊
- `POST /api/exit` - 使用者登出

### 聚會管理
- `POST /api/create-meeting` - 建立新聚會
- `GET /api/list-meeting` - 查詢可參加聚會列表
- `POST /api/join-meeting` - 參與聚會
- `POST /api/leave-meeting` - 離開聚會
- `POST /api/cancel-meeting` - 取消聚會
- `POST /api/finish-meeting` - 完成聚會
- `GET /api/my-meetings/<user_id>` - 查詢我的聚會

### 個人資料
- `GET /api/user-profile/<user_id>` - 取得使用者個人資料
- `POST /api/update-profile` - 更新個人資料
- `POST /api/sns-management` - SNS 帳號管理

### 聊天功能
- `GET /api/my-chats/<user_id>` - 取得聊天列表
- `POST /api/private-chat/history` - 取得私人聊天記錄
- `POST /api/private-chat/send` - 發送私人訊息
- `GET /api/available-chat-users/<user_id>` - 取得可聊天使用者列表
- `GET /api/meeting-chat` - 聚會聊天相關功能
- `GET /api/search-user` - 搜尋使用者

### 管理員功能
- `GET /api/admin/meetings` - 取得所有聚會
- `POST /api/admin/cancel-meeting` - 管理員取消聚會
- `POST /api/admin/finish-meeting` - 管理員完成聚會
- `GET /api/admin/users` - 取得所有使用者
- `GET /api/admin/users/<user_id>` - 取得使用者詳細資訊
- `POST /api/admin/remove-user` - 移除使用者
- `GET /api/admin/chat-partners` - 取得聊天配對列表
- `GET /api/admin/chat-history` - 取得聊天記錄
- `GET /api/admin/meeting-chat` - 取得聚會聊天記錄

## 🎯 主要特色

1. **完整的資料庫設計**
   - 4NF 正規化設計
   - 完整的資料完整性約束
   - 支援 10,000+ 筆資料的效能測試

2. **前後端分離架構**
   - RESTful API 設計
   - 模組化程式碼組織
   - 易於維護與擴展

3. **使用者體驗優化**
   - 響應式設計 (支援行動裝置)
   - 直覺的使用者介面
   - 即時資料更新

4. **安全性**
   - 角色權限管理
   - 資料驗證機制
   - 路由守衛保護

## 📝 開發環境

- **作業系統**: Windows 11
- **Python**: 3.10.9
  - Flask: 3.1.0
  - psycopg2-binary: 2.9.10
  - python-dotenv: 1.0.1
- **PostgreSQL**: 16.6
- **Node.js**: 21.5.0

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！

## 📄 授權

本專案為學術專案，僅供學習與研究使用。

---

---

# 💬 Bello — Social Meeting & Chat System

Bello is a database-centric web-based social networking system designed to provide a relaxed and secure platform where users can initiate or participate in physical gatherings such as lunch, coffee, language exchange, and more, with support for cross-language communication. The system features two main roles: User and Admin. Users can freely register accounts, edit profiles, host and join meetings, and communicate with others through built-in chat rooms, while administrators can manage meeting content and user behavior to maintain platform order.

## 🌐 Live Demo

**Deploy Link:** [https://bello-system.vercel.app](https://bello-system.vercel.app)

## ✨ Key Features

### User Features
- **User Authentication System**
  - User registration and login
  - Role-based access control (User/Admin)
  - Secure password verification mechanism

- **Meeting Management System**
  - Create new meetings (supports 5 meeting types: lunch, coffee/afternoon tea, dinner, drinks, language exchange)
  - Browse all available meetings
  - Join and leave meetings
  - Manage hosted meetings (cancel, finish)
  - Multi-language filtering (supports 15 languages)
  - Meeting status management (Ongoing, Finished, Canceled)

- **Profile Management**
  - Edit basic information (name, nickname, city, phone, email, etc.)
  - Edit detailed information (zodiac sign, MBTI, blood type, religion, marital status, etc.)
  - SNS account management (supports 10 social platforms)

- **Real-time Chat System**
  - Private one-on-one chat
  - Group chat for meetings
  - User search and matching
  - Chat history query

### Admin Features
- **Meeting Management**
  - View all meetings
  - Force cancel or finish meetings
  - Meeting statistics and analysis

- **User Management**
  - View all user lists
  - View user detailed information
  - Remove user accounts

- **Chat Record Management**
  - View private chat records
  - View meeting chat records
  - Chat record query and filtering

## 🛠️ Tech Stack

### Frontend
- **Frameworks & Tools**
  - Vue.js 3.5.13 (Composition API)
  - Vue Router 4.4.5 (Routing)
  - Pinia 2.2.6 (State Management)
  - Vite 6.0.1 (Build Tool)

- **UI Framework**
  - Bootstrap 5.3.3
  - Bootstrap Vue Next 0.26.10

- **HTTP Client**
  - Axios 1.7.9

### Backend
- **Framework**
  - Flask 3.1.0
  - Flask-CORS 5.0.0 (Cross-Origin Resource Sharing)

- **Database**
  - PostgreSQL 16.6
  - psycopg2-binary 2.9.10 (Database Driver)

- **Tools**
  - python-dotenv 1.0.1 (Environment Variables)

### Database Design
- **9 Database Tables**
  - `USER`: User basic information
  - `USER_DETAIL`: User detailed information
  - `USER_ROLE`: User roles (User/Admin)
  - `MEETING`: Meeting data
  - `MEETING_LANGUAGE`: Meeting languages
  - `PARTICIPATION`: Participation records
  - `SNS_DETAIL`: Social media accounts
  - `CHATTING_ROOM`: Meeting chat rooms
  - `PRIVATE_MESSAGE`: Private messages

- **Data Integrity**
  - Foreign key constraints (ON DELETE CASCADE)
  - CHECK constraints (ensures data values conform to specifications)
  - UNIQUE constraints (Account, Email)
  - Composite primary key design

## 📋 Project Implementation

In this project, my team and I were responsible for the entire process from data modeling, backend database design, frontend page development to frontend-backend integration. Implementation includes:

- Designed ER diagram, Relational Schema, and 4NF normalized database tables
- Implemented 9 database tables with composite indexes and foreign key constraints
- Wrote SQL commands to implement registration, login, meeting creation and query, chat room interaction, and other functions
- Used Python and PostgreSQL to implement backend logic
- Developed frontend interface using Vue.js and integrated with backend data
- Imported simulated data (10,000 records) and performed performance testing and database partitioning optimization

The system ultimately includes complete registration/login, language filtering, multi-language chat rooms, one-on-one private messaging, participation records, and other functions, successfully integrating user interaction and meeting management logic. Through this final project, I gained a deep understanding of the entire process from data modeling, normalization, query design to system integration in databases, and also implemented a practical social networking service prototype for the first time.

## 🚀 Quick Start

### Requirements

- **OS**: Windows 11 / macOS / Linux
- **Python**: 3.10.9 or above
- **PostgreSQL**: 16.6 or above
- **Node.js**: 21.5.0 or above
- **npm**: Installed with Node.js

### Backend Setup (127.0.0.1:8800)

1. **Environment Variables**
   ```bash
   cd backend
   cp .env.example .env
   ```
   Edit the `.env` file and fill in relevant information:
   - Database connection information (host, port, database, user, password)
   - Frontend port is preset to 5173
   - Backend port is preset to 8800

2. **Install Python Packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Initialization**
   ```bash
   # Ensure PostgreSQL service is running
   # Default database password is 0000. To change, modify the following files:
   # - DB_utils.py line 14
   # - config.py line 10
   # - .env file
   
   psql -U <username> -f init_bello_db.sql
   ```
   
   **Note**: If the database already exists, it's recommended to drop the old database first:
   ```sql
   DROP DATABASE bello;
   ```
   Then re-run the initialization script.

4. **Start Backend Service**
   ```bash
   python main.py
   ```
   
   Backend service will start at `http://127.0.0.1:8800`

### Frontend Setup (127.0.0.1:5173)

1. **Install Node.js Packages**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```
   
   Frontend service will start at `http://127.0.0.1:5173`

3. **Build Production Version** (Optional)
   ```bash
   npm run build
   npm run preview
   ```

### Testing Recommendations

- **Multi-user Testing**: It's recommended to use different browsers or incognito windows to log in with different accounts for testing
- **Chat Function Testing**: Requires at least two users to be online simultaneously to fully test chat functionality
- **Admin Testing**: It's recommended to prepare three windows (2 users + 1 admin) for complete functionality testing

## 📁 Project Structure

```
Bello_system/
├── backend/                 # Backend Flask application
│   ├── actions/            # API endpoint implementations
│   │   ├── auth/          # Authentication APIs
│   │   ├── meeting/       # Meeting management APIs
│   │   ├── profile/       # Profile APIs
│   │   ├── chat/          # Chat functionality APIs
│   │   └── admin/         # Admin functionality APIs
│   ├── app.py             # Flask application main program
│   ├── main.py            # Application entry point
│   ├── config.py          # Configuration file
│   ├── DB_utils.py        # Database management class
│   ├── init_bello_db.sql  # Database initialization script
│   ├── requirements.txt   # Python dependencies
│   ├── users.csv          # Simulated data (10,000 records)
│   └── .env.example       # Environment variables example
│
├── frontend/              # Frontend Vue.js application
│   ├── src/
│   │   ├── views/        # Page components
│   │   ├── components/   # Reusable components
│   │   ├── router/       # Route configuration
│   │   ├── stores/        # Pinia state management
│   │   ├── assets/       # Static resources
│   │   ├── App.vue       # Root component
│   │   └── main.js        # Application entry point
│   ├── package.json       # Node.js dependencies
│   ├── vite.config.js     # Vite configuration
│   └── index.html         # HTML template
│
├── plan.md                # Project plan document
└── README.md              # Project documentation
```

## 🔌 API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/signup` - User registration
- `POST /api/exit` - User logout

### Meeting Management
- `POST /api/create-meeting` - Create new meeting
- `GET /api/list-meeting` - Query available meetings
- `POST /api/join-meeting` - Join meeting
- `POST /api/leave-meeting` - Leave meeting
- `POST /api/cancel-meeting` - Cancel meeting
- `POST /api/finish-meeting` - Finish meeting
- `GET /api/my-meetings/<user_id>` - Query my meetings

### Profile
- `GET /api/user-profile/<user_id>` - Get user profile
- `POST /api/update-profile` - Update profile
- `POST /api/sns-management` - SNS account management

### Chat Functionality
- `GET /api/my-chats/<user_id>` - Get chat list
- `POST /api/private-chat/history` - Get private chat history
- `POST /api/private-chat/send` - Send private message
- `GET /api/available-chat-users/<user_id>` - Get available chat users
- `GET /api/meeting-chat` - Meeting chat functionality
- `GET /api/search-user` - Search users

### Admin Functions
- `GET /api/admin/meetings` - Get all meetings
- `POST /api/admin/cancel-meeting` - Admin cancel meeting
- `POST /api/admin/finish-meeting` - Admin finish meeting
- `GET /api/admin/users` - Get all users
- `GET /api/admin/users/<user_id>` - Get user details
- `POST /api/admin/remove-user` - Remove user
- `GET /api/admin/chat-partners` - Get chat partner list
- `GET /api/admin/chat-history` - Get chat history
- `GET /api/admin/meeting-chat` - Get meeting chat records

## 🎯 Key Highlights

1. **Complete Database Design**
   - 4NF normalized design
   - Complete data integrity constraints
   - Performance testing support for 10,000+ records

2. **Frontend-Backend Separation Architecture**
   - RESTful API design
   - Modular code organization
   - Easy to maintain and extend

3. **User Experience Optimization**
   - Responsive design (supports mobile devices)
   - Intuitive user interface
   - Real-time data updates

4. **Security**
   - Role-based access control
   - Data validation mechanisms
   - Route guard protection

## 📝 Development Environment

- **OS**: Windows 11
- **Python**: 3.10.9
  - Flask: 3.1.0
  - psycopg2-binary: 2.9.10
  - python-dotenv: 1.0.1
- **PostgreSQL**: 16.6
- **Node.js**: 21.5.0

## 🤝 Contributing

Welcome to submit Issues or Pull Requests!

## 📄 License

This project is an academic project for learning and research purposes only.
