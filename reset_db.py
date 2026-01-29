import asyncio
from app.core.database import engine, Base
from app.models import User, Book, Transaction

async def reset():
    async with engine.begin() as conn:
        print("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Database reset complete.")

if __name__ == "__main__":
    asyncio.run(reset())
