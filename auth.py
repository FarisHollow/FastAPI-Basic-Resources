from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from jwt.exceptions import InvalidTokenError
from typing import Annotated, Optional

SECRET_KEY = "14daf2103a3b0f9f3d8ddb67c4690fe6637dc510d701da864eb48ffa109a6b5b"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_db = {
    "Faris" : {
        "username" : "Faris",
        "full_name" : "Mir Faris",
        "email" : "mirfaris79@gmail.com",
        "hashed_password" : "$2b$12$7ffpQkCr0paOXeX2A/fkqef7WSOIkSOvIvN/Ota0evBEot275Zvt6",
        "disabled": False

    }
}


class Token(BaseModel):
    access_token : str
    token_type: str
    msg: str

class TokenData(BaseModel):
    username : Optional[str] = None

class User(BaseModel):
    username : str
    full_name : Optional[str] = None
    email : Optional[str] = None
    disabled : bool

class UserInDB(User):
    hashed_password : str 

class UserSignup(BaseModel):
    username: str
    full_name: str
    email: str
    password: str    


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_data = db[username]
        return UserInDB(**user_data)
    
def authenticate_user(db, username : str, password: str):

    user =  get_user(db, username)

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
     
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/signup")
async def signup(user: UserSignup):
    if user.username in fake_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    hashed_password = get_password_hash(user.password)
    fake_db[user.username] = {
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "hashed_password": hashed_password,
        "disabled": False
    }
    return {"msg": "User created successfully"}
   


@app.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_db, form_data.username, form_data.password)
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


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user}]



pd = get_password_hash("1234")
print(pd)