from fastapi import FastAPI
from app.routers import users

app=FastAPI(title='Recruitment API')
app.include_router(users.router)

@app.get("/")
def root():
    """
    Simple health/test endpoint.

    We're using this only to verify that FastAPI
    is running correctly.
    """

    return {
        "message": "Recruitment API is running successfully"
    }

# Attach the users router to the FastAPI application.
#
# Without this line, FastAPI knows the router exists
# in Python but won't expose its endpoints.
app.include_router(users.router)
