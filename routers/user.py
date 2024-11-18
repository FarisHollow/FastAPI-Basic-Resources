from schemas import Token, TokenData, UserBase, UserPublic, Users, SignUp, ProfileUpdate, TaskBase, TaskCreate, TaskPublic, Tasks, TaskUpdate
from typing import Annotated, Optional
from fastapi import Depends, APIRouter, HTTPException, Query, Form, status
from sqlmodel import Field, Session, SQLModel, create_engine, select
import contextlib 
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from jose import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from utility import SessionDep, get_password_hash, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_active_user

router = APIRouter()

# User Signup
@router.post("/signup/", response_model=UserPublic)
async def signup(*,
    username: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    address: Optional[str] = Form(...),
    session: SessionDep
):
    hashed_password = get_password_hash(password)
    db_user = Users(username=username, email=email, hashed_password=hashed_password, address=address)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# User Login
@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer", msg="Success")

# View Profile
@router.get("/profile/me/", response_model=UserPublic)
async def view_profile(
    current_user: Annotated[UserPublic, Depends(get_current_active_user)],
):
    return current_user

#See all users
@router.get("/users/", response_model= list[UserPublic] )
async def get_all_users(*,
                        session : SessionDep, 
                        offset: int = 0,
                        limit: Annotated[int, Query(le=100)] = 100,
                        active: Annotated[UserPublic, Depends(get_current_active_user)]
                       ):
     users = session.exec(select(Users).offset(offset).limit(limit)).all()
     return users

#Update Profile
@router.put("/user/me", response_model=UserPublic)
async def update_profile(
    user_data: ProfileUpdate,
    session: SessionDep,
    current_user: Annotated[Users, Depends(get_current_active_user)]
):
    user_db = session.exec(select(Users).where(Users.id == current_user.id)).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="No profile found")
    update_user_encoded = jsonable_encoder(user_data)

    if 'password' in update_user_encoded and update_user_encoded['password']:
        update_user_encoded['hashed_password'] = get_password_hash(update_user_encoded.pop('password'))

    for key, value in update_user_encoded.items():
        if value is not None:
            setattr(user_db, key, value)

    session.add(user_db)  
    session.commit()  
    session.refresh(user_db)  

    return user_db

# Delete Account
@router.delete("/delete/account")
async def delete_acc(session: SessionDep, current_user: Annotated[Users, Depends(get_current_active_user)]):
    acc = session.get(Users, current_user.id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    session.delete(acc)
    session.commit()
    return {"Deleted": True}