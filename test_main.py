from fastapi.testclient import TestClient
from main import app
from utility import get_current_active_user, SessionDep
from datetime import timedelta
from schemas import Users
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, StaticPool, SQLModel, Session
from typing import Annotated
from fastapi import Depends

client = TestClient(app)

# Database setup
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(
    sqlite_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def drop_db_and_tables():
    SQLModel.metadata.drop_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

database = Annotated[Session, Depends(get_session)]
app.dependency_overrides[SessionDep] = database

def override_dependency():
    return Users(id=1, username="testuser", disabled=False)

app.dependency_overrides[get_current_active_user] = override_dependency

# Test setup and teardown
def setup_function():
    create_db_and_tables()

def teardown_function():
    drop_db_and_tables()

# Test cases
def test_read_task():
    # Create a task first
    task_data = {
        "title": "Sample Task",
        "desc": "Sample description",
        "secret_name": "Secret123",
    }
    client.post("/tasks/", json=task_data)  # Add a task before testing the GET endpoint

    # Test the /tasks/ endpoint
    response = client.get("/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0  # Ensure at least one task is returned
    assert data[0]["title"] == "Sample Task"


def test_create_task():
    request_data = {
        "title": "Test Task",
        "desc": "This is a test task description.",
        "secret_name": "TopSecret123"
    }
    response = client.post("/tasks", json=request_data)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Test Task",
        "desc": "This is a test task description."
    }
