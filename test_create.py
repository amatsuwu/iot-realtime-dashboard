import asyncio
from backend.db.database import AsyncSessionLocal
from backend.schemas.user_schema import UserCreate
from backend.crud.crud_user import create_user
import traceback

async def test_create():
    try:
        user_in = UserCreate(username="admin_test", role="Admin", password="my_secure_password123")
        async with AsyncSessionLocal() as db:
            new_user = await create_user(db, user_in)
            print("Success!", new_user.username)
    except Exception as e:
        print("Error!")
        traceback.print_exc()

asyncio.run(test_create())
