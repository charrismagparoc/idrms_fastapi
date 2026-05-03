"""
routers/map_router.py
======================
Geo data for the map views. Used by:
  • Web:    MapPage.jsx    → GET /api/map/data/
  • Mobile: MapScreen.js   → GET /api/map/data/

Returns incidents, evacuation centers, and residents that have lat/lng
coordinates so the map can render markers without making multiple calls.

Endpoints
---------
GET /api/map/data/  – all geo-tagged records in one payload
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas

router = APIRouter(prefix="/map", tags=["Map – MapPage / MapScreen"])


@router.get("/data/", response_model=schemas.MapDataResponse)
def get_map_data(db: Session = Depends(get_db)):
    """
    Returns all incidents, evacuation centers, and residents that have
    coordinates. Both the web MapPage and mobile MapScreen call this to
    populate their map markers in a single request.
    """
    incidents = (
        db.query(models.Incident)
        .filter(models.Incident.lat.isnot(None), models.Incident.lng.isnot(None))
        .all()
    )
    centers = (
        db.query(models.EvacuationCenter)
        .filter(models.EvacuationCenter.lat.isnot(None), models.EvacuationCenter.lng.isnot(None))
        .all()
    )
    residents = (
        db.query(models.Resident)
        .filter(models.Resident.lat.isnot(None), models.Resident.lng.isnot(None))
        .all()
    )

    return schemas.MapDataResponse(
        incidents=incidents,
        evacuation_centers=centers,
        residents=residents,
    )
