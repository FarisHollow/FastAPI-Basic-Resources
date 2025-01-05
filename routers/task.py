   
from schemas import TaskCreate, TaskPublic, Tasks, TaskUpdate
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Query
from sqlmodel import  select
from utility import get_current_active_user, SessionDep

router= APIRouter()

# Task CRUD Endpoints
@router.post("/tasks/", response_model=TaskPublic)
async def create_task(task: TaskCreate, auth: Annotated[TaskPublic, Depends(get_current_active_user)], session: SessionDep):
    db_task = Tasks(**task.model_dump(), user_id=auth.id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.get("/tasks/", response_model=list[TaskPublic])
async def read_tasks(session: SessionDep, auth: Annotated[TaskPublic, Depends(get_current_active_user)], offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    tasks = session.exec(select(Tasks).where(Tasks.user_id == auth.id).offset(offset).limit(limit)).all()

    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks to show") 
           
    return  tasks

@router.get("/tasks/{task_id}", response_model=TaskPublic)
async def read_task(task_id: int, auth: Annotated[TaskPublic, Depends(get_current_active_user)], session: SessionDep):
    
    task = session.get(Tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/tasks/{task_id}", response_model=TaskPublic)
async def update_task(task_id: int, task: TaskUpdate, auth: Annotated[TaskPublic, Depends(get_current_active_user)], session: SessionDep):
    task_db = session.get(Tasks, task_id)
    if not task_db:
        raise HTTPException(status_code=404, detail="Task not found")
    task_data = task.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(task_db, key, value)
    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    return task_db

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, auth: Annotated[TaskPublic, Depends(get_current_active_user)], session: SessionDep):
    task = session.get(Tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}


@router.delete("/tasks/")
async def delete_all_task(auth: Annotated[TaskPublic, Depends(get_current_active_user)], session: SessionDep):
    task = session.exec(select(Tasks)).all()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    for n in task:
       session.delete(n)
       session.commit()
    return {"All tasks removed successfully": True}