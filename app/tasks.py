from app.celery_app import celery_app
from app.database import SessionLocal
from app import models



# @celery_app.task tells Celery:
# "this function can be executed by a worker."
@celery_app.task
def add_numbers(a: int, b: int):
    return a + b

@celery_app.task
def application_submitted(application_id: int):
    # Celery runs in a separate worker process.
    #
    # That means it does NOT have access to the FastAPI request's
    # database session, so the task must create its own session.
    db = SessionLocal()

    try:
        # Fetch the application from PostgreSQL.
        application = (
            db.query(models.Application)
            .filter(models.Application.id == application_id)
            .first()
        )

        # The application may have been deleted before the worker
        # gets around to processing the task.
        if not application:
            return {
                "status": "failed",
                "reason": "application not found",
                "application_id": application_id,
            }

        # Fetch the job associated with this application.
        job = (
            db.query(models.Job)
            .filter(models.Job.id == application.job_id)
            .first()
        )

        if not job:
            return {
                "status": "failed",
                "reason": "job not found",
                "application_id": application_id,
            }

        # Fetch the candidate who submitted the application.
        candidate = (
            db.query(models.User)
            .filter(models.User.id == application.candidate_id)
            .first()
        )

        # Fetch the recruiter who created the job.
        recruiter = (
            db.query(models.User)
            .filter(models.User.id == job.created_by)
            .first()
        )

        # For now, our "notification" is just printed in the worker.
        #
        # Later, this exact section can be replaced with:
        # - email sending
        # - notification table insert
        # - websocket notification
        # - Slack integration
        # etc.
        print(
            f"""
            NEW APPLICATION RECEIVED

            Application ID: {application.id}
            Job: {job.title}
            Candidate: {candidate.username if candidate else "Unknown"}
            Recruiter: {recruiter.username if recruiter else "Unknown"}
            """
        )

        return {
            "status": "processed",
            "application_id": application.id,
            "job_id": job.id,
            "candidate_id": application.candidate_id,
            "recruiter_id": job.created_by,
        }

    finally:
        # Always close the database session.
        #
        # This is important because Celery workers are long-running
        # processes. Leaving sessions open can eventually exhaust
        # PostgreSQL connections.
        db.close()