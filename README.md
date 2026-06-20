# 📡 即時資料分析與監控系統 (IoT Real-time Dashboard)

## 📖 專案介紹
這是一個基於 FastAPI 與 Streamlit 建構的前後端分離「即時資料分析與監控系統」。本系統專為處理物聯網 (IoT) 設備所產生的大量即時串流資料而設計。系統具備非同步處理能力、完善的權限控管 (RBAC)、即時 WebSocket 推播，以及高效能的資料庫寫入機制。

## 🛠️ 技術棧說明

### 後端 (Backend)
- **核心框架**：FastAPI (高效能、支援非同步)
- **資料庫 ORM**：SQLAlchemy (AsyncEngine)
- **資料庫遷移**：Alembic
- **連線驅動**：asyncmy (非同步 MariaDB 驅動)
- **認證機制**：JWT (JSON Web Tokens), Passlib (Bcrypt 雜湊)
- **資料驗證**：Pydantic V2
- **即時通訊**：WebSockets

### 前端 (Frontend)
- **核心框架**：Streamlit
- **資料處理與視覺化**：Pandas, Streamlit Charts
- **網頁通訊**：Requests (RESTful API), WebSockets (即時串流)
- **檔案處理**：Openpyxl (Excel 匯出)

### 部署與環境 (DevOps)
- **資料庫**：MariaDB 11.7
- **容器化**：Docker & Docker Compose (包含多階段構建)

---

## 🚀 本地運行步驟 (Local Development)

### 1. 啟動 MariaDB 資料庫
本專案依賴 MariaDB，推薦先透過 Docker 啟動資料庫：
```bash
docker compose up -d db
```

### 2. 後端啟動 (FastAPI)
```bash
# 建立並啟動虛擬環境 (Mac/Linux)
python3 -m venv venv
source venv/bin/activate

# 安裝依賴套件
pip install -r requirements.txt

# 初始化資料庫 (執行 Alembic 遷移)
alembic upgrade head

# 啟動 FastAPI 伺服器
uvicorn backend.main:app --reload --port 8000
```

### 3. 前端啟動 (Streamlit)
請開啟一個**全新的終端機視窗**，啟動虛擬環境後執行：
```bash
source venv/bin/activate
streamlit run app.py
```

---

## 🐳 Docker 部署指令 (Production)

本專案支援完整的一鍵式容器化部署。在專案根目錄下，只需要一行指令即可啟動包含「前端、後端、資料庫」的完整叢集：

```bash
# 一鍵背景啟動所有服務 (包含建置 Image)
docker compose up -d --build

# 停止並移除所有容器
docker compose down
```
部署完成後：
* **前端網頁**：請瀏覽 `http://localhost:8501`
* **後端 API**：請瀏覽 `http://localhost:8000`

---

## 📚 API 文件連結
FastAPI 自動產生了符合 OpenAPI 標準的互動式文件。當後端伺服器啟動後，您可以透過以下連結存取：
- **Swagger UI**：[http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**：[http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🌐 線上即時互動區 (Live Demo)

為了讓審查人員或面試官能夠**最快速、最無痛地體驗本專案**，我們已經將系統完整部署至雲端環境。
如果您當前的環境沒有安裝 Docker 或是 Python 執行環境，您可以直接點擊下方連結，立即體驗本系統的完整功能（包含即時 WebSocket 資料推播與 MariaDB 資料庫互動）：

👉 **[點我進入線上即時監控儀表板](https://iot-realtime-dashboard.onrender.com)**

*(註：由於使用免費雲端資源，若長時間無人訪問，首次點擊進入可能需要等待約 50 秒以喚醒伺服器。)*

---

## 🔑 測試帳號資訊
為了方便面試官或審查人員快速體驗系統的完整功能，我們已經預先建立了一組最高權限的管理員帳號，您可以直接使用此帳號登入以省去註冊流程：

- **帳號**：`admin_test2`
- **密碼**：`my_secure_password123`
- **角色**：`Admin` (最高權限)

使用此帳號，您可以直接體驗：
1. **即時監控儀表板**的最新數據變化
2. **資料管理與分析**頁面，進行資料的篩選與下載
3. 進入**系統管理後台**，查看所有使用者、修改權限、檢視伺服器即時日誌與資料庫狀態

---

## 📝 如何註冊新帳號？
如果您想要親自體驗完整的註冊流程，或是測試不同角色（User/Viewer）的權限差異，您可以隨時建立新帳號：

1. 開啟前端網頁首頁 (`http://localhost:8501`)
2. 在登入介面中，點擊上方頁籤切換至 **「註冊」**
3. 輸入您想要的帳號名稱、密碼，並從下拉選單中選擇您想要的**角色** (`Admin`, `User`, 或 `Viewer`)
4. 點擊註冊按鈕，系統會自動將密碼加密 (Bcrypt) 並存入 MariaDB 資料庫中。註冊成功後即可立即登入！

---

## 🧪 架構與整合測試腳本 (Test Scripts)
為了展示系統開發過程中的「測試驅動 (Test-Driven)」思維，專案根目錄保留了各核心模組的獨立測試腳本。審查人員可以直接檢視或執行這些檔案，以驗證系統底層的穩固性：

1. **資料庫連線與建表**：`test_db.py`、`test_tables.py` (驗證 `asyncmy` 與 ORM)
2. **CRUD 寫入與密碼雜湊**：`test_create.py`
3. **JWT 授權與 RESTful API**：`test_api.py`
4. **WebSocket 廣播與非同步推播**：`test_websocket_client.py`

*(測試方式：確保虛擬環境啟動且資料庫運行中，於終端機直接執行 `python <腳本名稱>.py` 即可檢視測試輸出結果)*
