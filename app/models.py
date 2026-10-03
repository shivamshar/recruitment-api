#it describes what our database should look like and provides a framework for alembic to make a table from 


import enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Integer,
    String,
)

from sqlalchemy.sql import func

from app.database import Base


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

    # Record when the user account was created.
    created_at = Column(

        # timezone=True tells SQLAlchemy/PostgreSQL that
        # timestamps should carry timezone information.
        DateTime(timezone=True),

        # func.now() tells PostgreSQL itself to generate
        # the current timestamp.
        server_default=func.now(),
    )