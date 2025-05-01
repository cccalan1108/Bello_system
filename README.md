# 💬 Bello —— 交友與語言交換聚會系統（資料庫期末專案）
Bello 是一款以資料庫為核心設計的網頁交友系統，旨在提供一個輕鬆又安全的平台，讓使用者能夠發起或參與如午餐、咖啡、語言交換等實體聚會，並支援跨語言交流。系統分為 User 與 Admin 兩大角色，使用者可以自由註冊帳號、編輯個人資料、舉辦與參加聚會，並透過平台內建聊天室與其他人溝通，而管理員則能控管聚會內容與使用者行為，維護平台秩序。

在此專案中，我與組員負責從資料建模、後端資料庫設計、前端頁面開發到前後端串接的全流程，實作內容包括：

設計 ER diagram、Relational Schema 與 4NF 正規化資料表
實作 9 張資料表及複合索引與外鍵約束（如 USER、MEETING、PARTICIPATION 等）
撰寫 SQL 指令實現註冊、登入、聚會建立與查詢、聊天室互動等功能
使用 Python 與 PostgreSQL 串接實作後端邏輯
前端介面使用 HTML/CSS/JavaScript 開發並配合後端串接資料
匯入模擬資料（10,000 筆）並進行效能測試與資料庫分區優化
本系統最終具備完整註冊登入、語言篩選、多語聊天室、一對一私訊、參與紀錄等功能，並成功整合使用者互動與聚會管理邏輯。透過這次期末專案，我深刻理解了資料庫從資料建模、正規化、查詢設計到系統整合的全流程，也首次實作了具備實用價值的交友服務原型。


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
