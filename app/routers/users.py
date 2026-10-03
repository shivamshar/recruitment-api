from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, utils, oauth2
from app.database import get_db, engine
from typing import List



router = APIRouter(
        tags=["Users"],
)

@router.post("/users", status_code=status.HTTP_201_CREATED, response_model= schemas.userout)
def Createuser(user: schemas.usercreate, db: Session= Depends(get_db)):
    # first we check if we have a duplicate username already registered
    duplicate_email=(db.query(models.User).filter(models.User.email==user.email).first())
    if duplicate_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    #now we check for username so we can give unique one to everyone

    duplicate_username=(db.query(models.User).filter(models.User.username==user.username).first())  
    if duplicate_username:
        raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Choose another username",
                )
      

    #now we hash the password
    hashed=utils.hash_password(user.password)
    user.password=hashed

    #now we create a new user object that is default by candidate

    new_user=models.User(email=user.email,
        username=user.username,
        password=hashed,
        role=models.UserRole.CANDIDATE)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



#get current user that is logged in
@router.get("/users/me", status_code=status.HTTP_200_OK, response_model=schemas.userout)
def get_current_user(db: Session=Depends(get_db), curr_user: models.User=Depends(oauth2.get_current_user)):
    return curr_user


@router.get("/recruiter-only")
def recruiter_only(
    current_user: models.User = Depends(
        oauth2.required_role(models.UserRole.RECRUITER)
    ),
):
    return {
        "message": "Recruiter access granted",
        "user_id": current_user.id,
    }