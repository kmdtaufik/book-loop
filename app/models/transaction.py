import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Enum
from app.core.database import Base

class TransactionStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    SHIPPED = "SHIPPED"
    COMPLETED = "COMPLETED"

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    giver_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[TransactionStatus] = mapped_column(Enum(TransactionStatus), default=TransactionStatus.REQUESTED)
    tracking_number: Mapped[str | None] = mapped_column(String, nullable=True)

    book: Mapped["Book"] = relationship()
    giver: Mapped["User"] = relationship(foreign_keys=[giver_id])
    receiver: Mapped["User"] = relationship(foreign_keys=[receiver_id])
