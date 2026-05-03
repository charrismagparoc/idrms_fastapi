"""
routers/dashboard_router.py
============================
Aggregated summary statistics for the dashboard. Used by:
  • Web:    Dashboard.jsx        → GET /api/dashboard/summary/
  • Mobile: DashboardScreen.js   → GET /api/dashboard/summary/

Endpoints
---------
GET /api/dashboard/summary/  – counts and aggregate stats for the main dashboard cards
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from collections import Counter

from database import get_db
import models
import schemas

router = APIRouter(prefix="/dashboard", tags=["Dashboard – Dashboard / DashboardScreen"])


@router.get("/summary/", response_model=schemas.DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Returns all the numbers needed to populate the stat cards on both the
    web Dashboard.jsx and mobile DashboardScreen.js.
    """
    total_incidents = db.query(func.count(models.Incident.id)).scalar()
    active_alerts   = db.query(func.count(models.Alert.id)).scalar()
    total_evac      = db.query(func.count(models.EvacuationCenter.id)).scalar()
    total_residents = db.query(func.count(models.Resident.id)).scalar()
    total_resources = db.query(func.count(models.Resource.id)).scalar()

    # Incidents grouped by severity
    severity_rows = (
        db.query(models.Incident.severity, func.count(models.Incident.id))
        .group_by(models.Incident.severity)
        .all()
    )
    incidents_by_severity = {row[0]: row[1] for row in severity_rows}

    # Evacuation occupancy rate across all centers
    evac_centers = db.query(models.EvacuationCenter).all()
    total_capacity   = sum(c.capacity for c in evac_centers) or 1
    total_occupancy  = sum(c.current_occupancy or c.occupancy or 0 for c in evac_centers)
    occupancy_rate   = round(total_occupancy / total_capacity * 100, 1)

    return schemas.DashboardSummary(
        total_incidents=total_incidents,
        active_alerts=active_alerts,
        total_evacuation_centers=total_evac,
        total_residents=total_residents,
        total_resources=total_resources,
        incidents_by_severity=incidents_by_severity,
        evacuation_occupancy_rate=occupancy_rate,
    )
