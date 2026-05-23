from fastapi.testclient import TestClient
from app.main import app
from app.storage import storage


client = TestClient(app)

def setup_function():
    storage["tasks"].clear()
    storage["task_id_counter"] = 1

USER_HEADERS = {
    "X-User-Id": "10",
    "X-User-Role": "user"
}

ADMIN_HEADERS = {
    "X-User-Id": "1",
    "X-User-Role": "admin"
}

def test_users_me():
    response = client.get(
        '/users/me',
        headers=USER_HEADERS
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 10
    assert data["role"] == "user"

def test_unauthorized_without_user_id():
    response = client.get('/users/me')

    assert response.status_code == 401

def test_user_cannot_access_admin_stats():
    response = client.get('/admin/stats', headers=USER_HEADERS)

    assert response.status_code == 403

def test_admin_gets_stats():
    client.post('/tasks',
        headers=USER_HEADERS,
        json = {
            "title": "new_task",
            "description": "simple task for nothing",
            "status": "todo",
            "priority": 3
        }            
    )

    response = client.get('/admin/stats', headers=ADMIN_HEADERS)

    data = response.json()

    print(response.json())

    assert response.status_code == 200
    assert data["total_tasks"] == 1
    assert data["by_status"]["todo"] == 1

def test_user_cannot_delete_foreign_task():
    create_response = client.post('/tasks',
        headers = {
            "X-User-Id": "15",
            "X-User-Role": "user"
        },                       
        json = {
            "title": "new_task_for_other_user",
            "description": "simple task for nothing (not for you)",
            "status": "in_progress",
            "priority": 2
        }
    )

    task_id = create_response.json()["id"]

    response = client.delete(
        f"/tasks/{task_id}",
        headers=USER_HEADERS
    )

    assert response.status_code == 404

def test_admin_can_delete_foreign_tasks():
    create_response = client.post('/tasks', headers=USER_HEADERS,
        json = {
            "title": "new_task_for_admin_to_delete",
            "description": "simple task for admin but not for user",
            "status": "todo",
            "priority": 1
        }
    )

    task_id = create_response.json()["id"]

    response = client.delete(
        f'/admin/tasks/{task_id}',
        headers=ADMIN_HEADERS
    )

    assert response.status_code == 204

def test_openapi_tags():
    response = client.get('/openapi.json')

    data = response.json()

    tags = []

    for path in data["paths"].values():
        for method in path.values():
            tags.extend(method.get("tags", []))

    assert "tasks" in tags
    assert "users" in tags
    assert "admin" in tags