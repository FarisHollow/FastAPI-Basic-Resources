from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query, Form
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select
import contextlib 
from pydantic import  EmailStr


@contextlib.asynccontextmanager
async def lifespan(app):
    create_db_and_tables()
    yield 

app = FastAPI(lifespan=lifespan)


class UserBase(SQLModel):
    username: str = Field(index=True, nullable=False)  
    email: EmailStr = Field(index=True, nullable=False) 
    address: Optional[str] = Field(nullable=False) 

class Users(UserBase, table= True):
    id: int = Field(default=None, primary_key=True)
    password: str = Field(nullable=False)  
    

class UserPublic(UserBase):
    id: int

class SignUp(UserBase):
    password: str

class Login(SQLModel):
    username: str
    password: str

#Task

class TaskBase(SQLModel):
    title: str = Field(index=True)
    desc: Optional[str] = Field(default=None, index=True)

class Tasks(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) 
    secret_name: str

class TaskPublic(TaskBase):
    id: int  

class TaskCreate(TaskBase):
    secret_name: str

class TaskUpdate(TaskBase):
    title: Optional[str]  = None
    desc: Optional[str] = None
    secret_name: Optional[str] = None


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


@app.post("/signup/", response_model=UserPublic)
async def signup(*,
    username: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    address: str = Form(...),
    session: SessionDep
):

    # db_user = Users.model_validate(username, email, password, address)
    db_user = Users(username=username, email=email, password=password, address=address)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"msg": "User registered", "user_id": db_user.id}

# @app.post("/signup/", response_model= UserPublic)
# async def signup(signup: Annotated[SignUp, Form()], session: SessionDep):
#     db_user = Users.model_validate(signup)
#     session.add(db_user)
#     session.commit()
#     session.refresh(db_user)
#     return db_user



@app.post("/login/")
async def login(login: Login, session: SessionDep):
    
    db_user = session.exec(select(Users).where(Users.username == login.username)).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not login.password != db_user.password:
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    return {"msg": "Login successful"}


@app.get("/users/", response_model=list[UserPublic])
def getUsers(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    users = session.exec(select(Users).offset(offset).limit(limit)).all()
    return users




#Task    

@app.post("/tasks/", response_model= TaskPublic)
def create_task(task: TaskCreate, session: SessionDep):

    db_task = Tasks.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@app.get("/tasks/", response_model=list[TaskPublic])
def read_tasks(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    tasks = session.exec(select(Tasks).offset(offset).limit(limit)).all()
    return tasks



@app.get("/tasks/{task_id}", response_model=TaskPublic)
def read_oneTask(task_id: int, session: SessionDep):
    task = session.get(Tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task






@app.patch("/tasks/{task_id}", response_model=TaskPublic)
def update_oneTask(task_id: int, task: TaskUpdate,  session: SessionDep):
    task_db = session.get(Tasks, task_id)
    if not task_db:
        raise HTTPException(status_code=404, detail="task not found")
    task_data = task.model_dump(exclude_unset=True)
    task_db.sqlmodel_update(task_data)
    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    return task_db




@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: SessionDep):
    task = session.get(Tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}

