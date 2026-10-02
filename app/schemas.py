from pydantic import BaseModel, ConfigDict, EmailStr, conint
from typing import Optional
from app.models import UserRole

class usercreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class userout(BaseModel):
    email: EmailStr
    username: str
    id: int
    role: UserRole

    model_config = ConfigDict(from_attributes=True)
