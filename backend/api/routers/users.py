from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.api.dependencies import get_db, get_current_user
from backend.db.models import User, RoleEnum
from backend.schemas.user_schema import UserResponse, UserUpdateRole
from backend.crud import crud_user

router = APIRouter(tags=["User Management"])

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0, 
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取得所有使用者列表 (限 Admin 存取)
    """
    if current_user.role != RoleEnum.Admin:
        raise HTTPException(status_code=403, detail="權限不足：只有 Admin 才能查看使用者列表")
    return await crud_user.get_users(db, skip=skip, limit=limit)

@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role_update: UserUpdateRole,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新使用者角色 (限 Admin 存取)
    """
    if current_user.role != RoleEnum.Admin:
        raise HTTPException(status_code=403, detail="權限不足：只有 Admin 才能更改使用者權限")
    
    updated_user = await crud_user.update_user_role(db, user_id=user_id, new_role=role_update.role)
    if not updated_user:
        raise HTTPException(status_code=404, detail="找不到該使用者")
        
    return updated_user
