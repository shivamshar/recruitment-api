#it describes what our database should look like and provides a framework for alembic to make a table from 
from sqlalchemy import ForeignKey

import enum
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Integer,
    String,
)

from sqlalchemy.sql import func

from app.database import Base
from sqlalchemy import UniqueConstraint


class UserRole(str, enum.Enum):
    """
    Define the allowed user roles in our application.

    Using an Enum prevents arbitrary values like:

    "canddate"
    "Recruiter123"
    "whatever"

    Only these defined values should be allowed.
    """

    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    ADMIN = "admin"

class ApplicationStatus(str, enum.Enum):
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFERED = "offered"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class User(Base):
    """
    SQLAlchemy model representing the users table.

    One object of this class corresponds to one row
    inside PostgreSQL.
    """

    # Name of the actual PostgreSQL table.
    __tablename__ = "users"

    # Primary key uniquely identifies every user.
    #
    # PostgreSQL/SQLAlchemy will automatically generate
    # increasing integer IDs.
    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
    )

    # User's email address.
    #
    # unique=True:
    # Two users cannot have the same email.
    #
    # nullable=False:
    # Every user must have an email.
    #
    # index=True:
    # PostgreSQL creates an index, which makes searches
    # such as WHERE email = ... faster.
    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    # Public/display username.
    #
    # We also make this unique so two users cannot
    # register the same username.
    username = Column(
        String,
        unique=True,
        nullable=False,
    )

    # Store the HASHED password here.
    #
    # We will NEVER store plaintext passwords.
    #
    # We'll implement password hashing when we build auth.
    password = Column(
        String,
        nullable=False,
    )

    # Role determines what this user is allowed to do.
    #
    # Example:
    #
    # candidate -> apply to jobs
    # recruiter -> create/manage jobs
    # admin     -> broader administrative permissions
    role = Column(
        Enum(UserRole),
        nullable=False,

        # New users default to candidate unless
        # explicitly assigned another role.
        default=UserRole.CANDIDATE,
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=True,
    )

    # Record when the user account was created.
    created_at = Column(

        # timezone=True tells SQLAlchemy/PostgreSQL that
        # timestamps should carry timezone information.
        DateTime(timezone=True),

        # func.now() tells PostgreSQL itself to generate
        # the current timestamp.
        server_default=func.now(),
    )


class Company(Base):
    """
    SQLAlchemy model representing the users table.

    One object of this class corresponds to one row
    inside PostgreSQL.
    """

    # Name of the actual PostgreSQL table.
    __tablename__ = "companies"

    # Primary key uniquely identifies every user.
    #
    # PostgreSQL/SQLAlchemy will automatically generate
    # increasing integer IDs.
    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
    )

    # Name of company.
    #
    # unique=True:
    # Two users cannot have the same email.
    #
    # nullable=False:
    # Every user must have an email.
    #
    # index=True:
    # PostgreSQL creates an index, which makes searches
    # such as WHERE email = ... faster.
    name = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    # for the description of comapny that is optional
    description = Column(
        String,
        unique=False,
        nullable=True,
    )

    #website.
    website = Column(
        String,
        nullable=False,
    )

    #location 

    location = Column(
            String,
            nullable=False,
        )

    

    # Record when the company account account was created.
    created_at = Column(

        # timezone=True tells SQLAlchemy/PostgreSQL that
        # timestamps should carry timezone information.
        DateTime(timezone=True),

        # func.now() tells PostgreSQL itself to generate
        # the current timestamp.
        server_default=func.now(),
    )


class Job(Base):
    __tablename__ = "jobs"
    
        # Primary key uniquely identifies every user.
        #
        # PostgreSQL/SQLAlchemy will automatically generate
        # increasing integer IDs.
    
    # Gives us a list of all applications
    # submitted for this job.
    applications = relationship(
        "Application",
        back_populates="job",
    )


    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
    )

    # Name of company.
    #
    # unique=True:
    # Two users cannot have the same email.
    #
    # nullable=False:
    # Every user must have an email.
    #
    # index=True:
    # PostgreSQL creates an index, which makes searches
    # such as WHERE email = ... faster.
    title = Column(
        String,
        unique=False,
        nullable=False,
        index=True,
    )

    # for the description of comapny that is optional
    description = Column(
        String,
        unique=False,
        nullable=True,
    )

    #location 

    location = Column(
            String,
            nullable=False,
        )

    employment_type = Column(
                String,
                nullable=False,
            )

    company_id = Column(
                Integer,
                ForeignKey("companies.id"),
                nullable=False,
            )
    
    created_by = Column(
            Integer,
            ForeignKey("users.id"),
            nullable=False,
        )

    

    # Record when the company account account was created.
    created_at = Column(

        # timezone=True tells SQLAlchemy/PostgreSQL that
        # timestamps should carry timezone information.
        DateTime(timezone=True),

        # func.now() tells PostgreSQL itself to generate
        # the current timestamp.
        server_default=func.now(),
    )

    company = relationship(
    "Company",
    foreign_keys=[company_id],
)

    creator = relationship(
    "User",
    foreign_keys=[created_by],
)

class Application(Base):
    __tablename__ = "applications"

    # Gives us access to the actual Job object
    # associated with this application.
    job = relationship(
        "Job",
        back_populates="applications",
    )


    # Prevent the same candidate from applying
    # to the same job more than once.
    __table_args__ = (
    UniqueConstraint(
        "candidate_id",
        "job_id",
        name="uq_candidate_job_application",
    ),
)

    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
    )

    candidate_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False,
    )

    status = Column(
        Enum(ApplicationStatus),
        nullable=False,
        default=ApplicationStatus.APPLIED,
    )

    cover_letter = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )