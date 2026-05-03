"""
models.py
=========
SQLAlchemy ORM models for every table in the IDRMS database.
Each class maps 1-to-1 with a table and mirrors the fields used by
both the web app (useLocalData.js) and mobile app (useDB.js).
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, JSON, Text
)
from database import Base


# ---------------------------------------------------------------------------
# Users  (web: UsersPage / mobile: UsersScreen)
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, nullable=False)
    email      = Column(String, unique=True, index=True, nullable=False)
    password   = Column(String, nullable=False)          # plain-text for demo; hash in prod
    role       = Column(String, default="Staff")         # Admin | Staff | Viewer
    status     = Column(String, default="Active")        # Active | Inactive
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# Incidents  (web: IncidentsPage / mobile: IncidentsScreen)
# ---------------------------------------------------------------------------
class Incident(Base):
    __tablename__ = "incidents"

    id            = Column(Integer, primary_key=True, index=True)
    type          = Column(String, nullable=False)        # Flood | Fire | Landslide …
    zone          = Column(String, nullable=False)        # Zone 1 … Zone 10
    location      = Column(String, default="")
    severity      = Column(String, default="Medium")      # Low | Medium | High
    status        = Column(String, default="Pending")     # Pending | Ongoing | Resolved
    description   = Column(Text, default="")
    reporter      = Column(String, default="")
    source        = Column(String, default="web")         # web | mobile
    lat           = Column(Float, nullable=True)
    lng           = Column(Float, nullable=True)
    date_reported = Column(DateTime, default=datetime.utcnow)
    created_at    = Column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# Alerts  (web: AlertsPage / mobile: AlertsScreen)
# ---------------------------------------------------------------------------
class Alert(Base):
    __tablename__ = "alerts"

    id               = Column(Integer, primary_key=True, index=True)
    title            = Column(String, nullable=False)
    message          = Column(Text, default="")
    level            = Column(String, default="Advisory")   # Advisory | Warning | Danger
    zone             = Column(String, default="All Zones")
    recipients_count = Column(Integer, default=0)
    sent_by          = Column(String, default="System")
    created_at       = Column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# Evacuation Centers  (web: EvacuationPage / mobile: EvacuationScreen)
# ---------------------------------------------------------------------------
class EvacuationCenter(Base):
    __tablename__ = "evacuation_centers"

    id                   = Column(Integer, primary_key=True, index=True)
    name                 = Column(String, nullable=False)
    zone                 = Column(String, nullable=False)
    address              = Column(String, default="")
    capacity             = Column(Integer, default=100)
    current_occupancy    = Column(Integer, default=0)     # web uses current_occupancy
    occupancy            = Column(Integer, default=0)     # mobile uses occupancy
    status               = Column(String, default="Open") # Open | Full | Closed
    facilities_available = Column(JSON, default=list)
    contact_person       = Column(String, default="")
    contact_number       = Column(String, default="")
    contact              = Column(String, default="")     # mobile alias
    lat                  = Column(Float, nullable=True)
    lng                  = Column(Float, nullable=True)
    created_at           = Column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# Residents  (web: ResidentsPage / mobile: ResidentsScreen)
# ---------------------------------------------------------------------------
class Resident(Base):
    __tablename__ = "residents"

    id                 = Column(Integer, primary_key=True, index=True)
    name               = Column(String, nullable=False)
    zone               = Column(String, nullable=False)
    address            = Column(String, default="")
    household_members  = Column(Integer, default=1)
    contact            = Column(String, default="")
    evacuation_status  = Column(String, default="Safe")   # Safe | Evacuated | Missing
    vulnerability_tags = Column(JSON, default=list)       # ["Elderly","PWD", …]
    notes              = Column(Text, default="")
    added_by           = Column(String, default="System")
    source             = Column(String, default="web")
    lat                = Column(Float, nullable=True)
    lng                = Column(Float, nullable=True)
    added_at           = Column(DateTime, default=datetime.utcnow)
    updated_at         = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ---------------------------------------------------------------------------
# Resources  (web: ResourcesPage / mobile: ResourcesScreen)
# ---------------------------------------------------------------------------
class Resource(Base):
    __tablename__ = "resources"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, nullable=False)
    category   = Column(String, default="Other")          # Food | Medical | Equipment …
    quantity   = Column(Integer, default=0)
    available  = Column(Integer, default=0)
    unit       = Column(String, default="pcs")
    location   = Column(String, default="")
    status     = Column(String, default="Available")      # Available | Low | Depleted
    notes      = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# Activity Log  (web: ActivityLogPage / mobile: ActivityLogScreen)
# ---------------------------------------------------------------------------
class ActivityLog(Base):
    __tablename__ = "activity_log"

    id         = Column(Integer, primary_key=True, index=True)
    action     = Column(Text, nullable=False)
    type       = Column(String, default="System")   # Incident | Alert | Resident …
    user_name  = Column(String, default="System")
    urgent     = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
