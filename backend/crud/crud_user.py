from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from backend.db.models import User
from backend.schemas.user_schema import UserCreate
from backend.core.security import get_password_hash

# ==========================================
# Read: 查詢使用者
# ==========================================

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    透過使用者名稱查詢使用者。
    主要用於「登入驗證」以及「註冊時檢查帳號是否重複」。
    """
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    # scalar_one_or_none() 會回傳單一物件，若無結果則回傳 None
    return result.scalar_one_or_none()

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    透過 ID 查詢使用者。
    主要用於 Token 解碼後，確認該使用者是否還存在於資料庫中。
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# Create: 建立使用者 (註冊)

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """
    將 Pydantic 傳入的明文密碼進行雜湊後，建立並儲存使用者。
    """
    # 1. 呼叫 security.py 進行密碼雜湊
    hashed_password = get_password_hash(user.password)
    
    # 2. 建立 SQLAlchemy ORM 模型實例 (注意：我們存的是雜湊值，不是明文)
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role
    )
    
    # 3. 將物件加入 Session 並非同步提交
    db.add(db_user)
    await db.commit()
    
    # 4. 刷新物件，讓資料庫自動產生的欄位 (如 id, created_at) 反映到 db_user 上
    await db.refresh(db_user)
    
    return db_user

# ==========================================
# Update: 更新使用者
# ==========================================

async def update_user_role(db: AsyncSession, user_id: int, new_role: str) -> Optional[User]:
    """
    更新使用者的角色
    """
    user = await get_user(db, user_id)
    if user:
        user.role = new_role
        await db.commit()
        await db.refresh(user)
    return user

# ==========================================
# Read: 查詢所有使用者
# ==========================================
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    """
    取得使用者列表
    """
    stmt = select(User).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()