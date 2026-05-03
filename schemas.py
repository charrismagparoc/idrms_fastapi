"""
schemas.py
==========
Pydantic models used for request body validation and response serialisation.
One Input + one Output class per resource, named after the screen that uses it.
"""

from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


# ---------------------------------------------------------------------------
# Auth  (Login / LoginScreen)
# ---------------------------------------------------------------------------

class LoginInput(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    status: str
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    user: UserOut


# ---------------------------------------------------------------------------
# Users  (UsersPage / UsersScreen)
# ---------------------------------------------------------------------------

class UserInput(BaseModel):
    name: str
    email: str
    password: str
    role: str = "Staff"
    status: str = "Active"

class UserUpdateInput(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None


# ---------------------------------------------------------------------------
# Incidents  (IncidentsPage / IncidentsScreen)
# ---------------------------------------------------------------------------

class IncidentInput(BaseModel):
    type: str
    zone: str
    location: str = ""
    severity: str = "Medium"
    status: str = "Pending"
    description: str = ""
    reporter: str = ""
    source: str = "web"
    lat: Optional[float] = None
    lng: Optional[float] = None

class IncidentUpdateInput(BaseModel):
    type: Optional[str] = None
    zone: Optional[str] = None
    location: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    reporter: Optional[str] = None
    source: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class IncidentOut(BaseModel):
    id: int
    type: str
    zone: str
    location: str
    severity: str
    status: str
    description: str
    reporter: str
    source: str
    lat: Optional[float]
    lng: Optional[float]
    date_reported: Optional[datetime]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Alerts  (AlertsPage / AlertsScreen)
# ---------------------------------------------------------------------------

class AlertInput(BaseModel):
    title: str
    message: str = ""
    level: str = "Advisory"
    zone: str = "All Zones"
    recipients_count: int = 0
    sent_by: str = "System"

class AlertOut(BaseModel):
    id: int
    title: str
    message: str
    level: str
    zone: str
    recipients_count: int
    sent_by: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Evacuation Centers  (EvacuationPage / EvacuationScreen)
# ---------------------------------------------------------------------------

class EvacuationCenterInput(BaseModel):
    name: str
    zone: str
    address: str = ""
    capacity: int = 100
    current_occupancy: int = 0
    occupancy: int = 0               # mobile alias
    status: str = "Open"
    facilities_available: List[str] = []
    contact_person: str = ""
    contact_number: str = ""
    contact: str = ""                # mobile alias
    lat: Optional[float] = None
    lng: Optional[float] = None

class EvacuationCenterUpdateInput(BaseModel):
    name: Optional[str] = None
    zone: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = None
    current_occupancy: Optional[int] = None
    occupancy: Optional[int] = None
    status: Optional[str] = None
    facilities_available: Optional[List[str]] = None
    contact_person: Optional[str] = None
    contact_number: Optional[str] = None
    contact: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class EvacuationCenterOut(BaseModel):
    id: int
    name: str
    zone: str
    address: str
    capacity: int
    current_occupancy: int
    occupancy: int
    status: str
    facilities_available: List[str]
    contact_person: str
    contact_number: str
    contact: str
    lat: Optional[float]
    lng: Optional[float]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Residents  (ResidentsPage / ResidentsScreen)
# ---------------------------------------------------------------------------

class ResidentInput(BaseModel):
    name: str
    zone: str
    address: str = ""
    household_members: int = 1
    contact: str = ""
    evacuation_status: str = "Safe"
    vulnerability_tags: List[str] = []
    notes: str = ""
    added_by: str = "System"
    source: str = "web"
    lat: Optional[float] = None
    lng: Optional[float] = None

class ResidentUpdateInput(BaseModel):
    name: Optional[str] = None
    zone: Optional[str] = None
    address: Optional[str] = None
    household_members: Optional[int] = None
    contact: Optional[str] = None
    evacuation_status: Optional[str] = None
    vulnerability_tags: Optional[List[str]] = None
    notes: Optional[str] = None

class ResidentOut(BaseModel):
    id: int
    name: str
    zone: str
    address: str
    household_members: int
    contact: str
    evacuation_status: str
    vulnerability_tags: List[str]
    notes: str
    added_by: str
    source: str
    lat: Optional[float]
    lng: Optional[float]
    added_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Resources  (ResourcesPage / ResourcesScreen)
# ---------------------------------------------------------------------------

class ResourceInput(BaseModel):
    name: str
    category: str = "Other"
    quantity: int = 0
    available: int = 0
    unit: str = "pcs"
    location: str = ""
    status: str = "Available"
    notes: str = ""

class ResourceUpdateInput(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    available: Optional[int] = None
    unit: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class ResourceOut(BaseModel):
    id: int
    name: str
    category: str
    quantity: int
    available: int
    unit: str
    location: str
    status: str
    notes: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Activity Log  (ActivityLogPage / ActivityLogScreen)
# ---------------------------------------------------------------------------

class ActivityLogInput(BaseModel):
    action: str
    type: str = "System"
    user_name: str = "System"
    urgent: bool = False

class ActivityLogOut(BaseModel):
    id: int
    action: str
    type: str
    user_name: str
    urgent: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Dashboard  (Dashboard / DashboardScreen) — summary response only
# ---------------------------------------------------------------------------

class DashboardSummary(BaseModel):
    total_incidents: int
    active_alerts: int
    total_evacuation_centers: int
    total_residents: int
    total_resources: int
    incidents_by_severity: dict
    evacuation_occupancy_rate: float


# ---------------------------------------------------------------------------
# Map  (MapPage / MapScreen) — combined geo data
# ---------------------------------------------------------------------------

class MapDataResponse(BaseModel):
    incidents: List[IncidentOut]
    evacuation_centers: List[EvacuationCenterOut]
    residents: List[ResidentOut]


# ---------------------------------------------------------------------------
# Reports  (ReportsPage / ReportsScreen) — aggregate stats
# ---------------------------------------------------------------------------

class ReportSummary(BaseModel):
    incidents_total: int
    incidents_resolved: int
    incidents_pending: int
    alerts_total: int
    residents_evacuated: int
    residents_safe: int
    resources_available: int
    resources_depleted: int
    top_incident_zones: List[dict]
    top_incident_types: List[dict]


# ---------------------------------------------------------------------------
# Risk  (RiskIntelligencePage / RiskScreen)
# ---------------------------------------------------------------------------

class RiskZoneOut(BaseModel):
    zone: str
    incident_count: int
    severity_score: float
    risk_level: str       # Low | Medium | High | Critical
