import asyncio
from backend.db.database import engine
from sqlalchemy import text

async def test():
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text('SHOW TABLES;'))
            print('Tables:', [row[0] for row in result])
    except Exception as e:
        print(f'Error: {e}')

asyncio.run(test())
