from typing import List, Annotated
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.book import Book, BookStatus
from app.schemas.book import BookCreate, BookResponse

router = APIRouter(prefix="/books", tags=["books"])

async def fetch_google_books_data(isbn: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}")
        if response.status_code != 200:
            return None
        data = response.json()
        if "totalItems" in data and data["totalItems"] == 0:
            return None

        # Get first result
        try:
             volume_info = data["items"][0]["volumeInfo"]
             title = volume_info.get("title", "Unknown Title")
             authors = volume_info.get("authors", ["Unknown Author"])
             author = ", ".join(authors)
             image_links = volume_info.get("imageLinks", {})
             image_url = image_links.get("thumbnail") or image_links.get("smallThumbnail")

             return {
                 "title": title,
                 "author": author,
                 "image_url": image_url
             }
        except (KeyError, IndexError):
            return None

@router.post("/", response_model=BookResponse)
async def create_book(
    book_in: BookCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Fetch data
    metadata = await fetch_google_books_data(book_in.isbn)
    if not metadata:
        raise HTTPException(status_code=404, detail="Book not found on Google Books")

    new_book = Book(
        title=metadata["title"],
        author=metadata["author"],
        isbn=book_in.isbn,
        condition=book_in.condition,
        image_url=metadata["image_url"],
        owner_id=current_user.id,
        status=BookStatus.AVAILABLE
    )
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    return new_book

@router.get("/", response_model=List[BookResponse])
async def read_books(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100
):
    result = await db.execute(select(Book).where(Book.status == BookStatus.AVAILABLE).offset(skip).limit(limit))
    return result.scalars().all()
