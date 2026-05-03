

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas

router = APIRouter(prefix="/activity-log", tags=["Activity Log – ActivityLogPage / ActivityLogScreen"])


@router.get("/", response_model=List[schemas.ActivityLogOut])
def list_activity_log(db: Session = Depends(get_db)):
    """Return up to 500 entries, newest first."""
    return (
        db.query(models.ActivityLog)
        .order_by(models.ActivityLog.created_at.desc())
        .limit(500)
        .all()
    )


@router.post("/", response_model=schemas.ActivityLogOut, status_code=201)
def create_log_entry(payload: schemas.ActivityLogInput, db: Session = Depends(get_db)):
    """
    Append a log entry. Both apps call this from their log() helper after
    every mutation (add, update, delete, login, logout).
    """
    record = models.ActivityLog(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
