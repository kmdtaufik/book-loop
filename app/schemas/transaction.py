from datetime import datetime
from pydantic import BaseModel
from app.models.transaction import TransactionStatus

class TransactionBase(BaseModel):
    book_id: int
    offered_book_id: int | None = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    tracking_number: str | None = None

class TransactionResponse(BaseModel):
    id: int
    book_id: int
    offered_book_id: int | None
    giver_id: int
    receiver_id: int
    status: TransactionStatus
    tracking_number: str | None
    created_at: datetime

    # Optional: Include Book title/author strings if needed for simple display
    # For now, sticking to IDs to keep it simple, client can fetch book details or we can expand later

    class Config:
        from_attributes = True
