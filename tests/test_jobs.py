from fastapi.testclient import TestClient

from app.main import app

from app.config import settings
from jose import jwt

from app import models
from tests.conftest import TestingSessionLocal


client = TestClient(app)

#first we create a recruiter and then give him a company and then test the job creation

def test_recruiter_with_company(recruiter_user):
    login_response = client.post(
                "/login",
                data={
                    "username": recruiter_user.email,
                    "password": "password123",
                },
            )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    company_response= client.post(
                "/companies",
                json={
                    "name": "AMZN Technologies",
                    "location": "US",
                    "website": "https://AMZN.com",
                    "description": "A technology company focused on shit.",
                },headers={
                "Authorization": f"Bearer {token}"
            },
            )

    assert company_response.status_code == 201
    
    response = client.post("/jobs", json={"title": "random bs",
                "description": "doing random  shit.",
                "location": "delhi",
                "employment_type": "part-time"},headers={
                                "Authorization": f"Bearer {token}"
                            }, )

    assert response.status_code==201

def test_recruiter_without_company_cannot_create_job(recruiter_user):
    login_response = client.post(
        "/login",
        data={
            "username": recruiter_user.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.post(
        "/jobs",
        json={
            "title": "Backend Developer",
            "description": "Build backend APIs.",
            "location": "Bengaluru",
            "employment_type": "Full-time",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 403

def test_candidate_cannot_create_job(candidate_user):
    login_response = client.post(
            "/login",
            data={
                "username": candidate_user.email,
                "password": "candidate123",
            },
        )
    
    token = login_response.json()["access_token"]
    response = client.post(
            "/jobs",
            json={
                "title": "Backend Developer",
                "description": "Build backend APIs.",
                "location": "Bengaluru",
                "employment_type": "Full-time",
            },
            headers={
                "Authorization": f"Bearer {token}"
            },
        )
    assert response.status_code == 403

def test_correct_company_id(recruiter_user):
    login_response = client.post(
            "/login",
            data={
                "username": recruiter_user.email,
                "password": "password123",
            },
        )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    company_response= client.post(
                "/companies",
                json={
                    "name": "AMZN Technologies",
                    "location": "US",
                    "website": "https://AMZN.com",
                    "description": "A technology company focused on shit.",
                },headers={
                "Authorization": f"Bearer {token}"
            },
            )

    assert company_response.status_code == 201

    company_id = company_response.json()["id"]
    
    response = client.post("/jobs", json={"title": "random bs",
                "description": "doing random  shit.",
                "location": "delhi",
                "employment_type": "part-time"},headers={
                                "Authorization": f"Bearer {token}"
                            }, )

    data=response.json()

    db = TestingSessionLocal()

    job = db.query(models.Job).first()

    assert job.company_id == company_id
    assert job.created_by == recruiter_user.id

    db.close()