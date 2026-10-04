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

# recruiter cannot apply → 403
# admin cannot apply → 403
# no token → 401
# stored candidate_id, job_id, and default status are correct in the test DB