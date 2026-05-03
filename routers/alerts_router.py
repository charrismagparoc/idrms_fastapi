from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas

router = APIRouter(prefix="/alerts", tags=["Alerts - AlertsPage / AlertsScreen"])


@router.get("/", response_model=List[schemas.AlertOut])
def list_alerts(db: Session = Depends(get_db)):
    return db.query(models.Alert).order_by(models.Alert.created_at.desc()).all()


@router.post("/", response_model=schemas.AlertOut, status_code=201)
def create_alert(payload: schemas.AlertInput, db: Session = Depends(get_db)):
    record = models.Alert(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{alert_id}/", response_model=schemas.AlertOut)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    record = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return record


@router.delete("/{alert_id}/", status_code=204)
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    record = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Alert not found.")
    db.delete(record)
    db.commit()
    return None