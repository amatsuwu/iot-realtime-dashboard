from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.db.models import RoleEnum

# UserBase: 包含 username, role
class UserBase(BaseModel):
    username: str
    role: RoleEnum

# UserCreate: 繼承 UserBase，加上 password (字串，必填)
class UserCreate(UserBase):
    password: str

class UserUpdateRole(BaseModel):
    role: RoleEnum

# UserResponse: 繼承 UserBase，加上 id, created_at。絕對不可包含密碼。
class UserResponse(UserBase):
    id: int
    created_at: datetime

    # 嚴格使用 Pydantic V2 的語法，取代舊版的 class Config: orm_mode = True
    model_config = ConfigDict(from_attributes=True)
