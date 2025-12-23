from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import engine, Base
from app.models import User, Book, Transaction

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield

app = FastAPI(title="BookLoop API")

@app.get("/health")
async def root():
    return {"message": "Welcome to BookLoop API", "status": 200}
