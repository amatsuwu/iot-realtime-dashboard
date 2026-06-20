import csv
import io
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from backend.api.dependencies import get_db, get_current_user
from backend.db.models import User, RoleEnum, DataRecord
from backend.schemas.data_schema import DataRecordCreate, DataRecordResponse
from backend.crud import crud_data

router = APIRouter(tags=["Data Management"])

@router.post("/", response_model=DataRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_data(
    data_in: DataRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # 警衛室攔截：必須登入
):
    """
    新增一筆資料。系統會自動將資料綁定給當前登入的使用者 (creator_id)。
    """
    return await crud_data.create_data_record(db=db, obj_in=data_in, creator_id=current_user.id)

@router.get("/", response_model=List[DataRecordResponse])
async def read_data(
    skip: int = Query(0, ge=0, description="分頁起始點"),
    limit: int = Query(100, ge=1, le=1000, description="單次取得筆數限制"),
    category: Optional[str] = Query(None, description="依分類篩選"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    讀取資料列表 (支援分頁與篩選)。
    """
    records = await crud_data.get_data_records(
        db=db, skip=skip, limit=limit, category=category
    )
    return records

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    刪除特定資料。權限：僅限資料創建者本人，或系統管理員 (Admin)。
    """
    # 1. 先把資料找出來
    record = await crud_data.get_data_record(db=db, record_id=record_id)
    if not record:
        raise HTTPException(status_code=404, detail="找不到該筆資料")
        
    # 2. 權限審查！如果不是創建者，而且也不是 Admin，就拋出 403 越權錯誤
    if record.creator_id != current_user.id and current_user.role != RoleEnum.Admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="權限不足：您只能刪除自己創建的資料"
        )
        
    # 3. 審查通過，執行刪除
    await crud_data.delete_data_record(db=db, db_obj=record)

# ==========================================
# Batch Import: 批量導入資料 (CSV)
# ==========================================
@router.post("/batch-import", status_code=status.HTTP_201_CREATED)
async def batch_import_data(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    上傳 CSV 檔案進行批量資料導入。
    CSV 必須包含表頭：title, value, category。
    """
    # 1. 檢查副檔名防呆
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="格式錯誤：請上傳 .csv 檔案")

    # 2. 讀取並解碼檔案內容
    content = await file.read()
    try:
        decoded_content = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="編碼錯誤：請確保 CSV 檔案為 UTF-8 編碼")

    csv_reader = csv.DictReader(io.StringIO(decoded_content))
    records_to_create = []

    # 3. 逐行解析與驗證資料
    for row in csv_reader:
        try:
            # 建立 ORM 實例，並統一把這批資料綁定給上傳者
            record = DataRecord(
                title=row['title'],
                value=float(row['value']),
                category=row['category'],
                creator_id=current_user.id
            )
            records_to_create.append(record)
        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"CSV 缺少必要表頭欄位: {e}")
        except ValueError:
            raise HTTPException(status_code=400, detail="資料格式錯誤：value 必須是數字")

    # 4. 效能優化：使用 add_all 進行批次寫入，而不是跑迴圈一直 db.commit()
    if records_to_create:
        db.add_all(records_to_create)
        await db.commit()

    return {"message": f"成功匯入 {len(records_to_create)} 筆資料！"}
