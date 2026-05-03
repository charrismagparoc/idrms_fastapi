"""
routers/reports_router.py
==========================
Aggregate statistics for the reports view. Used by:
  • Web:    ReportsPage.jsx   → GET /api/reports/summary/
  • Mobile: ReportsScreen.js  → GET /api/reports/summary/

Endpoints
---------
GET /api/reports/summary/  – totals and breakdowns for the reports dashboard
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from collections import Counter

from database import get_db
import models
import schemas

router = APIRouter(prefix="/reports", tags=["Reports – ReportsPage / ReportsScreen"])


@router.get("/summary/", response_model=schemas.ReportSummary)
def get_report_summary(db: Session = Depends(get_db)):
    """
    All the aggregate numbers for the reports view. Both the web
    ReportsPage and mobile ReportsScreen call this endpoint.
    """
    # Incidents
    all_incidents = db.query(models.Incident).all()
    incidents_total    = len(all_incidents)
    incidents_resolved = sum(1 for i in all_incidents if i.status == "Resolved")
    incidents_pending  = sum(1 for i in all_incidents if i.status == "Pending")

    # Alerts
    alerts_total = db.query(func.count(models.Alert.id)).scalar()

    # Residents
    all_residents = db.query(models.Resident).all()
    residents_evacuated = sum(1 for r in all_residents if r.evacuation_status == "Evacuated")
    residents_safe      = sum(1 for r in all_residents if r.evacuation_status == "Safe")

    # Resources
    all_resources = db.query(models.Resource).all()
    resources_available = sum(1 for r in all_resources if r.status == "Available")
    resources_depleted  = sum(1 for r in all_resources if r.status == "Depleted")

    # Top 5 incident zones
    zone_counter = Counter(i.zone for i in all_incidents)
    top_zones = [{"zone": z, "count": c} for z, c in zone_counter.most_common(5)]

    # Top 5 incident types
    type_counter = Counter(i.type for i in all_incidents)
    top_types = [{"type": t, "count": c} for t, c in type_counter.most_common(5)]

    return schemas.ReportSummary(
        incidents_total=incidents_total,
        incidents_resolved=incidents_resolved,
        incidents_pending=incidents_pending,
        alerts_total=alerts_total,
        residents_evacuated=residents_evacuated,
        residents_safe=residents_safe,
        resources_available=resources_available,
        resources_depleted=resources_depleted,
        top_incident_zones=top_zones,
        top_incident_types=top_types,
    )
