from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc
from typing import Optional, List, Dict, Any

from backend.db.models import DataRecord
from backend.schemas.data_schema import DataRecordCreate

# ==========================================
# Create: 新增資料
# ==========================================
async def create_data_record(db: AsyncSession, obj_in: DataRecordCreate, creator_id: int) -> DataRecord:
    """
    建立一筆新的資料紀錄，並強制綁定創建者的 ID。
    """
    db_obj = DataRecord(
        title=obj_in.title,
        value=obj_in.value,
        category=obj_in.category,
        creator_id=creator_id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

# ==========================================
# Read: 讀取資料 (支援分頁、篩選、排序)
# ==========================================
async def get_data_records(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    order_by_time_desc: bool = True
) -> List[DataRecord]:
    """
    取得多筆資料。支援條件篩選與分頁限制，防止一次拉取過多資料導致系統崩潰。
    """
    # 初始化查詢語句
    stmt = select(DataRecord)
    
    # 動態篩選：如果有傳入 category，就加入 where 條件
    if category:
        stmt = stmt.where(DataRecord.category == category)
        
    # 動態排序：預設以 timestamp 倒序排列 (最新的資料在最前面)
    if order_by_time_desc:
        stmt = stmt.order_by(desc(DataRecord.timestamp))
    else:
        stmt = stmt.order_by(asc(DataRecord.timestamp))
        
    # 分頁控制
    stmt = stmt.offset(skip).limit(limit)
    
    # 執行查詢並回傳 List
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_data_record(db: AsyncSession, record_id: int) -> Optional[DataRecord]:
    """
    根據 ID 取得單一筆資料。用於更新或刪除前的資料驗證。
    """
    stmt = select(DataRecord).where(DataRecord.id == record_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

# ==========================================
# Update: 更新資料
# ==========================================
async def update_data_record(db: AsyncSession, db_obj: DataRecord, update_data: Dict[str, Any]) -> DataRecord:
    """
    更新既有的資料。接收一個 dict，只更新有傳入的欄位。
    """
    for field, value in update_data.items():
        setattr(db_obj, field, value)
        
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

# ==========================================
# Delete: 刪除資料
# ==========================================
async def delete_data_record(db: AsyncSession, db_obj: DataRecord) -> None:
    """
    從資料庫中物理刪除該筆紀錄。
    """
    await db.delete(db_obj)
    await db.commit()
