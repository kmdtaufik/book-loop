from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.book import Book
from app.models.transaction import Transaction, TransactionStatus
from app.schemas.user import UserCreate, Token, UserResponse, UserUpdate
from sqlalchemy import func

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = security.get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        username=user_in.username,
        password_hash=hashed_password,
        is_kyc_verified=False,
        points=0
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Determine if login is by email or username (assuming email for now based on schemas)
    # The OAuth2PasswordRequestForm has 'username' and 'password' fields.
    # We will treat 'username' field as email as per typical implementation or check against email column

    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()

    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

from app.models.book import Book, BookStatus
from app.models.transaction import Transaction, TransactionStatus
from app.schemas.user import UserCreate, Token, UserResponse, UserUpdate
from sqlalchemy import func

# ... imports ...

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Calculate Stats
    # Books Listed
    listed_res = await db.execute(select(func.count(Book.id)).where(Book.owner_id == current_user.id))
    current_user.books_listed = listed_res.scalar() or 0

    # Books Swapped (Received)
    swapped_res = await db.execute(select(func.count(Transaction.id)).where(
        (Transaction.receiver_id == current_user.id) & (Transaction.status == TransactionStatus.COMPLETED)
    ))
    current_user.books_swapped = swapped_res.scalar() or 0

    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_in: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    if user_in.email:
        # Check uniqueness
        result = await db.execute(select(User).where(User.email == user_in.email))
        existing_user = result.scalars().first()
        if existing_user and existing_user.id != current_user.id:
             raise HTTPException(status_code=400, detail="Email already taken")
        current_user.email = user_in.email

    if user_in.password:
        if not user_in.old_password:
             raise HTTPException(status_code=400, detail="Old password required to change password")
        if not security.verify_password(user_in.old_password, current_user.password_hash):
             raise HTTPException(status_code=400, detail="Incorrect old password")
        current_user.password_hash = security.get_password_hash(user_in.password)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    # Re-calculate stats for response consisteny
    listed_res = await db.execute(select(func.count(Book.id)).where(Book.owner_id == current_user.id))
    current_user.books_listed = listed_res.scalar() or 0
    swapped_res = await db.execute(select(func.count(Transaction.id)).where(
        (Transaction.receiver_id == current_user.id) & (Transaction.status == TransactionStatus.COMPLETED)
    ))
    current_user.books_swapped = swapped_res.scalar() or 0

    return current_user
