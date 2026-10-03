from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from app.database import Base
from app.main import app
from app.database import get_db


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