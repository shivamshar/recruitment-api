from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, relationship

from app import models, schemas, utils, oauth2
from app.database import get_db


router = APIRouter(tags=["Jobs"])



@router.post("/jobs",status_code=status.HTTP_201_CREATED, response_model= schemas.JobsOut)
def create_job(job: schemas.JobsCreate, db: Session= Depends(get_db),current_user: models.User = Depends(oauth2.required_role(models.UserRole.RECRUITER))):
    #check recruiter has valid id
    if current_user.company_id is None:
        raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="recruiter has no valid company id",
                )

    new_job = models.Job(title=job.title,
        description=job.description,
        location=job.location,
        employment_type=job.employment_type,
        company_id=current_user.company_id,
        created_by=current_user.id,)

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return {
    "id": new_job.id,
    "title": new_job.title,
    "description": new_job.description,
    "location": new_job.location,
    "employment_type": new_job.employment_type,
    "company_id": new_job.company_id,
    "created_by": new_job.created_by,
    "company_name": new_job.company.name,
    "recruiter_name": new_job.creator.username,
}