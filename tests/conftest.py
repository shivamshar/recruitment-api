from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from app.database import Base
from app.main import app
from app.database import get_db
from app import models, utils


TEST_DATABASE_URL = "postgresql://shivam:password@localhost:5434/recruitment_test"


# Separate SQLAlchemy engine ONLY for tests
test_engine = create_engine(TEST_DATABASE_URL)


# Separate session factory ONLY for tests
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    """
    FastAPI will use this instead of the real get_db()
    whenever tests are running.
    """
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


# Replace the application's normal DB dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def clean_database():
    """
    Runs automatically before every test.

    Each test gets a fresh database so tests do not interfere
    with each other.
    """

    # Remove all tables and any data left by previous tests.
    Base.metadata.drop_all(bind=test_engine)

    # Recreate empty tables for the next test.
    Base.metadata.create_all(bind=test_engine)

    yield

@pytest.fixture()
def recruiter_user():
    db= TestingSessionLocal()
    recruiter = models.User(
    email="recruiter@test.com",
    username="recruiter1",
    password=utils.hash_password("password123"),
    role=models.UserRole.RECRUITER,
)

    db.add(recruiter)
    db.commit()
    db.refresh(recruiter)

    db.close()

    return recruiter


@pytest.fixture()
def admin_user():
    db= TestingSessionLocal()
    admin = models.User(
    email="admin@test.com",
    username="recruiter1",
    password=utils.hash_password("admin123"),
    role=models.UserRole.ADMIN,
)

    db.add(admin)
    db.commit()
    db.refresh(admin)

    db.close()

    return admin



@pytest.fixture()
def candidate_user():
    db= TestingSessionLocal()
    candidate = models.User(
    email="candidate@test.com",
    username="candidate",
    password=utils.hash_password("candidate123"),
    role=models.UserRole.CANDIDATE,
)

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    db.close()

    return candidate

@pytest.fixture
def test_job(recruiter_user):
    """
    Creates a company for the recruiter,
    then creates one job tied to that company.
    """

    db = TestingSessionLocal()

    # Create a company first because every job
    # must belong to a valid company.
    company = models.Company(
        name="Test Company",
        location="Delhi",
        website="https://testcompany.com",
        description="Company used for pytest fixtures",
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    # Associate the recruiter with this company.
    recruiter = (
        db.query(models.User)
        .filter(models.User.id == recruiter_user.id)
        .first()
    )

    recruiter.company_id = company.id
    db.commit()
    db.refresh(recruiter)

    # Create a job belonging to that company
    # and recruiter.
    job = models.Job(
        title="Backend Developer",
        description="Test job for application tests",
        location="Delhi",
        employment_type="Full-time",
        company_id=company.id,
        created_by=recruiter.id,
    )

    db.add(job)
    db.commit()
    db.refresh(job)
    db.close()

    return job


@pytest.fixture()
def create_application(candidate_user, recruiter_user, test_job):
    db = TestingSessionLocal()
    
    application = models.Application(
        candidate_id=candidate_user.id,
        job_id=test_job.id,
        cover_letter="Test application cover letter",

        # You can omit status if the model already defaults
        # to ApplicationStatus.APPLIED.
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    # Store values before closing the session.
    application_data = {
        "id": application.id,
        "candidate_id": application.candidate_id,
        "job_id": application.job_id,
        "status": application.status,
    }

    db.close()

    return application_data



