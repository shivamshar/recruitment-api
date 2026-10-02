from fastapi import FastAPI

app=FastAPI(title='Recruitment API')

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
