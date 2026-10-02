from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


# create_engine() creates SQLAlchemy's main connection
# interface to PostgreSQL.
#
# It does NOT necessarily create a permanent database
# connection immediately.
#
# SQLAlchemy manages connections through a connection pool.
engine = create_engine(
    settings.database_url
)


# SessionLocal is a session factory.
#
# Calling:
#
# db = SessionLocal()
#
# gives us a database session that can:
#
# - query rows
# - insert rows
# - update rows
# - delete rows
# - commit transactions
#
SessionLocal = sessionmaker(

    # We manually call db.commit().
    #
    # SQLAlchemy will not automatically commit every change.
    autocommit=False,

    # Prevent automatic flushing before every query.
    #
    # We still get normal SQLAlchemy behavior but retain
    # explicit control over the session.
    autoflush=False,

    # Connect these sessions to the engine defined above.
    bind=engine,
)


# Base is the parent class for all SQLAlchemy models.
#
# Example:
#
# class User(Base):
#     ...
#
# SQLAlchemy stores information about all tables/models
# inside Base.metadata.
#
# IMPORTANT:
# We create Base only ONCE in the application.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that creates one database session
    for a request and closes it afterward.
    """

    # Create a new database session.
    db = SessionLocal()

    try:

        # yield gives the database session to whatever
        # FastAPI endpoint requested it.
        #
        # Example:
        #
        # def create_user(db: Session = Depends(get_db)):
        #     ...
        yield db

    finally:

        # This always runs after the request finishes,
        # even if an exception occurred.
        #
        # Closing sessions prevents leaked database connections.
        db.close()