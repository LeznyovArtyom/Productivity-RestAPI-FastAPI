from sqlmodel import SQLModel, Field, Relationship, Column
from typing import Optional, List
from datetime import datetime
from sqlalchemy.dialects.mysql import LONGBLOB


class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=45)
    
    users: List["User"] = Relationship(back_populates="role")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=45)
    login: str = Field(max_length=30, unique=True, index=True)
    password: str = Field(max_length=100)
    image: Optional[bytes] = Field(default=None, sa_column=Column(LONGBLOB()))
    role_id: Optional[int] = Field(default=None, foreign_key="role.id")
    
    role: Optional[Role] = Relationship(back_populates="users")
    tasks: List["Task"] = Relationship(back_populates="user", cascade_delete=True)


class Importance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=45)


class Status(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=45)


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    importance_id: Optional[int] = Field(default=None, foreign_key="importance.id")
    status_id: Optional[int] = Field(default=None, foreign_key="status.id")
    deadline: datetime
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    user: Optional[User] = Relationship(back_populates="tasks")
    importance: Optional[Importance] = Relationship()
    status: Optional[Status] = Relationship()
