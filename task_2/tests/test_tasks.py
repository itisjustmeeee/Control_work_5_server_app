from app.main import app, fake_db, task_id_counter
from fastapi.testclient import TestClient

client = TestClient(app)

def setup_function(function):
    fake_db.clear()
    task_id_counter = 1

HEADERS = {"X-User-Id": "10"}

def test_create_task_success():
    response = client.post(
        "/tasks",
        headers=HEADERS,
        json={
            "title": "Новая задача",
            "description": "Новое описание для задачи",
            "status": "todo",
            "priority": 4
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Новая задача"
    assert data["owner_id"] == 10

def test_create_task_short_title():
    response = client.post(
        "/tasks",
        headers=HEADERS,
        json={
            "title": "a",
            "description": "Аписание",
            "status": "todo",
            "priority": 4
        }
    )

    assert response.status_code == 422

def test_unauthorized_without_header():
    response = client.get("/tasks")

    assert response.status_code == 401

def test_user_sees_only_own_tasks():
    client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "Task user 10",
            "description": "",
            "status": "todo",
            "priority": 1
        }
    )

    client.post(
        "/tasks",
        headers={"X-User-Id": "20"},
        json={
            "title": "Task user 20",
            "description": "",
            "status": "done",
            "priority": 5
        }
    )

    response = client.get(
        "/tasks",
        headers={"X-User-Id": "10"}
    )

    data = response.json()

    assert len(data) == 1
    assert data[0]["owner_id"] == 10

def test_filter_by_status_and_priority():
    client.post(
        "/tasks",
        headers=HEADERS,
        json={
            "title": "Task 1",
            "description": "Lolz",
            "status": "todo",
            "priority": 2
        }
    )

    client.post(
        "/tasks",
        headers=HEADERS,
        json={
            "title": "Task 2",
            "description": "Lolz2",
            "status": "done",
            "priority": 5
        }
    )

    response = client.get(
        "/tasks?status=done&min_priority=4",
        headers=HEADERS
    )

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Task 2"

def test_update_status_success():
    create_response = client.post(
        "/tasks",
        headers=HEADERS,
        json={
            "title": "Task",
            "description": "heh",
            "status": "todo",
            "priority": 3
        }
    )

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}/status",
        headers=HEADERS,
        json={
            "status": "done"
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "done"

def test_get_foreign_task_404():
    create_response = client.post(
        "/tasks",
        headers={"X-User-Id": "20"},
        json={
            "title": "Foreign task",
            "description": "New description",
            "status": "todo",
            "priority": 2
        }
    )

    task_id = create_response.json()["id"]

    response = client.get(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "10"}
    )

    assert response.status_code == 404

def test_delete_task_success():
    create_response = client.post(
        "/tasks",
        headers=HEADERS,
        json={
            "title": "Delete us pls",
            "description": "new desc die",
            "status": "todo",
            "priority": 1
        }
    )

    task_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/tasks/{task_id}",
        headers=HEADERS
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/tasks/{task_id}",
        headers=HEADERS
    )

    assert get_response.status_code == 404

def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"