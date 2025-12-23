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
    isbn: Mapped[str] = mapped_column(String, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[BookStatus] = mapped_column(Enum(BookStatus), default=BookStatus.AVAILABLE)

    owner: Mapped["User"] = relationship(back_populates="books")
