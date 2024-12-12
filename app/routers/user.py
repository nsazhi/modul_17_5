from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated

from app.models import *
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete

from slugify import slugify

router = APIRouter(prefix="/user", tags=["user"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/")
async def all_users(db: DbSession):
    users = db.scalars(select(User)).all()
    return users


@router.get("/user_id")
async def user_by_id(db: DbSession, user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found")
    return user


@router.get("/user_id/tasks")
async def tasks_by_user_id(db: DbSession, user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found")
    tasks = db.scalars(select(Task).where(Task.user_id == user_id)).all()
    return tasks


@router.post("/create")
async def create_user(db: DbSession, create_user: CreateUser):
    if db.scalar(select(User).where(User.username == create_user.username)):
        raise HTTPException(status_code=409, detail="User already exists")

    db.execute(insert(User).values(username=create_user.username,
                                   firstname=create_user.firstname,
                                   lastname=create_user.lastname,
                                   age=create_user.age,
                                   slug=slugify(create_user.username)))
    db.commit()
    return {
        "status_code": status.HTTP_201_CREATED,
        "transaction": "Successful"
    }


@router.put("/update")
async def update_user(db: DbSession, user_id: int, update_user: UpdateUser):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found")

    db.execute(update(User).where(User.id == user_id).values(
        username=update_user.username,
        firstname=update_user.firstname,
        lastname=update_user.lastname,
        age=update_user.age,
        slug=slugify(update_user.username)))
    db.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "User update is successful!"
    }


@router.delete("/delete")
async def delete_user(db: DbSession, user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found")
    tasks = db.scalars(select(Task).where(Task.user_id == user_id)).all()
    tasks_id = [i.id for i in tasks]

    db.execute(delete(Task).where(Task.id.in_(tasks_id)))
    db.execute(delete(User).where(User.id == user_id))
    db.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "User delete is successful!"
    }
