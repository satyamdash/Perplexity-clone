# db/reset_db.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import inspect, text
from backend.dbclient import Base  # import all your models so metadata includes them
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL)

async def drop_user_table_and_check():
    print("🗑️ Dropping user table...")
    async with engine.begin() as conn:
        # Drop the user table specifically
        await conn.execute(text("DROP TABLE IF EXISTS \"user\" CASCADE"))
        print("✅ User table dropped successfully!")
    
    print("🔍 Checking database state...")
    async with engine.begin() as conn:
        # Use run_sync to run the synchronous inspect function
        inspector = await conn.run_sync(lambda sync_conn: inspect(sync_conn))
        tables = await conn.run_sync(lambda sync_conn: inspector.get_table_names())
        
        if not tables:
            print("✅ All tables have been deleted.")
        else:
            print("🧾 Existing tables:", tables)

if __name__ == "__main__":
    asyncio.run(drop_user_table_and_check())
