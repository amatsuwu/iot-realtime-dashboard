from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import os

from backend.api.dependencies import get_db, get_current_user
from backend.db.models import User, RoleEnum
from backend.db.database import engine

router = APIRouter(tags=["System Monitoring"])

@router.get("/db-status")
async def get_db_status(current_user: User = Depends(get_current_user)):
    """
    取得資料庫連線池狀態 (限 Admin 存取)
    """
    if current_user.role != RoleEnum.Admin:
        raise HTTPException(status_code=403, detail="權限不足：只有 Admin 才能查看資料庫狀態")
    
    pool = engine.pool
    return {
        "size": pool.size(),
        "checkedin": pool.checkedin(),
        "checkedout": pool.checkedout(),
        "overflow": pool.overflow()
    }

@router.get("/logs")
async def get_system_logs(lines: int = 100, current_user: User = Depends(get_current_user)):
    """
    取得系統日誌 (限 Admin 存取)
    """
    if current_user.role != RoleEnum.Admin:
        raise HTTPException(status_code=403, detail="權限不足：只有 Admin 才能查看系統日誌")
        
    log_file_path = "system.log"
    if not os.path.exists(log_file_path):
        return {"logs": ["Log file not found. System is just starting or logging is not enabled."]}
        
    try:
        with open(log_file_path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            # 取最後 N 行
            return {"logs": all_lines[-lines:]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
