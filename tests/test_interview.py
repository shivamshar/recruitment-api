from fastapi.testclient import TestClient

from app.main import app

from app.config import settings
from jose import jwt

from app import models
from tests.conftest import TestingSessionLocal


client = TestClient(app)

def test_interview_creation(recruiter_user, test_job, create_application, candidate_user):
    #first we login as recruiter and call the application response
    login_response = client.post(
                        "/login",
                        data={
                            "username": recruiter_user.email,
                            "password": "password123",
                        },
                    )
                
            
    token = login_response.json()["access_token"]

    assert login_response.status_code == 200

    # Call the recruiter-facing applications endpoint.
    response = client.get(
        "/applications/recruiter",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    data = response.json()
    application = data[0]
    
    # Confirm this is the application created by our fixture.
    assert application["id"] == create_application["id"]

    #now we create an interview with this id

    interview_response=client.post("/interview", json = {
                                    "application_id": create_application["id"],
                                    "scheduled_at": "2026-10-10T15:30:00+05:30",
                                    "interview_type": "technical",
                                    "location_or_link": "https://meet.google.com/abc-defg-hij",
                                    "notes": "First technical interview. Focus on backend fundamentals and API design."
                                    }, headers={
                                                "Authorization": f"Bearer {token}"
                                            },)


    assert interview_response.status_code == 201


#candidate cannot schedule one

def test_interview_creation(recruiter_user, test_job, create_application, candidate_user):
    #first we login as recruiter and call the application response
    login_response = client.post(
                        "/login",
                        data={
                            "username": candidate_user.email,
                            "password": "candidate123",
                        },
                    )
                
            
    token = login_response.json()["access_token"]
    assert login_response.status_code == 200

    interview_response=client.post("/interview", json = {
                                        "application_id": create_application["id"],
                                        "scheduled_at": "2026-10-10T15:30:00+05:30",
                                        "interview_type": "technical",
                                        "location_or_link": "https://meet.google.com/abc-defg-hij",
                                        "notes": "First technical interview. Focus on backend fundamentals and API design."
                                        }, headers={
                                                    "Authorization": f"Bearer {token}"
                                                },)

    assert interview_response.status_code == 403


def test_interview_for_only_our_job( create_application,  recruiter_user2):
    login_response = client.post(
                            "/login",
                            data={
                                "username": recruiter_user2.email,
                                "password": "password123",
                            },
                        )
                    
                
    token = login_response.json()["access_token"]

    assert login_response.status_code == 200

    # Call the recruiter-facing applications endpoint.
    response = client.get(
        "/applications/recruiter",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    # assert response.status_code == 200
    # data = response.json()
    # application = data[0]
    
    # # Confirm this is the application created by our fixture.
    # assert application["id"] != create_application["id"]

    #now we create an interview with this id

    interview_response=client.post("/interview", json = {
                                    "application_id": create_application["id"],
                                    "scheduled_at": "2026-10-10T15:30:00+05:30",
                                    "interview_type": "technical",
                                    "location_or_link": "https://meet.google.com/abc-defg-hij",
                                    "notes": "First technical interview. Focus on backend fundamentals and API design."
                                    }, headers={
                                                "Authorization": f"Bearer {token}"
                                            },)


    assert interview_response.status_code == 403
    



