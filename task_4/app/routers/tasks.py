from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import TaskCreate, StatusUpdate
from app.dependencies import get_current_user, get_storage

router = APIRouter(
    prefix='/tasks',
    tags=["tasks"]
)

@router.post('')
async def create_task(task: TaskCreate, user=Depends(get_current_user), storage=Depends(get_storage)):
    new_task = {
        "id": storage["task_id_counter"],
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "owner_id": user["id"]
    }

    storage["tasks"].append(new_task)
    storage["task_id_counter"] += 1

    return new_task

@router.get('')
async def get_tasks(user=Depends(get_current_user), storage=Depends(get_storage)):
    return [
        task for task in storage["tasks"] if task["owner_id"] == user["id"]
    ]

@router.get('/{task_id}')
async def get_task(task_id: int, user=Depends(get_current_user), storage=Depends(get_storage)):
    for task in storage["tasks"]:
        if (task["id"] == task_id and task["owner_id"] == user["id"]):
            return task
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found")

@router.patch('/{task_id}/status')
async def update_status(task_id: int, data: StatusUpdate, user=Depends(get_current_user), storage=Depends(get_storage)):
    for task in storage["tasks"]:
        if (task["id"] == task_id and task["owner_id"] == user["id"]):
            task["status"] = data.status
            return task
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found")

@router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, user=Depends(get_current_user), storage=Depends(get_storage)):
    for i, task in enumerate(storage["tasks"]):
        if (task["id"] == task_id and task["owner_id"] == user["id"]):
            storage["tasks"].pop(i)
            return
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found")
