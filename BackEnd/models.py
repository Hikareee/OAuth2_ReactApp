from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base

class Todo(Base):
    __tablename__ = "Todos"

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String)
    created = Column(DateTime)
    description = Column(String) 
    completion = Column(Boolean)
