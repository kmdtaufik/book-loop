from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated, List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.book import Book, BookStatus
from app.models.transaction import Transaction, TransactionStatus
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/request", response_model=TransactionResponse)
async def request_book(
    tx_in: TransactionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # 1. Fetch the target book
    result = await db.execute(select(Book).where(Book.id == tx_in.book_id))
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # 2. Validation
    if book.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot request your own book")
    if book.status != BookStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="Book is not available")

    # 3. Barter Logic vs Points Logic
    offered_book = None
    if tx_in.offered_book_id:
        # Fetch offered book
        res_offered = await db.execute(select(Book).where(Book.id == tx_in.offered_book_id))
        offered_book = res_offered.scalars().first()

        if not offered_book:
             raise HTTPException(status_code=404, detail="Offered book not found")
        if offered_book.owner_id != current_user.id:
             raise HTTPException(status_code=403, detail="You do not own the offered book")
        if offered_book.status != BookStatus.AVAILABLE:
             raise HTTPException(status_code=400, detail="Offered book is not available")

        # Mark offered book pending
        offered_book.status = BookStatus.PENDING

    else:
        # Point System Fallback (if no book offered)
        if current_user.points < 1:
            raise HTTPException(status_code=400, detail="Insufficient points. Offer a book or earn points.")
        current_user.points -= 1

    # Update target book status
    book.status = BookStatus.PENDING

    # Create Transaction
    new_tx = Transaction(
        book_id=book.id,
        offered_book_id=offered_book.id if offered_book else None,
        giver_id=book.owner_id,
        receiver_id=current_user.id,
        status=TransactionStatus.REQUESTED
    )

    db.add(new_tx)
    await db.commit()
    await db.refresh(new_tx)
    return new_tx

@router.get("/my-swaps", response_model=List[TransactionResponse])
async def get_my_swaps(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Fetch transactions where user is giver OR receiver
    result = await db.execute(
        select(Transaction)
        .where((Transaction.giver_id == current_user.id) | (Transaction.receiver_id == current_user.id))
        .order_by(Transaction.created_at.desc())
    )
    return result.scalars().all()

@router.put("/{tx_id}/accept", response_model=TransactionResponse)
async def accept_request(
    tx_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(Transaction).where(Transaction.id == tx_id))
    tx = result.scalars().first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if tx.giver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to accept this request")

    if tx.status != TransactionStatus.REQUESTED:
        raise HTTPException(status_code=400, detail="Transaction must be in REQUESTED state")

    tx.status = TransactionStatus.ACCEPTED
    await db.commit()
    await db.refresh(tx)
    return tx

@router.put("/{tx_id}/ship", response_model=TransactionResponse)
async def ship_book(
    tx_id: int,
    payload: TransactionUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(Transaction).where(Transaction.id == tx_id))
    tx = result.scalars().first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if tx.giver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to ship this book")

    if tx.status != TransactionStatus.ACCEPTED:
        raise HTTPException(status_code=400, detail="Transaction must be ACCEPTED before shipping")

    if not payload.tracking_number:
         raise HTTPException(status_code=400, detail="Tracking number required")

    tx.status = TransactionStatus.SHIPPED
    tx.tracking_number = payload.tracking_number
    await db.commit()
    await db.refresh(tx)
    return tx

@router.put("/{tx_id}/confirm", response_model=TransactionResponse)
async def confirm_receipt(
    tx_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Eager load giver and book because we need to update them
    # Actually explicit queries might be safer/clearer for updates
    result = await db.execute(select(Transaction).where(Transaction.id == tx_id))
    tx = result.scalars().first()
    if not tx:
         raise HTTPException(status_code=404, detail="Transaction not found")

    if tx.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to confirm this receipt")

    if tx.status != TransactionStatus.SHIPPED:
        raise HTTPException(status_code=400, detail="Transaction must be SHIPPED before confirming")

    # Logic:
    # 1. Update Tx -> COMPLETED
    tx.status = TransactionStatus.COMPLETED

    # 2. Update Book -> SWAPPED (so it doesn't show as pending forever, though technically it's gone)
    book_result = await db.execute(select(Book).where(Book.id == tx.book_id))
    book = book_result.scalars().first()
    if book:
        book.status = BookStatus.SWAPPED

    # 3. Add Point to Giver
    giver_result = await db.execute(select(User).where(User.id == tx.giver_id))
    giver = giver_result.scalars().first()
    if giver:
        giver.points += 1

    await db.commit()
    await db.refresh(tx)
    return tx
