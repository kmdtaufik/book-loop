from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    username: str
    password: str

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    username: str
    is_kyc_verified: bool
    points: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
