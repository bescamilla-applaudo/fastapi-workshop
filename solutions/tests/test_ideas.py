import pytest


@pytest.mark.anyio
async def test_create_idea(client, auth_headers):
    response = await client.post(
        "/api/v1/ideas/",
        json={"title": "AI-powered todo", "description": "Uses GPT", "category": "tech"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "AI-powered todo"
    assert data["category"] == "tech"
    assert "id" in data


@pytest.mark.anyio
async def test_create_idea_without_auth(client):
    response = await client.post(
        "/api/v1/ideas/",
        json={"title": "No auth idea"},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_create_idea_empty_title(client, auth_headers):
    response = await client.post(
        "/api/v1/ideas/",
        json={"title": "", "description": "Missing title"},
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_list_ideas(client, auth_headers):
    await client.post(
        "/api/v1/ideas/",
        json={"title": "Idea 1"},
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/ideas/",
        json={"title": "Idea 2"},
        headers=auth_headers,
    )
    response = await client.get("/api/v1/ideas/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.anyio
async def test_list_ideas_filter_by_category(client, auth_headers):
    await client.post(
        "/api/v1/ideas/",
        json={"title": "Tech idea", "category": "tech"},
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/ideas/",
        json={"title": "Food idea", "category": "food"},
        headers=auth_headers,
    )
    response = await client.get(
        "/api/v1/ideas/?category=tech", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(idea["category"] == "tech" for idea in data)


@pytest.mark.anyio
async def test_get_idea(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/ideas/",
        json={"title": "My idea"},
        headers=auth_headers,
    )
    idea_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/ideas/{idea_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "My idea"


@pytest.mark.anyio
async def test_get_nonexistent_idea(client, auth_headers):
    response = await client.get("/api/v1/ideas/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.anyio
async def test_update_idea(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/ideas/",
        json={"title": "Original"},
        headers=auth_headers,
    )
    idea_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/v1/ideas/{idea_id}",
        json={"title": "Updated"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


@pytest.mark.anyio
async def test_update_partial(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/ideas/",
        json={"title": "Keep this", "description": "Change this"},
        headers=auth_headers,
    )
    idea_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/v1/ideas/{idea_id}",
        json={"description": "Changed!"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Keep this"
    assert data["description"] == "Changed!"


@pytest.mark.anyio
async def test_delete_idea(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/ideas/",
        json={"title": "To delete"},
        headers=auth_headers,
    )
    idea_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/ideas/{idea_id}", headers=auth_headers)
    assert response.status_code == 204

    get_resp = await client.get(f"/api/v1/ideas/{idea_id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.anyio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
