from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_user():
    """
    A valid user should be created successfully.
    """

    response = client.post(
        "/users",
        json={
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "testuser@example.com"
    assert data["username"] == "testuser"

    # Since role defaults to candidate in our backend,
    # we expect that value in the response.
    assert data["role"] == "candidate"

    # Very important:
    # our API must NEVER return the password.
    assert "password" not in data


def test_create_user_duplicate_email():
    client.post(
        "/users",
        json={
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "password123",
        },
    )

    response = client.post(
        "/users",
        json={
            "email": "duplicate@example.com",
            "username": "user2",
            "password": "password123",
        },
    )

    assert response.status_code == 409