import datetime

from uuid import UUID

from pydantic import BaseModel


class TodoActionBase(BaseModel):
    title: str
    description: str
    deadline: datetime.datetime


class TodoActionItem(TodoActionBase):
    owner_id: int
    card_guid: UUID

    class Config:
        orm_mode = True


class TodoActionCreate(TodoActionBase):
    pass


class TodoListBase(BaseModel):
    title: str
    description: str | None = None


class TodoListCreate(TodoListBase):
    pass


class TodoListItem(TodoListBase):
    owner_id: int
    list_guid: UUID
    cards: list[TodoActionItem] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
