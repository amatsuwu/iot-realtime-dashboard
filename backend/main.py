import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.api.routers import auth, data, monitor, users, system
import logging

# 設定全域日誌，同時輸出到終端機與 system.log 檔案
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("system.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
from backend.services.simulator import generate_realtime_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 伺服器啟動時執行的動作
    print("🚀 啟動背景服務：即時資料模擬器...")
    # 把任務丟到背景執行，並且保留 reference 避免被垃圾回收機制清除
    simulator_task = asyncio.create_task(generate_realtime_data())
    
    yield # 交出控制權，讓 FastAPI 開始接受連線
    
    # 伺服器關閉時執行的動作
    print("🛑 正在停止背景服務...")
    simulator_task.cancel() # 取消背景任務

app = FastAPI(
    title="即時資料分析與監控系統 API",
    description="提供 RESTful API 與 WebSocket 連接",
    version="1.0.0",
    lifespan=lifespan
)

# 掛載認證路由，並加上統一路徑前綴
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(data.router, prefix="/api/v1/data")
app.include_router(monitor.router, prefix="/api/v1/monitor")
app.include_router(users.router, prefix="/api/v1/users")
app.include_router(system.router, prefix="/api/v1/system")

@app.get("/")
async def root():
    return {"message": "系統後端 API 正常運行中"}
