from pydantic import BaseModel, Field
from typing import Literal

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str | None = None
    status: Literal["todo", "in_progress", "done"]
    priority: int = Field(..., ge=1, le=3)

class Task(TaskCreate):
    id: int
    owner_id: int

class StatusUpdate(BaseModel):
    status: Literal["todo", "in_progress", "done"]