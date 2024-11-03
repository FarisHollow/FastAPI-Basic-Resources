from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select
import contextlib 


@contextlib.asynccontextmanager
async def lifespan(app):
    create_db_and_tables()
    yield 

app = FastAPI(lifespan=lifespan)

class Tasks(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) 
    title: str = Field(index=True)
    desc: Optional[str] = Field(default=None, index=True)  
    secret_name: str



sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
     yield session


SessionDep = Annotated[Session, Depends(get_session)]





@app.post("/tasks/")
def create_task(task: Tasks, session: SessionDep) -> Tasks:
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/tasks/")
def read_tasks(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Tasks]:
    tasks = session.exec(select(Tasks).offset(offset).limit(limit)).all()
    return tasks



@app.get("/tasks/{task_id}")
def read_task(task_id: int, session: SessionDep) -> Tasks:
    task = session.get(Tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task



@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: SessionDep):
    task = session.get(Tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}






# class Task(BaseModel):

#     id: int
#     title: str
#     description: Optional[str] = None





# @app.post("/items/{id}")
# async def create_item(*, id: int = Path(gt = 0), task: Task):
#     tasks[id] = {
#         "task": task,
#         "description": task.description
#     }
#     return {"message": "Task added successfully", "task": {"id": id, "title": task.title, "description": task.description}}




# @app.get("/view_tasks")
# async def viewTasks():
#     return {"Tasks are ": tasks}


# @app.get("/view_task/{id}")
# async def viewTasks():
#     return {"Tasks are ": tasks}


