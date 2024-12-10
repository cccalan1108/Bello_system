# Bello

## 開發環境

- Windows 11

- Python: 3.10.9
  - Flask: 3.1.0
  - psycopg2: 2.9.10
  - python-dotenv: 1.0.1

- PostgreSQL: 16.6

- Node.js: 21.5.0

## 使用方法

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
