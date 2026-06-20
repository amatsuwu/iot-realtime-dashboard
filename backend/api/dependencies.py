from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from backend.db.database import AsyncSessionLocal
from backend.db.models import User
from backend.core.security import decode_access_token
from backend.crud.crud_user import get_user_by_username

# 建立 OAuth2 密碼模式實例，設定 Swagger UI 去哪裡拿 Token (對應我們寫的 auth.py 路由)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    提供每個 Request 獨立的資料庫 Session
    """
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    驗證 Token 並回傳目前登入的使用者物件 (User)。
    如果失敗則拋出 401 錯誤。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證身分或 Token 已過期",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. 解碼 Token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    # 2. 取出帳號名稱
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
        
    # 3. 去資料庫做最後的名冊確認
    user = await get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
        
    return user
