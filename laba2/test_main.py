from fastapi.testclient import TestClient
from main import app
import time

client = TestClient(app)


def test_register_user():
    response = client.post(
        "/register/",
        json={"username": "newuser", "email": "newuser@example.com", "full_name": "New User",
              "hashed_password": "password123"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"


def test_register_user_duplicate():
    response = client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User",
              "hashed_password": "password123"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username or Email already registered"


def test_login_success():
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials():
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_get_users():
    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_users_me():
    response = client.post("/token", data={"username": "testuser", "password": "password123"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_get_users_me_unauthorized():
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_delete_user():
    response = client.delete("/users/testuser")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_delete_non_existent_user():
    response = client.delete("/users/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
