from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

# DataRecordBase: 包含 title, value (float), category
class DataRecordBase(BaseModel):
    title: str
    value: float
    category: str

# DataRecordCreate: 繼承 DataRecordBase
class DataRecordCreate(DataRecordBase):
    pass

# DataRecordResponse: 繼承 DataRecordBase，加上 id, timestamp, creator_id
class DataRecordResponse(DataRecordBase):
    id: int
    timestamp: datetime
    creator_id: Optional[int] = None

    # 嚴格使用 Pydantic V2 的語法，取代舊版的 class Config: orm_mode = True
    model_config = ConfigDict(from_attributes=True)
