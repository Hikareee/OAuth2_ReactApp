from fastapi import FastAPI, Depends
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


app = FastAPI() 


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


class Todos(BaseModel):
    title: str = None
    description: str = None
    created: datetime = None
    completed: bool = False

# test API Endpoint for index
# in this endpoint I also return the number of data


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
    