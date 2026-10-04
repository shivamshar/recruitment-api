from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, relationship

from app import models, schemas, utils, oauth2
from app.database import get_db
from typing import List


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


#route to get all the jobs that have been posted

@router.get(
    "/jobs/get_all",
    response_model=list[schemas.JobsOut],
)
def get_all_jobs(
    db: Session = Depends(get_db),
):
    # Fetch all Job rows from the database.
    jobs = db.query(models.Job).all()

    # Build the exact response shape expected by JobsOut.
    return [
        {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "location": job.location,
            "employment_type": job.employment_type,
            "company_id": job.company_id,
            "created_by": job.created_by,

            # These come from SQLAlchemy relationships,
            # not directly from the jobs table.
            "company_name": job.company.name,
            "recruiter_name": job.creator.username,
        }
        for job in jobs
    ]