from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import defaultdict
from typing import List

from database import get_db
import models
import schemas

router = APIRouter(prefix="/risk", tags=["Risk – RiskIntelligencePage / RiskScreen"])

SEVERITY_WEIGHT = {"High": 3, "Medium": 2, "Low": 1}


def _risk_level(score: float) -> str:
    if score >= 10:
        return "Critical"
    if score >= 6:
        return "High"
    if score >= 3:
        return "Medium"
    return "Low"


@router.get("/zones/", response_model=List[schemas.RiskZoneOut])
def get_zone_risk(db: Session = Depends(get_db)):
    """
    Scores every zone by summing severity weights of its active (non-resolved)
    incidents. Used by RiskIntelligencePage on the web and RiskScreen on mobile.
    """
    incidents = (
        db.query(models.Incident)
        .filter(models.Incident.status != "Resolved")
        .all()
    )

    zone_data: dict[str, dict] = defaultdict(lambda: {"count": 0, "score": 0.0})

    for inc in incidents:
        zone_data[inc.zone]["count"] += 1
        zone_data[inc.zone]["score"] += SEVERITY_WEIGHT.get(inc.severity, 1)

    result = []
    for zone, data in sorted(zone_data.items()):
        result.append(
            schemas.RiskZoneOut(
                zone=zone,
                incident_count=data["count"],
                severity_score=round(data["score"], 1),
                risk_level=_risk_level(data["score"]),
            )
        )

    # Sort highest risk first
    result.sort(key=lambda x: x.severity_score, reverse=True)
    return result
