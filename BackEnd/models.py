from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base


class Todo(Base):
    __tablename__ = "Todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    created = Column(DateTime)
    description = Column(String)
    completion = Column(Boolean)


class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    fullname = Column(String)
    email = Column(String)
    token = Column(String)
    disabled = Column(Boolean)

