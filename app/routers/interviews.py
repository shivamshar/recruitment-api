from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, utils, oauth2
from app.database import get_db
from typing import List


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


#router to get all possible interviews scheduled(just for quality of life)

@router.get("/interview/get_all", status_code=status.HTTP_200_OK, response_model=List[schemas.InterviewOut])
def get_all_interview(db: Session= Depends(get_db)):
    try:
        # cursor.execute(""" SELECT * FROM posts """)
        # posts = cursor.fetchall()
        interview = db.query(models.Interview).all()
        return interview

    except Exception as e:
        db.rollback()
        print("DATABASE ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/interview/{interview_id}", status_code= status.HTTP_200_OK, response_model= schemas.InterviewOut)
def get_specific_interview(interview_id: int, db: Session=Depends(get_db), current_user: models.User= Depends(oauth2.required_role(models.UserRole.RECRUITER))):

    #extract the interview

    interview= db.query(models.Interview).filter(models.Interview.id==interview_id).first()

    if interview is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail =  " the interview does not exist")

    if interview.created_by!= current_user.id:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail =  " you cannot access this interview")

    return interview


#fetch all the interviews for one application

router.get("/applications/{job_id}/interviews" , status_code= status.HTTP_200_OK, response_model= List[schemas.InterviewOut])
def get_alliinterviews_forajob(job_id: int, db: Session=Depends(get_db), current_user: models.User= Depends(oauth2.required_role(models.UserRole.RECRUITER))):
    
    #     The logic should be:
    # 1. Fetch the job.
    # 2. If the job does not exist → 404.
    # 3. Check job.created_by == current_user.id.
    # 4. If another recruiter owns it → 403.
    # 5. Fetch interviews whose applications belong to that job.
    # 6. Return a list of InterviewOut.
    
    job = (
        db.query(models.Job)
        .filter(models.Job.id == job_id)
        .first()
    )

    if job is None:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail =  " the job does not exist")

    if job.created_by!= current_user.id:
            raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail =  " you cannot access this feature")

    interviews = (
    db.query(models.Interview)
    .join(
        models.Application,
        models.Interview.application_id == models.Application.id
    )
    .filter(models.Application.job_id == job_id)
    .all()
)   

    return interviews





