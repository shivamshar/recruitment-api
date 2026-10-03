from fastapi.testclient import TestClient

from app.main import app

from app.config import settings
from jose import jwt


client = TestClient(app)

#we test a successful login 

def test_successful_login():
    """
    A valid user should be created successfully.
    """

    client.post(
        "/users",
        json={
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "password123",
        },
    )

    response=client.post("/login", data = {"username": "testuser@example.com", "password": "password123"} )

    assert response.status_code == 200

    data = response.json()

    
    payload = jwt.decode(
    data["access_token"],
    settings.secret_key,
    algorithms=[settings.algorithm],
)
    print(payload)
    assert payload["user_id"]== 1
    assert "access_token" in data
    assert data["access_token"] is not None
    assert data["token_type"] == "bearer"
    


def test_wrong_login():
    """
    A valid user should be created successfully.
    """

    client.post(
        "/users",
        json={
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "password123",
        },
    )

    response=client.post("/login", data = {"username": "testuser@example.com", "password": "password"})    #we add the wrong password

    assert response.status_code == 401


def test_current_user():
    client.post(
            "/users",
            json={
                "email": "shivam@example.com",
                "username": "user123",
                "password": "password123",
            },
        )

    login_response=client.post("/login", data = {"username": "shivam@example.com", "password": "password123"})

    print(login_response.status_code)
    print(login_response.json())

    response = client.get(
        "/users/me",  headers={
        "Authorization": f"Bearer {login_response.json()["access_token"]}"
    },
)
    assert response.status_code == 200


def test_recruiter_login(recruiter_user):
    login_response = client.post(
        "/login",
        data={
            "username": recruiter_user.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/recruiter-only",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

