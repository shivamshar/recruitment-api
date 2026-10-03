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
