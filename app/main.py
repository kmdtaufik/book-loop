from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import engine, Base
from app.models import User, Book, Transaction
from app.api.routes import auth, transactions, books

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="BookLoop API", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(books.router)

@app.get("/")
async def root():
    return {"message": "Welcome to BookLoop API", "status": "active"}
