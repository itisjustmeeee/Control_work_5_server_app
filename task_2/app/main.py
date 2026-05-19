from fastapi import FastAPI, status, HTTPException, Request, Header
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.model import TaskCreate, CustomExceptionModel, StatusUpdate
import os

app = FastAPI()

fake_db = []
task_id_counter = 1


class Task(TaskCreate):
    id: int
    owner_id: int


class CustomException(HTTPException):
    def __init__(self, status_code, detail: str, message: str):
        super().__init__(status_code=status_code, detail=detail)
        self.message = message

def get_user_id(x_user_id: str | None):
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id header required"
        )

    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid X-User-Id"
        )


@app.exception_handler(CustomException)
async def custom_exception_handler(
    request: Request,
    exc: CustomException
) -> JSONResponse:

    error = jsonable_encoder(
        CustomExceptionModel(
            status_code=exc.status_code,
            error_message=exc.message,
            error_details=exc.detail
        )
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error
    )

@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"model": Task},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": CustomExceptionModel
        },
    },
)
async def post_tasks(
    task: TaskCreate,
    x_user_id: str | None = Header(default=None)
):
    global task_id_counter

    user_id = get_user_id(x_user_id)

    new_task = {
        "id": task_id_counter,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "owner_id": user_id
    }

    fake_db.append(new_task)

    task_id_counter += 1

    return new_task

@app.get("/tasks")
async def get_tasks(
    status: str | None = None,
    min_priority: int | None = None,
    x_user_id: str | None = Header(default=None)
):
    user_id = get_user_id(x_user_id)

    result = [
        task for task in fake_db
        if task["owner_id"] == user_id
    ]

    if status:
        result = [
            task for task in result
            if task["status"] == status
        ]

    if min_priority is not None:
        result = [
            task for task in result
            if task["priority"] >= min_priority
        ]

    return result

@app.get("/tasks/{task_id}")
async def get_task_by_id(
    task_id: int,
    x_user_id: str | None = Header(default=None)
):
    user_id = get_user_id(x_user_id)

    for task in fake_db:
        if task["id"] == task_id and task["owner_id"] == user_id:
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )

@app.patch("/tasks/{task_id}/status")
async def patch_task(
    task_id: int,
    data: StatusUpdate,
    x_user_id: str | None = Header(default=None)
):
    user_id = get_user_id(x_user_id)

    for task in fake_db:
        if task["id"] == task_id and task["owner_id"] == user_id:
            task["status"] = data.status
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )

@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_task(
    task_id: int,
    x_user_id: str | None = Header(default=None)
):
    user_id = get_user_id(x_user_id)

    for i, task in enumerate(fake_db):
        if task["id"] == task_id and task["owner_id"] == user_id:
            fake_db.pop(i)
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "env": os.getenv("APP_ENV", "local")
    }