"""
routers/resources_router.py
============================
CRUD for relief resources (food, equipment, medical supplies). Used by:
  • Web:    ResourcesPage.jsx   → GET / POST / PATCH / DELETE /api/resources/
  • Mobile: ResourcesScreen.js  → same endpoints

Endpoints
---------
GET    /api/resources/       – list all resources
POST   /api/resources/       – add a resource
GET    /api/resources/{id}/  – single resource
PATCH  /api/resources/{id}/  – partial update
DELETE /api/resources/{id}/  – delete
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas

router = APIRouter(prefix="/resources", tags=["Resources – ResourcesPage / ResourcesScreen"])


@router.get("/", response_model=List[schemas.ResourceOut])
def list_resources(db: Session = Depends(get_db)):
    return db.query(models.Resource).order_by(models.Resource.name).all()


@router.post("/", response_model=schemas.ResourceOut, status_code=201)
def create_resource(payload: schemas.ResourceInput, db: Session = Depends(get_db)):
    record = models.Resource(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{resource_id}/", response_model=schemas.ResourceOut)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    record = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Resource not found.")
    return record


@router.patch("/{resource_id}/", response_model=schemas.ResourceOut)
def update_resource(
    resource_id: int,
    payload: schemas.ResourceUpdateInput,
    db: Session = Depends(get_db),
):
    record = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Resource not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{resource_id}/", status_code=204)
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    record = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Resource not found.")
    db.delete(record)
    db.commit()
    return None
