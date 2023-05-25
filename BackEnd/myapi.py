from fastapi import FastAPI, Depends, status, Security, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date, datetime
from typing import Union
from datetime import datetime, timedelta
from decouple import config

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm,SecurityScopes
from jose import JWTError, jwt

from passlib.context import CryptContext


from typing import Annotated

app = FastAPI()


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

todos = {
    1: {
        "title": "task 1",
        "description": "this is the first task",
        "created": "March 13, 2023 at 11:35:51 PM UTC+7",
        "completed": True
    },
    2: {
        "title": "task 2",
        "description": "this is the second task",
        "created": "March 13, 2023 at 11:35:51 PM UTC+7",
        "completed": False
    },
    3: {
        "title": "task 3",
        "description": "this is the third task",
        "created": "March 13, 2023 at 11:35:51 PM UTC+7",
        "completed": True
    }
}

fake_users_db = {
    "TakumiFujiwara": {
        "username": "Takumi",
        "full_name": "Takumi Fujiwara",
        "email": "takumi@gmail.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False
    },
    "SeeleVolerei": {
        "username": "Seele",
        "full_name": "Seele Volerei",
        "email": "seele@gmail.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True
    }
}


class User(BaseModel):
    username: str
    email: Union[str,None] = None
    full_name: Union[str,None] = None
    disabled: Union[str,None] = None


class UserInDB(User):
    hashed_password: str


class Todos(BaseModel):
    title: str = None
    description: str = None
    created: datetime = None
    completed: bool = False

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated= "auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# test API Endpoint for index
# in this endpoint I also return the number of data
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data:dict, expires_delta: Union[timedelta,None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else: expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(
        security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
    ):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )

    return {"access_token": user.username, "token_type": "bearer"}

@app.get("/status/")
async def read_system_status(current_user: Annotated[User, Depends(get_current_user)]):
    return {"status": "ok"}
    
@app.get("/")
def index():
    return {"n_todo": len(todos)}

# Endpoint GET todo lists


@app.get("/todos")
def get_todos(db: Session = Depends(get_db)):
    return db.query(models.Todo).all()

# Endpoint POST todo based on todo_ID


@app.post("/createTodo")
def post_todos(todo: Todos, db: Session = Depends(get_db)):
    if models.Todo.id in todos:
        return {"error": "student ID is EXIST"}
    todo_model = models.Todo()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.created = todo.created
    todo_model.completion = todo.completed

    db.add(todo_model)
    db.commit()

    return todo


@app.put("/{todo_id}")
def update_todo(todo_id: int, todo: Todos, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todo).filter(
        models.Todo.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {todo_id} : Iz not there"
        )

    if todo_model.title != None:
        todo_model.title = todo.title
    if todo_model.description != None:
        todo_model.description = todo.description
    if todo_model.created != None:
        todo_model.created = todo.created
    if todo_model.completion != None:
        todo_model.completion = todo.completed

    db.add(todo_model)
    db.commit()
    return todo


@app.delete("/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todo).filter(
        models.Todo.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(
            status_code=404,
            details=f"ID {todo_id}: Does not exist"
        )
    db.query(models.Todo).filter(models.Todo.id == todo_id).delete()
    db.commit()
