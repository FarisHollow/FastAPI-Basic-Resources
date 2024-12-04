from fastapi import FastAPI
import contextlib 
from routers import user, task
from utility import create_db_and_tables

@contextlib.asynccontextmanager
async def lifespan(app):
    create_db_and_tables()
    yield 

app = FastAPI(lifespan=lifespan)

app.include_router(user.router)
app.include_router(task.router)