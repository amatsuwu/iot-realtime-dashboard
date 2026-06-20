import asyncio
import random
from datetime import datetime, timezone
from backend.services.websocket import manager
from backend.db.database import AsyncSessionLocal
from backend.db.models import DataRecord

# 設定告警閾值
WARNING_THRESHOLD = 80.0
# 批次寫入的大小 (例如每累積 5 筆就寫入一次資料庫)
BATCH_SIZE = 5

async def generate_realtime_data():
    """
    即時資料模擬器 (Background Task)
    每秒生成一筆隨機資料，並透過 WebSocket 廣播給所有前端。
    並定時將累積的資料批次寫入 MariaDB，以供歷史查詢。
    """
    categories = ["Temperature", "Humidity", "System_Load"]
    batch_records = []
    
    while True:
        try:
            # 1. 隨機生成模擬數值
            current_category = random.choice(categories)
            current_value = round(random.uniform(20.0, 100.0), 2)
            
            # 2. 判斷是否觸發異常告警
            is_alert = current_value > WARNING_THRESHOLD
            
            # 3. 組合要推播的資料字典
            timestamp = datetime.now(timezone.utc)
            data_payload = {
                "title": f"Simulated_{current_category}",
                "value": current_value,
                "category": current_category,
                "timestamp": timestamp.isoformat(),
                "is_alert": is_alert
            }
            
            # 4. 呼叫電台總機，廣播給所有連線中的前端
            await manager.broadcast(data_payload)
            
            # 5. 準備要寫入資料庫的 ORM 物件
            # 系統生成的資料沒有特定 creator，因此依據 models.py 設定為 None
            record = DataRecord(
                title=data_payload["title"],
                value=data_payload["value"],
                category=data_payload["category"],
                timestamp=timestamp
            )
            batch_records.append(record)
            
            # 6. 批次寫入判斷：當累積滿 BATCH_SIZE 筆時，開啟短暫連線一次性寫入資料庫
            if len(batch_records) >= BATCH_SIZE:
                async with AsyncSessionLocal() as db:
                    db.add_all(batch_records)
                    await db.commit()
                # 寫入成功後清空暫存清單
                batch_records.clear()
            
            # 7. 休息 1 秒鐘後繼續下一次生成
            await asyncio.sleep(1)
            
        except asyncio.CancelledError:
            print("資料模擬器收到停止訊號，準備優雅關閉...")
            # 伺服器關閉前，如果緩衝區還有未寫入的資料，把握機會做最後一次寫入
            if batch_records:
                try:
                    async with AsyncSessionLocal() as db:
                        db.add_all(batch_records)
                        await db.commit()
                    print("✅ 關閉前已將剩餘資料批次寫入完畢")
                except Exception as e:
                    print(f"關閉前寫入失敗: {e}")
            break
        except Exception as e:
            print(f"模擬器發生未預期錯誤: {e}")
            await asyncio.sleep(5)
