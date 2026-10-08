from celery import Celery


# Create the Celery application.
celery_app = Celery(
    "recruitment_api",

    # Redis is the broker:
    # FastAPI/Python sends task messages here.
    broker="redis://localhost:6379/0",

    # Redis also stores task results.
    backend="redis://localhost:6379/0",

    # IMPORTANT:
    # Tell the worker to import this module when it starts.
    #
    # Without this, the worker may start successfully
    # but not know about tasks defined in app/tasks.py.
    include=["app.tasks"],
)


celery_app.conf.update(
    task_track_started=True,
)