import asyncio
from backend.db.database import engine
async def test():
    try:
        async with engine.begin() as conn:
            print('Connection successful!')
    except Exception as e:
        print(f"Error: {e}")
asyncio.run(test())
