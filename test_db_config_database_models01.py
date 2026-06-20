import asyncio
from backend.db.database import engine
from backend.db.models import Base

async def init_tables():
    print("⏳ 準備連線至資料庫...")
    try:
        # 使用 begin() 來開啟一個 transaction
        async with engine.begin() as conn:
            print("🔗 連線成功！正在建立資料表...")
            # 由於 create_all 是同步操作，必須透過 run_sync 在非同步環境中執行
            await conn.run_sync(Base.metadata.create_all)
        print("✅ 資料表建立完成！")
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
    finally:
        # 關閉引擎釋放資源
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_tables())
