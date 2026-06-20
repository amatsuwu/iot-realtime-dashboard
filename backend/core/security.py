from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from typing import Optional
from backend.core.config import settings

# 設定密碼雜湊演算法 (使用 bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==========================================
# 密碼處理相關函式
# ==========================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    驗證使用者輸入的明文密碼是否與資料庫中的雜湊密碼相符。
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    將明文密碼進行雜湊處理。
    """
    return pwd_context.hash(password)

# ==========================================
# JWT Token 相關函式
# ==========================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    核發 JWT Access Token。
    傳入的 data 應包含 'sub' (通常為 username) 以及自訂欄位 (如 role)。
    """
    # 複製一份資料避免改動到原始 dict
    to_encode = data.copy()
    
    # 設定過期時間
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # 如果未指定，則使用 config 中的預設時間 (例如 30 分鐘)
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 將過期時間加入 Payload
    to_encode.update({"exp": expire})
    
    # 使用密鑰與指定的演算法進行編碼
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    解碼並驗證 JWT Token。
    如果過期或無效，返回 None。
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
