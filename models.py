from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Uuid, DateTime
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class TodoList(Base):
    __tablename__ = "todoLists"

    id = Column(Integer, primary_key=True, index=True)
    list_guid = Column(Uuid, index=True, unique=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    description = Column(String, index=True)

    cards = relationship("TodoAction")


class TodoAction(Base):
    __tablename__ = "todoAction"

    id = Column(Integer, primary_key=True, index=True)
    list_guid = Column(Uuid, ForeignKey("todoLists.list_guid"), index=True)
    card_guid = Column(Uuid, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=False)
    description = Column(String, index=False)
    deadline = Column(DateTime, index=False)

