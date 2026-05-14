import pytest


@pytest.mark.anyio
async def test_register_user(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "securepass123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.anyio
async def test_register_duplicate_email(client, test_user):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": test_user.email, "password": "anotherpass"},
    )
    assert response.status_code == 409


@pytest.mark.anyio
async def test_register_invalid_email(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "securepass123"},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_register_short_password(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.com", "password": "123"},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_login_success(client, test_user):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_wrong_password(client, test_user):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "wrongpass"},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_login_nonexistent_user(client):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@example.com", "password": "whatever"},
    )
    assert response.status_code == 401
