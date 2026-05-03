from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas

router = APIRouter(prefix="/incidents", tags=["Incidents - IncidentsPage / IncidentsScreen"])


@router.get("/", response_model=List[schemas.IncidentOut])
def list_incidents(db: Session = Depends(get_db)):
    
    return db.query(models.Incident).order_by(models.Incident.created_at.desc()).all()


@router.post("/", response_model=schemas.IncidentOut, status_code=201)
def create_incident(payload: schemas.IncidentInput, db: Session = Depends(get_db)):
    
    record = models.Incident(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{incident_id}/", response_model=schemas.IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    record = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Incident not found.")
    return record


@router.patch("/{incident_id}/", response_model=schemas.IncidentOut)
def update_incident(
    incident_id: int,
    payload: schemas.IncidentUpdateInput,
    db: Session = Depends(get_db),
):
    
    record = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Incident not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{incident_id}/", status_code=204)
def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    record = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Incident not found.")
    db.delete(record)
    db.commit()
    return None