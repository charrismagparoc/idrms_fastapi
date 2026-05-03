from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas

router = APIRouter(
    prefix="/evacuation-centers",
    tags=["Evacuation Centers – EvacuationPage / EvacuationScreen"],
)


def _sync_occupancy(record: models.EvacuationCenter, data: dict):
    """Keep current_occupancy and occupancy in sync regardless of which field the client sent."""
    if "current_occupancy" in data and data["current_occupancy"] is not None:
        record.current_occupancy = data["current_occupancy"]
        record.occupancy = data["current_occupancy"]
    elif "occupancy" in data and data["occupancy"] is not None:
        record.occupancy = data["occupancy"]
        record.current_occupancy = data["occupancy"]

    if "contact_number" in data and data["contact_number"]:
        record.contact_number = data["contact_number"]
        record.contact = data["contact_number"]
    elif "contact" in data and data["contact"]:
        record.contact = data["contact"]
        record.contact_number = data["contact"]


@router.get("/", response_model=List[schemas.EvacuationCenterOut])
def list_evacuation_centers(db: Session = Depends(get_db)):
    return db.query(models.EvacuationCenter).order_by(models.EvacuationCenter.id).all()


@router.post("/", response_model=schemas.EvacuationCenterOut, status_code=201)
def create_evacuation_center(
    payload: schemas.EvacuationCenterInput,
    db: Session = Depends(get_db),
):
    data = payload.model_dump()
    record = models.EvacuationCenter(
        name=data["name"],
        zone=data["zone"],
        address=data.get("address", ""),
        capacity=data.get("capacity", 100),
        status=data.get("status", "Open"),
        facilities_available=data.get("facilities_available", []),
        lat=data.get("lat"),
        lng=data.get("lng"),
    )
    _sync_occupancy(record, data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{center_id}/", response_model=schemas.EvacuationCenterOut)
def get_evacuation_center(center_id: int, db: Session = Depends(get_db)):
    record = db.query(models.EvacuationCenter).filter(models.EvacuationCenter.id == center_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Evacuation center not found.")
    return record


@router.patch("/{center_id}/", response_model=schemas.EvacuationCenterOut)
def update_evacuation_center(
    center_id: int,
    payload: schemas.EvacuationCenterUpdateInput,
    db: Session = Depends(get_db),
):
    record = db.query(models.EvacuationCenter).filter(models.EvacuationCenter.id == center_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Evacuation center not found.")

    data = payload.model_dump(exclude_unset=True)

    # Apply simple fields
    for field in ("name", "zone", "address", "capacity", "status", "facilities_available", "lat", "lng"):
        if field in data and data[field] is not None:
            setattr(record, field, data[field])

    _sync_occupancy(record, data)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{center_id}/", status_code=204)
def delete_evacuation_center(center_id: int, db: Session = Depends(get_db)):
    record = db.query(models.EvacuationCenter).filter(models.EvacuationCenter.id == center_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Evacuation center not found.")
    db.delete(record)
    db.commit()
    return None
