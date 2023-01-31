import uuid
from typing import List, Type
from uuid import UUID

from sqlalchemy.orm import Session

import models, schemas


def get_todo_list(db: Session, id: UUID, user_id: int):
    return db.query(models.TodoList).filter(
        models.TodoList.list_guid == id,
        models.TodoList.owner_id == user_id).first()


def list_todo_lists(db: Session, owner_id: id) -> list[Type[models.TodoList]]:
    return db.query(models.TodoList).filter(models.TodoList.owner_id == owner_id).all()


def create_todo_list(db: Session, todo_list: schemas.TodoListCreate, owner_id: id) -> models.TodoList:
    item = models.TodoList(
        owner_id=owner_id,
        title=todo_list.title,
        description=todo_list.description,
        list_guid=uuid.uuid4()
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def create_todo_action(db: Session,list_id: UUID, todo_action: schemas.TodoActionCreate, owner_id: id) -> models.TodoAction:
    item = models.TodoAction(
        list_guid=list_id,
        card_guid=uuid.uuid4(),
        owner_id=owner_id,
        title=todo_action.title,
        description=todo_action.description,
        deadline=todo_action.deadline
    )

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_todo_action(db: Session, list_id: UUID, card_id: UUID, owner_id: int):
    return db.query(models.TodoAction).filter(
        models.TodoAction.owner_id == owner_id,
        models.TodoAction.list_guid == list_id,
        models.TodoAction.card_guid == card_id).first()


def list_action_for_card(db: Session, list_guid: UUID, owner_id: int):
    return db.query(models.TodoAction).filter(
        models.TodoAction.owner_id == owner_id, models.TodoAction.list_guid == list_guid).all()


def delete_todo_action(db: Session, todo_card: models.TodoAction):
    db.delete(todo_card)
    db.commit()
    return

def delete_todo_list(db: Session, todo_list: models.TodoList):
    db.delete(todo_list)
    db.commit()
    return