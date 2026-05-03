from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas

router = APIRouter(prefix="/residents", tags=["Residents - ResidentsPage / ResidentsScreen"])


@router.get("/", response_model=List[schemas.ResidentOut])
def list_residents(db: Session = Depends(get_db)):
    return db.query(models.Resident).order_by(models.Resident.added_at.desc()).all()


@router.post("/", response_model=schemas.ResidentOut, status_code=201)
def create_resident(payload: schemas.ResidentInput, db: Session = Depends(get_db)):
    record = models.Resident(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{resident_id}/", response_model=schemas.ResidentOut)
def get_resident(resident_id: int, db: Session = Depends(get_db)):
    record = db.query(models.Resident).filter(models.Resident.id == resident_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Resident not found.")
    return record


@router.patch("/{resident_id}/", response_model=schemas.ResidentOut)
def update_resident(
    resident_id: int,
    payload: schemas.ResidentUpdateInput,
    db: Session = Depends(get_db),
):
    record = db.query(models.Resident).filter(models.Resident.id == resident_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Resident not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{resident_id}/", status_code=204)
def delete_resident(resident_id: int, db: Session = Depends(get_db)):
    record = db.query(models.Resident).filter(models.Resident.id == resident_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Resident not found.")
    db.delete(record)
    db.commit()
    return None