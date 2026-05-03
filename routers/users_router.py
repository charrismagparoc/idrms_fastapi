"""
routers/users_router.py
========================
CRUD for system user accounts. Used by:
  • Web:    UsersPage.jsx   → GET / POST / PATCH / DELETE /api/users/
  • Mobile: UsersScreen.js  → same endpoints

Endpoints
---------
GET    /api/users/       – list all users
POST   /api/users/       – create user account
GET    /api/users/{id}/  – single user
PATCH  /api/users/{id}/  – partial update (name, role, status, password)
DELETE /api/users/{id}/  – delete
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas

router = APIRouter(prefix="/users", tags=["Users – UsersPage / UsersScreen"])


@router.get("/", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).order_by(models.User.name).all()


@router.post("/", response_model=schemas.UserOut, status_code=201)
def create_user(payload: schemas.UserInput, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="A user with that email already exists.")

    record = models.User(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{user_id}/", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    record = db.query(models.User).filter(models.User.id == user_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="User not found.")
    return record


@router.patch("/{user_id}/", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    payload: schemas.UserUpdateInput,
    db: Session = Depends(get_db),
):
    record = db.query(models.User).filter(models.User.id == user_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="User not found.")

    data = payload.model_dump(exclude_unset=True)

    # Only update password if it's a non-empty string
    if "password" in data and not (data["password"] and data["password"].strip()):
        del data["password"]

    for field, value in data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{user_id}/", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    record = db.query(models.User).filter(models.User.id == user_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="User not found.")
    db.delete(record)
    db.commit()
    return None
