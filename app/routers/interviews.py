from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, utils, oauth2
from app.database import get_db


router = APIRouter(tags=["Company"])

@router.post("/interview", status_code= status.HTTP_201_CREATED, response_model= schemas.InterviewOut)
def create_interview(interview: schemas.InterviewCreate, db: Session=Depends(get_db), current_user: models.User= Depends(oauth2.required_role(models.UserRole.RECRUITER))):
    
    #first check that application exists for which interview is scheduled

    application= db.query(models.Application).filter(models.Application.id==interview.application_id).first()

    if not application:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = "application is not found")
    
    #now we check that the recruiter is the one that created that job
    job= db.query(models.Job).filter(models.Job.id==application.job_id).first()

    

    if not job.created_by==current_user.id:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail = "you did not create this job")

    new_interview= models.Interview(application_id= application.id, scheduled_at=interview.scheduled_at, interview_type= interview.interview_type, 
                                    location_or_link= interview.location_or_link, notes= interview.notes,
                                    created_by= current_user.id

                                      )


    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)

    return new_interview



    





# @router.post("/companies",status_code=status.HTTP_201_CREATED, response_model= schemas.CompanyOut)
# def recruiter_only(company: schemas.CompanyCreate, db: Session= Depends(get_db),current_user: models.User = Depends(oauth2.required_role(models.UserRole.RECRUITER))):
