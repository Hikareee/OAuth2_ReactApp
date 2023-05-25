from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
import models 
from database import engine,SessionLocal
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date, datetime

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

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
    "TakumiFujiwara":{
        "username": "Takumi",
        "full_name": "Takumi Fujiwara",
        "email": "takumi@gmail.com",
        "hashed_password":"fakehashedsecret",
        "disabled": False
    },
    "SeeleVolerei": {
        "username": "Seele",
        "full_name": "Seele Volerei",
        "email": "seele@gmail.com",
        "hashed_password":"fakehashedsecret2",
        "disabled": True
    }
}

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

class Todos(BaseModel):
    title: str = None
    description: str = None
    created: datetime = None
    completed: bool = False

# test API Endpoint for index
# in this endpoint I also return the number of data

def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return User(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
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
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


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
    todo_model = db.query(models.Todo).filter(models.Todo.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {todo_id} : Iz not there"
        )
    
    if todo_model.title !=  None:
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
def delete_todo(todo_id:int, db:Session = Depends(get_db)):
    todo_model = db.query(models.Todo).filter(models.Todo.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(
            status_code = 404, 
            details=f"ID {todo_id}: Does not exist"
        )
    db.query(models.Todo).filter(models.Todo.id == todo_id).delete()
    db.commit() 
    