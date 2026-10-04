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

class JobsCreate(BaseModel):
    title: str
    description: str | None = None
    location: str
    employment_type: str

class JobsOut(BaseModel):
    id: int
    title: str
    description: str | None
    location: str
    employment_type: str
    company_id: int
    created_by: int
    company_name: str
    recruiter_name: str

    model_config = {
        "from_attributes": True
    }



class ApplicationCreate(BaseModel):
    # The candidate chooses which job they want to apply to.
    job_id: int

    # Optional message submitted with the application.
    cover_letter: str | None = None

class ApplicationOut(BaseModel):
    # Application's database ID.
    
    message: str

    id: int

    # Job this application belongs to.
    job_id: int

    # Candidate who submitted the application.
    candidate_id: int

    # Useful QoL fields pulled from related tables.
    candidate_name: str
    title: str
    location: str

    # Current application status.
    status: str

    # Optional cover letter submitted by the candidate.
    cover_letter: str | None = None
