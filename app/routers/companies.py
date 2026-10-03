from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, utils, oauth2
from app.database import get_db


router = APIRouter(tags=["Company"])


@router.post("/companies",status_code=status.HTTP_201_CREATED, response_model= schemas.CompanyOut)
def recruiter_only(company: schemas.CompanyCreate, db: Session= Depends(get_db),current_user: models.User = Depends(oauth2.required_role(models.UserRole.RECRUITER))):
    duplicate_name=(db.query(models.Company).filter(models.Company.name==company.name).first())
    if duplicate_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="company already registered",
        )

    #prevents a recruiter belonging to one company to overrride his company
    if current_user.company_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Recruiter already belongs to a company",
        )

    new_company = models.Company(
        name=company.name,
        location=company.location,
        website=company.website,
        description=company.description,
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    current_user.company_id = new_company.id

    db.commit()
    db.refresh(current_user)

    return new_company
    






    