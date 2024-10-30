# schemas.py
from pydantic import BaseModel

class UserBase(BaseModel):
    firstname: str
    lastname: str
    phone: str
    email: str
    password: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class OTPSendRequest(BaseModel):
    phone_number: str

class OTPLoginRequest(BaseModel):
    phone_number: str
    otp: str