from schemas import Token, TokenData, UserBase, UserPublic, Users, SignUp, ProfileUpdate, TaskBase, TaskCreate, TaskPublic, Tasks, TaskUpdate
from typing import Annotated, Optional
from fastapi import Depends, FastAPI, HTTPException, Query, Form, status
from sqlmodel import Field, Session, SQLModel, create_engine, select
import contextlib 
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from jose import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from routers import user, task
from utility import create_db_and_tables

@contextlib.asynccontextmanager
async def lifespan(app):
    create_db_and_tables()
    yield 

app = FastAPI(lifespan=lifespan)

app.include_router(user.router)
app.include_router(task.router)