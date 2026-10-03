from fastapi.testclient import TestClient

from app.main import app

from app.config import settings
from jose import jwt

from app import models
from tests.conftest import TestingSessionLocal


client = TestClient(app)

def test_company_create(recruiter_user):
    login_response = client.post(
            "/login",
            data={
                "username": recruiter_user.email,
                "password": "password123",
            },
        )
    
    token = login_response.json()["access_token"]

    response = client.post(
                "/companies",
                json={
                    "name": "MSFT Technologies",
                    "location": "FDB",
                    "website": "https://MSFT.com",
                    "description": "A technology company focused on shit.",
                },headers={
                "Authorization": f"Bearer {token}"
            },
            )
    
    assert response.status_code == 201

def test_duplicate_company(recruiter_user):
    login_response = client.post(
            "/login",
            data={
                "username": recruiter_user.email,
                "password": "password123",
            },
        )
    
    token = login_response.json()["access_token"]

    response = client.post(
                "/companies",
                json={
                    "name": "MSFT Technologies",
                    "location": "FDB",
                    "website": "https://MSFT.com",
                    "description": "A technology company focused on shit.",
                },headers={
                "Authorization": f"Bearer {token}"
            },
            )
    response2 = client.post(
                    "/companies",
                    json={
                        "name": "MSFT Technologies",
                        "location": "FDB",
                        "website": "https://MSFT.com",
                        "description": "A technology company focused on shit.",
                    },headers={
                    "Authorization": f"Bearer {token}"
                },
                )
    
    assert response2.status_code == 409


def test_candidate_cannot(candidate_user):
    login_response = client.post(
            "/login",
            data={
                "username": candidate_user.email,
                "password": "candidate123",
            },
        )
    
    token = login_response.json()["access_token"]

    response = client.post(
                "/companies",
                json={
                    "name": "MSFT Technologies",
                    "location": "FDB",
                    "website": "https://MSFT.com",
                    "description": "A technology company focused on shit.",
                },headers={
                "Authorization": f"Bearer {token}"
            },
            )
    
    assert response.status_code == 403


def test_recruiter_company_id_updates(recruiter_user):
    # 1. Login as recruiter
    login_response = client.post(
        "/login",
        data={
            "username": recruiter_user.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    # 2. Create company
    response = client.post(
        "/companies",
        json={
            "name": "Acme Technologies",
            "location": "Bengaluru",
            "website": "https://acme.com",
            "description": "Software company",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 201

    company_id = response.json()["id"]

    # 3. Query the test DB again
    db = TestingSessionLocal()

    recruiter = (
        db.query(models.User)
        .filter(models.User.id == recruiter_user.id)
        .first()
    )

    # 4. Check relationship
    assert recruiter.company_id == company_id

    db.close()