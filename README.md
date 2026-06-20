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

## 🔑 測試帳號資訊
如果您還沒有註冊帳號，系統建議的三種不同權限等級測試帳號（您可以在前端首頁的「註冊」面板自行建立）：

| 角色層級 | 權限說明 |
| :--- | :--- |
| **Admin** | 最高權限，可刪除所有資料、進入系統管理後台更改他人權限與檢視系統日誌。 |
| **User** | 一般使用者，可新增資料、編輯或刪除**自己**建立的資料。 |
| **Viewer**| 僅供檢視，可以看圖表與下載分析報表 (Excel/CSV)，無權新增或刪除。 |
