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

class CompanyCreate(BaseModel):
    name: str
    location: str | None = None
    website: str | None = None
    description: str | None = None

class CompanyOut(BaseModel):
    name: str
    id: int
    location: str
    website: str
    description: str

    model_config = ConfigDict(from_attributes=True)


