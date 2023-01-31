from datetime import datetime, timedelta
from typing import Type
from uuid import UUID
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import models
import schemas
import todoListRepository
from database import SessionLocal, engine
from jose import JWTError, jwt
from passlib.context import CryptContext

from schemas import Token, User, TokenData, UserCreate, TodoListCreate, TodoActionCreate
from userRepository import get_user, save_user

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
models.Base.metadata.create_all(bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)) -> User | bool:
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

#funkcja ktora tworzy jvt token - tekst ktory mowi jakie dane zostały zakodowane jaki algorytmem
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
        token_data = TokenData(email=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register")
async def register_user(form_data: UserCreate, db: Session = Depends(get_db)):
    user = get_user(db, form_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    save_user(form_data.email, get_password_hash(form_data.password), db)
    return {}


@app.get("/todoList/{id}", response_model=schemas.TodoListItem)
async def get_todo_list(id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    todo_list = todoListRepository.get_todo_list(db, id, user.id)
    if not todo_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found",
        )
    return todo_list

@app.post("/todoList", response_model=schemas.TodoListItem)
async def create_todo_list(todo_list: TodoListCreate, db: Session = Depends(get_db),
                           user: User = Depends(get_current_active_user)):
    return todoListRepository.create_todo_list(db, todo_list, user.id)


@app.get("/todoList", response_model=list[schemas.TodoListItem])
async def get_todo_lists(db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    return todoListRepository.list_todo_lists(db, user.id)

@app.get("/todoList/{list_id}/todoAction/{card_id}", response_model=schemas.TodoActionItem)
async def get_todo_card(list_id: UUID, card_id: UUID, db: Session = Depends(get_db),
                        user: User = Depends(get_current_active_user)):
    todo_list = todoListRepository.get_todo_list(db, list_id, user.id)
    if not todo_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found",
        )
    todo_action = todoListRepository.get_todo_action(db, list_id, card_id, user.id)
    if not todo_action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found",
        )
    return todo_action


@app.post("/todoList/{list_id}/todoAction/", response_model=schemas.TodoActionItem)
async def create_todo_card(list_id: UUID, todo_action: TodoActionCreate,
                           db: Session = Depends(get_db),
                           user: User = Depends(get_current_active_user)
                           ):
    todo_list = todoListRepository.get_todo_list(db, list_id, user.id)
    if not todo_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found",
        )
    return todoListRepository.create_todo_action(db, list_id, todo_action, user.id)


@app.delete("/todoList/{list_id}/todoAction/{card_id}")
async def delete_todo_action(list_id: UUID, card_id: UUID, db: Session = Depends(get_db),
                             user: User = Depends(get_current_active_user)):
    todo_card = todoListRepository.get_todo_action(db, list_id, card_id, user.id)
    todoListRepository.delete_todo_action(db, todo_card)
    return {}

@app.delete("/todoList/{list_id}")
async def delete_todo_list(list_id: UUID,db: Session = Depends(get_db),
                             user: User = Depends(get_current_active_user)):
    todo_list = todoListRepository.get_todo_list(db, list_id, user.id)
    todoListRepository.delete_todo_action(db, todo_list)
    return {}