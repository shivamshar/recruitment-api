# Admin email: sharmashivam784@gmail.com
# Admin username: sharmashivam784
# Admin password: password

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, utils, oauth2
from app.database import get_db


router = APIRouter( prefix="/admin",
        tags=["Admin"],
)




@router.post(
    "/recruiters",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.userout,
)
def create_recruiter(
    recruiter: schemas.usercreate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(
        oauth2.required_role(models.UserRole.ADMIN)
    ),
):
    # Check duplicate email
    duplicate_email = (
        db.query(models.User)
        .filter(models.User.email == recruiter.email)
        .first()
    )

    if duplicate_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Check duplicate username
    duplicate_username = (
        db.query(models.User)
        .filter(models.User.username == recruiter.username)
        .first()
    )

    if duplicate_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Choose another username",
        )

    hashed_password = utils.hash_password(recruiter.password)

    new_recruiter = models.User(
        email=recruiter.email,
        username=recruiter.username,
        password=hashed_password,

        # Important difference from normal signup:
        role=models.UserRole.RECRUITER,
    )

    db.add(new_recruiter)
    db.commit()
    db.refresh(new_recruiter)

    return new_recruiter


@router.post(
    "/create_new_admin",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.userout,
)
def create_admin(
    admin: schemas.usercreate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(
        oauth2.required_role(models.UserRole.ADMIN)
    ),
):
    # Check duplicate email
    duplicate_email = (
        db.query(models.User)
        .filter(models.User.email == admin.email)
        .first()
    )

    if duplicate_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Check duplicate username
    duplicate_username = (
        db.query(models.User)
        .filter(models.User.username == admin.username)
        .first()
    )

    if duplicate_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Choose another username",
        )

    hashed_password = utils.hash_password(admin.password)

    new_admin = models.User(
        email=admin.email,
        username=admin.username,
        password=hashed_password,

        # Important difference from normal signup:
        role=models.UserRole.ADMIN,
    )

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return new_admin