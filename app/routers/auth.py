from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, utils
from app.database import get_db

from app.oauth2 import create_access_token


router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login")
def login(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user= (db.query(models.User).filter(models.User.email== credentials.username).first())   #we login using the email 

    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail = "Invalid credentials")

    if not utils.verify_password(credentials.password, user.password):
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail = "Invalid credentials")

    token =  create_access_token(data={"user_id": user.id})

    return {
    "access_token": token,
    "token_type": "bearer"
}
