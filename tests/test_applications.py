from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

#candidate can apply to a valid job → 201

def test_application_creation(candidate_user, test_job):
    login_response = client.post(
                "/login",
                data={
                    "username": candidate_user.email,
                    "password": "candidate123",
                },
            )
        
    
    token = login_response.json()["access_token"]

    assert login_response.status_code == 200

    application_response =  client.post("/applications", json = { "job_id": test_job.id, "cover_letter": " this is just a test",},headers={
                "Authorization": f"Bearer {token}"
            },)

    assert application_response.status_code ==  201

# candidate cannot apply to the same job twice → 409
def test_application_duplication(candidate_user, test_job):
    login_response = client.post(
                "/login",
                data={
                    "username": candidate_user.email,
                    "password": "candidate123",
                },
            )
        
    
    token = login_response.json()["access_token"]

    assert login_response.status_code == 200

    application_response =  client.post("/applications", json = { "job_id": test_job.id, "cover_letter": " this is just a test",},headers={
                "Authorization": f"Bearer {token}"
            },)

    assert application_response.status_code ==  201

    application_response1 =  client.post("/applications", json = { "job_id": test_job.id, "cover_letter": " this is just a test",},headers={
                    "Authorization": f"Bearer {token}"
                },)
    assert application_response1.status_code ==  409
    

# invalid job_id → 404
def test_invalid_job_id(candidate_user, test_job):
    login_response = client.post(
                "/login",
                data={
                    "username": candidate_user.email,
                    "password": "candidate123",
                },
            )
        
    
    token = login_response.json()["access_token"]

    assert login_response.status_code == 200

    application_response =  client.post("/applications", json = { "job_id": test_job.id+1, "cover_letter": " this is just a test",},headers={
                "Authorization": f"Bearer {token}"
            },)

    assert application_response.status_code ==  404


def test_recruiter_cannot_apply(recruiter_user, test_job):
    login_response = client.post(
                "/login",
                data={
                    "username": recruiter_user.email,
                    "password": "password123",
                },
            )
        
    
    token = login_response.json()["access_token"]

    assert login_response.status_code == 200

    application_response =  client.post("/applications", json = { "job_id": test_job.id, "cover_letter": " this is just a test",},headers={
                "Authorization": f"Bearer {token}"
            },)

    assert application_response.status_code ==  403


def test_no_token(recruiter_user, test_job):
    login_response = client.post(
                "/login",
                data={
                    "username": recruiter_user.email,
                    "password": "password123",
                },
            )
        
    
    token = login_response.json()["access_token"]

    assert login_response.status_code == 200

    application_response =  client.post("/applications", json = { "job_id": test_job.id, "cover_letter": " this is just a test",},)

    assert application_response.status_code ==  401

#recruiter can fetch applications for jobs they created
def test_recruiter_fetch_application(recruiter_user, test_job, create_application, candidate_user):
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

    # The endpoint returns a list of applications.
    assert len(data) >= 1

    # Grab the first returned application.
    application = data[0]

    # Confirm this is the application created by our fixture.
    assert application["id"] == create_application["id"]

    # Confirm the candidate is correct.
    assert application["candidate_id"] == candidate_user.id

    # Confirm the job is correct.
    assert application["job_id"] == test_job.id

    # Confirm QoL fields are also returned correctly.
    assert application["candidate_name"] == candidate_user.username
    assert application["title"] == test_job.title



