from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlmodel import Field, Session, SQLModel, Relationship

# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str
    msg: str

class TokenData(BaseModel):
    username: Optional[str] = None



# User Models
class UserBase(SQLModel):
    username: str = Field(index=True, nullable=False)
    email: EmailStr = Field(index=True, nullable=False)
    address: Optional[str] = Field(nullable=False)
   
   

class Users(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(nullable=False)
    disabled: bool = Field(default=False)
    tasks: List["Tasks"] = Relationship(back_populates= "user", cascade_delete=True)

class UserPublic(UserBase):
    id: int

class SignUp(UserBase):
    password: str

class ProfileUpdate(UserBase):
    username: str 
    email: EmailStr
    address: Optional[str] = None
    password: str

class Config:
    orm_mode = True  
    exclude = {'disabled'}


 
# Task Models
class TaskBase(SQLModel):
    title: str = Field(index=True)
    desc: Optional[str] = Field(default=None, index=True)
   

class Tasks(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    secret_name: str
    user_id: int = Field(default=None, foreign_key="users.id") 
    
    user: Optional[Users] = Relationship(back_populates="tasks")

class TaskPublic(TaskBase):
    id: int
    


class TaskCreate(TaskBase):
    secret_name: str

class TaskUpdate(TaskBase):
    title: Optional[str] = None
    desc: Optional[str] = None
    secret_name: Optional[str] = None   