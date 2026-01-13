from pydantic import BaseModel
from typing import Optional

class BookCreate(BaseModel):
    isbn: str
    condition: str

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: Optional[str] = None
    condition: str
    image_url: Optional[str] = None
    status: str
    owner_id: int

    class Config:
        from_attributes = True
