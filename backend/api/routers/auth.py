from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from backend.api.dependencies import get_db
from backend.schemas.user_schema import UserCreate, UserResponse
from backend.crud.crud_user import get_user_by_username, create_user
from backend.core.security import verify_password, create_access_token
from backend.core.config import settings

# 建立 Router 實例
router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    使用者註冊 API
    """
    # 檢查帳號是否已存在
    user = await get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="該使用者名稱已被註冊"
        )
    
    # 建立新使用者
    new_user = await create_user(db, user=user_in)
    return new_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    使用者登入 API (回傳 JWT Token)
    """
    # 1. 驗證使用者是否存在，以及密碼是否正確
    user = await get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. 核發 Access Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    # 3. 回傳標準 OAuth2 格式 (讓 Swagger UI 原生支援)，並夾帶使用者資訊給前端
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "username": user.username,
            "role": user.role.value
        }
    }
