# Bello

<<<<<<< Updated upstream
## 開發環境

- Windows 11

- Python: 3.10.9
  - Flask: 3.1.0
  - psycopg2: 2.9.10
  - python-dotenv: 1.0.1

- PostgreSQL: 16.6

- Node.js: 21.5.0
=======
🌐 **線上版本：** [https://bello-tw.vercel.app/](https://bello-tw.vercel.app/)

Bello 是一款以資料庫為核心設計的網頁交友系統，提供一個輕鬆又安全的平台，讓使用者能夠發起或參與如午餐、咖啡、語言交換等實體聚會，並支援跨語言交流。系統分為 User 與 Admin 兩大角色，使用者可以自由註冊帳號、編輯個人資料、舉辦與參加聚會，並透過平台內建聊天室與其他人溝通，而管理員則能控管聚會內容與使用者行為，維護平台秩序。

## ✨ 功能特色

### 👤 用戶功能
- **多元登入方式**：支援帳號密碼登入與 Google OAuth 登入
- **個人資料管理**：完整的個人資料編輯，包含頭像上傳與裁剪功能
- **聚會管理**：發起、參與、取消聚會，支援多種聚會類型（午餐、咖啡、晚餐、喝酒、語言交換）
- **聚會密碼保護**：可為聚會設定密碼，其他用戶需輸入正確密碼才能加入
- **地點整合**：支援 Google Places 自動完成輸入地點，並可在地圖上查看聚會位置
- **即時通訊**：
  - 一對一私人聊天
  - 聚會群組聊天室
  - 在線狀態顯示
- **好友系統**：
  - 搜尋並添加好友（支援帳號、姓名、暱稱搜尋）
  - 好友請求管理（發送、接受、拒絕）
  - 好友列表與在線狀態（含頭像顯示）
  - 查看其他用戶的公開個人資料（完整基本資料與詳細資料）
  - 社群帳號顯示（願意交換時顯示所有社群帳號）
  - 所有用戶列表均顯示頭像（私人聊天、好友列表、搜尋結果）

### 🔐 管理員功能
- **聚會管理**：查看所有聚會、查看聚會詳情、取消聚會、結束聚會
- **用戶管理**：瀏覽所有用戶列表、查看用戶詳細資料、刪除用戶、支援 ID 搜尋
- **聊天記錄查看**：
  - 查看所有私人聊天對話列表（顯示雙方用戶、訊息數、最後訊息時間）
  - 查看所有聚會聊天列表（顯示聚會資訊、訊息數、狀態）
  - 點擊查看詳細聊天記錄
  - 支援分頁瀏覽和 ID 搜尋

### 🎨 使用者體驗
- 頁面載入狀態管理（避免數據閃爍）
- 響應式設計適配各種螢幕尺寸
- 載入動畫與操作反饋
- 友善的錯誤提示

### 🛡️ 安全特性
- JWT Token 認證機制
- 路由權限控制（Navigation Guards）
- API 端點保護（`@require_auth`、`@require_admin` 裝飾器）
- 內嵌瀏覽器檢測與提示（LINE、Facebook 等）

## 🛠️ 技術棧

### 前端
- **框架**：Vue.js 3.5.13
- **路由**：Vue Router 4.4.5
- **UI 框架**：Bootstrap 5.3.3
- **構建工具**：Vite 6.0.1
- **圖片處理**：Cropper.js 1.6.2（頭像裁剪）
- **HTTP 客戶端**：Axios 1.7.9

### 後端
- **框架**：Flask 3.1.0
- **資料庫**：PostgreSQL（Neon 雲端資料庫）
- **資料庫驅動**：psycopg2-binary 2.9.9
- **認證**：PyJWT 2.8.0
- **密碼雜湊**：bcrypt 4.1.2
- **OAuth**：google-auth 2.25.2
- **CORS**：Flask-CORS 5.0.0

### 部署
- **前端部署**：Vercel
- **後端部署**：Vercel Serverless Functions
- **資料庫**：Neon PostgreSQL

## 📁 專案結構

```
Bello_system/
├── frontend/                 # 前端專案
│   ├── src/
│   │   ├── components/      # Vue 組件
│   │   ├── views/           # 頁面視圖
│   │   ├── router/          # 路由配置
│   │   ├── utils/           # 工具函數（API、認證等）
│   │   └── config/          # 配置文件
│   ├── public/              # 靜態資源
│   └── package.json
├── backend/                 # 後端專案
│   ├── actions/             # API 端點
│   │   ├── auth/            # 認證相關
│   │   ├── meeting/         # 聚會管理
│   │   ├── profile/         # 個人資料
│   │   ├── chat/            # 聊天功能
│   │   ├── friend/          # 好友系統
│   │   └── admin/           # 管理員功能
│   ├── DB_utils.py          # 資料庫工具類
│   ├── jwt_utils.py         # JWT 工具函數
│   ├── app.py               # Flask 應用入口
│   ├── config.py            # 配置文件
│   ├── init_bello_db.sql    # 資料庫初始化腳本
│   └── requirements.txt     # Python 依賴
├── api/                     # Vercel Serverless Function
│   ├── index.py             # 入口文件
│   └── requirements.txt
├── vercel.json              # Vercel 部署配置
└── README.md
```

## 🚀 快速開始

### 環境要求

- Python 3.10.9+
- Node.js 21.5.0+
- PostgreSQL 資料庫（建議使用 Neon）

### 1. 克隆專案

```bash
git clone <repository-url>
cd final-project/Bello_system
```

### 2. 後端設置

#### 安裝依賴

```bash
cd backend
pip install -r requirements.txt
```

#### 環境變數配置

複製 `backend/.env.example` 並重命名為 `backend/.env`，填入以下配置：

```env
# 資料庫連接
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require

# 伺服器配置
SERVER_HOST=127.0.0.1
SERVER_PORT=8800

# JWT 配置
JWT_SECRET_KEY=your-secret-key-here
JWT_EXPIRATION_HOURS=24

# Google OAuth 配置
GOOGLE_CLIENT_ID=your-google-client-id
```

#### 初始化資料庫

1. 登入 [Neon 控制台](https://console.neon.tech/)
2. 使用 SQL Editor 執行 `backend/init_bello_db.sql` 文件中的 SQL 語句
3. 或使用 psql 命令：
   ```bash
   psql <your-neon-connection-string> -f backend/init_bello_db.sql
   ```

#### 啟動後端服務

```bash
cd backend
python app.py
```

後端服務將在 `http://127.0.0.1:8800` 啟動。

### 3. 前端設置

#### 安裝依賴

```bash
cd frontend
npm install
```

#### 環境變數配置（選用，需使用 Google Maps 功能時）

複製 `frontend/.env.example` 並重命名為 `frontend/.env`，填入以下配置：

```env
# Google Maps API Key（用於地點自動完成與地圖顯示）
VITE_GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

> 📍 需要在 [Google Cloud Console](https://console.cloud.google.com/apis/credentials) 啟用 **Maps JavaScript API** 和 **Places API**

#### 啟動開發伺服器

```bash
npm run dev
```

前端服務將在 `http://127.0.0.1:5173` 啟動。

### 4. 訪問應用

打開瀏覽器訪問 `http://127.0.0.1:5173`

## 📦 部署

### Vercel 部署

本專案已配置 Vercel 部署，支援自動部署：

1. 將專案推送到 GitHub
2. 在 Vercel 中導入專案
3. 設置環境變數（與 `.env` 相同）
4. Vercel 會自動構建並部署

詳細配置請參考 `vercel.json`。

### 環境變數設置

在 Vercel 專案設置中添加以下環境變數：

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `JWT_EXPIRATION_HOURS`
- `GOOGLE_CLIENT_ID`
- `VITE_GOOGLE_MAPS_API_KEY`（前端用，用於地點功能）

## 🏗️ 系統架構

### 前端架構

- **組件化設計**：使用 Vue 3 Composition API
- **路由管理**：Vue Router 實現 SPA 路由，包含權限守衛
- **狀態管理**：使用 localStorage 存儲認證狀態
- **API 封裝**：統一的 API 請求處理，自動添加 JWT Token

### 後端架構

- **RESTful API**：遵循 REST 設計原則
- **模組化設計**：使用 Flask Blueprint 組織路由
- **認證機制**：JWT Token 認證，支援裝飾器保護端點
- **資料庫抽象**：`DB_utils.py` 封裝所有資料庫操作

### 資料庫設計

- **正規化**：符合 4NF 正規化
- **主要資料表**：
  - `USER`：用戶基本資料
  - `USER_DETAIL`：用戶詳細資料
  - `MEETING`：聚會資訊
  - `PARTICIPATION`：參與記錄
  - `FRIENDSHIP`：好友關係
  - `PRIVATE_MESSAGE`：私人訊息
  - `CHATTING_ROOM`：聚會聊天記錄

## 🔑 主要功能說明

### 認證系統

- **JWT Token**：登入後發放 JWT Token，有效期 24 小時
- **路由保護**：未登入用戶訪問受保護路由會自動重定向到登入頁
- **Google OAuth**：支援 Google 帳號登入（內嵌瀏覽器會顯示提示）

### 好友系統

- **好友請求**：發送、接受、拒絕好友請求
- **好友列表**：查看所有好友及其在線狀態
- **用戶搜尋**：搜尋用戶並發送好友請求
- **個人資料查看**：查看其他用戶的公開個人資料

### 聊天系統

- **私人聊天**：一對一即時聊天
- **聚會聊天**：群組聊天室，支援查看所有參與者
- **在線狀態**：實時顯示用戶在線/離線狀態
  - 心跳機制：前端每 30 秒發送狀態更新
  - 判斷邏輯：60 秒內有活動才算在線
- **訊息歷史**：保存並顯示聊天記錄

### 聚會系統

- **聚會類型**：午餐、咖啡/下午茶、晚餐、喝酒、語言交換
- **語言篩選**：支援多種語言標籤
- **參與管理**：加入、離開、取消聚會
- **狀態管理**：進行中、已完成、已取消

## 🧪 開發說明

### 前端開發

```bash
cd frontend
npm run dev      # 啟動開發伺服器
npm run build    # 構建生產版本
npm run lint     # 代碼檢查
```

### 後端開發

```bash
cd backend
python app.py    # 啟動 Flask 開發伺服器
```

### 資料庫操作

所有資料庫操作都通過 `DB_utils.py` 中的 `DatabaseManager` 類進行，確保連接管理和錯誤處理的一致性。

## 📝 API 端點

### 認證相關
- `POST /login` - 用戶登入
- `POST /signup` - 用戶註冊
- `POST /auth/google` - Google OAuth 登入
- `GET /auth/google/client-id` - 獲取 Google Client ID

### 聚會相關
- `GET /meetings` - 獲取聚會列表
- `POST /create-meeting` - 創建聚會
- `POST /join-meeting` - 加入聚會
- `POST /leave-meeting` - 離開聚會
- `GET /my-meetings/:user_id` - 獲取我的聚會

### 聊天相關
- `GET /my-chats` - 獲取聊天列表
- `GET /private-chat/history` - 獲取私人聊天記錄
- `POST /private-chat/send` - 發送私人訊息
- `GET /meeting-chat/:meeting_id` - 獲取聚會聊天記錄
- `POST /meeting-chat/send` - 發送聚會訊息

### 好友相關
- `GET /friends` - 獲取好友列表
- `POST /friends/add` - 發送好友請求
- `POST /friends/accept` - 接受好友請求
- `POST /friends/reject` - 拒絕好友請求
- `GET /friends/status/:user_id` - 檢查好友狀態

### 個人資料
- `GET /user-profile/:user_id` - 獲取用戶資料
- `GET /friends/user-profile/:user_id` - 獲取其他用戶的公開資料
- `POST /update-profile` - 更新個人資料
- `POST /update-avatar` - 更新頭像

### 管理員相關
- `GET /admin/users` - 獲取所有用戶列表（支援分頁和搜尋）
- `GET /admin/users/:user_id` - 獲取用戶詳細資料
- `POST /admin/users/:user_id/remove` - 移除用戶
- `GET /admin/meetings` - 獲取所有聚會列表
- `GET /admin/all-private-chats` - 獲取所有私人聊天對話列表
- `POST /admin/chat-history` - 獲取指定兩個用戶間的聊天記錄
- `GET /admin/all-meeting-chats` - 獲取所有有聊天記錄的聚會列表
- `GET /admin/meeting-chat/:meeting_id` - 獲取指定聚會的聊天記錄

所有需要認證的端點都需要在請求頭中包含 `Authorization: Bearer <token>`。

## 🔒 安全特性

- **JWT 認證**：所有 API 請求都需要有效的 JWT Token
- **角色權限**：管理員功能需要 `Admin` 角色
- **CORS 配置**：正確配置跨域請求
- **輸入驗證**：後端驗證所有輸入參數
- **SQL 注入防護**：使用參數化查詢
>>>>>>> Stashed changes

## 使用方法

<<<<<<< Updated upstream
### 後端設置 (127.0.0.1/8800)
1. 將 `backend/.env.example` 複製一份並改名為 `.env` 後填入相關資訊
   前端 port 程式中皆已預設為 5173、後端 port 設為 8800 (.env檔案、app.py、config.py、DB_utils、main.py)
2. 安裝相關套件 
    ```bash
    cd backend
    pip install -r requirements.txt
    ```
3. 使用 SQL 檔案初始化資料庫 
   port 已設為 5432 (.env檔案、app.py、config.py、main.py)
   資料庫密碼設為 0000，如需更改請至 DB_utils.py 第 14 行、config.py 第 10 行、.env 檔 3 處更改！！！！！！！！！！
    ```bash
    psql -U <username> -f init_bello_db.sql
    ```
4. 啟動後端服務
    ```bash
    python main.py
    ```
=======
本專案為期末專案作品。

## 👥 貢獻

本專案為學習用途，歡迎提出建議和改進。
>>>>>>> Stashed changes

### 前端設置 (127.0.0.1/5173)
1. 安裝相關套件
    ```bash
    cd frontend
    npm install
    ```
2. 啟動開發伺服器
    ```bash
    npm run dev
    ```

<<<<<<< Updated upstream
## 程式架構說明

### 前端 (Vue.js)
1. **Views**
   - 頁面級元件，對應不同路由
   - 主要功能：
     * `HomeView`: 首頁
     * `LoginView`/`RegisterView`: 用戶認證
     * `MeetingsView`: 聚會列表與管理
     * `ProfileView`: 個人資料管理
     * `AdminView`: 管理員後台

2. **Router**
   - 基於 Vue Router 實現的路由系統
   - 包含Navigation Guards，控制頁面訪問權限
   - 實現前端頁面導航與狀態管理

### 後端 (Flask)
1. **Actions**
   - REST API 端點實現
   - 主要模組：
     * `auth/`: 用戶認證相關
     * `meeting/`: 聚會管理功能
     * `profile/`: 個人資料操作
     * `admin/`: 管理員功能
     * `chat/`: 即時通訊功能

2. **DB_utils**
   - 封裝與資料庫相關的功能，包含資料庫連線管理與查詢操作。
=======
**開發者**：期末專案團隊  
**最後更新**：2025年1月
>>>>>>> Stashed changes
