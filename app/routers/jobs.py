from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, relationship

from app import models, schemas, utils, oauth2
from app.database import get_db
from typing import List
import json
from app.redis_client import redis_client


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
    # This is the Redis key where we will store
    # the complete list of jobs.
    cache_key = "jobs:all"

    # First check Redis.
    # If this key exists, Redis will return a JSON string.
    cached_jobs = redis_client.get(cache_key)

    # If cached data exists, return it immediately.
    #
    # This means we completely skip the PostgreSQL query.
    if cached_jobs:
        print("CACHE HIT - returning jobs from Redis")
        return json.loads(cached_jobs)

    # If there is no cached data,
    # fetch all jobs from PostgreSQL.
    
    # If we reach here, Redis had no cached value.
    print("CACHE MISS - querying PostgreSQL")
    jobs = db.query(models.Job).all()

    # Build the exact response structure expected
    # by your JobsOut schema.
    jobs_data = [
        {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "location": job.location,
            "employment_type": job.employment_type,
            "company_id": job.company_id,
            "created_by": job.created_by,

            # These values come from SQLAlchemy relationships.
            "company_name": job.company.name,
            "recruiter_name": job.creator.username,
        }
        for job in jobs
    ]

    # Redis stores strings/bytes, not Python lists directly.
    #
    # json.dumps() converts jobs_data into a JSON string.
    #
    # ex=60 means the cache automatically expires
    # after 60 seconds.
    redis_client.set(
        cache_key,
        json.dumps(jobs_data),
        ex=60,
    )

    # Return the same data we just cached.
    return jobs_data