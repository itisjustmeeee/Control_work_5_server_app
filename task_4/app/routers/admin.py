from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import require_admin, get_storage

router = APIRouter(
    prefix='/admin',
    tags=["admin"]
)

@router.get('/stats')
async def get_stats(admin=Depends(require_admin), storage=Depends(get_storage)):
    stats = {
        "todo": 0,
        "in_progress": 0,
        "done": 0
    }

    for task in storage["tasks"]:
        stats[task["status"]] += 1

    return {
        "total_tasks": len(storage["tasks"]),
        "by_status": stats
    }

@router.delete('/tasks/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_admin(task_id: int, admin=Depends(require_admin), storage=Depends(get_storage)):
    for i, task in enumerate(storage["tasks"]):
        if task["id"] == task_id:
            storage["tasks"].pop(i)
            return
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found")