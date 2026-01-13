import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Enum
from app.core.database import Base

class BookStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    PENDING = "PENDING"
    SWAPPED = "SWAPPED"

class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    author: Mapped[str] = mapped_column(String, index=True)
    isbn: Mapped[str] = mapped_column(String, index=True, nullable=True) # made clear it's nullable or not, plan said nullable=True but code had it not. Let's stick effectively to what it was but add image_url.
    condition: Mapped[str] = mapped_column(String, nullable=True)
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[BookStatus] = mapped_column(Enum(BookStatus), default=BookStatus.AVAILABLE)

    owner: Mapped["User"] = relationship(back_populates="books")
