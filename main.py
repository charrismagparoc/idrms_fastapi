"""
IDRMS FastAPI Backend
=====================
Incident and Disaster Risk Management System — Barangay Kauswagan
Flood Risk Prediction Using Mendeley Flood Dataset

Entry point. Connects all routers including the ML prediction router.

Run with:  uvicorn main:app --reload --host 0.0.0.0 --port 8000
Docs at:   http://localhost:8000/docs

IMPORTANT: Before running for the first time, train the ML models:
    python ml/train_model.py
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_tables
from routers import (
    auth_router,
    incidents_router,
    alerts_router,
    evacuation_centers_router,
    residents_router,
    resources_router,
    users_router,
    activity_log_router,
    dashboard_router,
    reports_router,
    map_router,
    risk_router,
    predict_router,
)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="IDRMS API",
    description=(
        "Incident and Disaster Risk Management System — Barangay Kauswagan, Cagayan de Oro City.\n\n"
        "**ML Prediction Endpoints** are under `/api/predict/` and classify residents as "
        "LOW / MEDIUM / HIGH flood risk using Decision Tree, Random Forest, and Logistic Regression.\n\n"
       
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Create DB tables on startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
def on_startup():
    create_tables()


# ---------------------------------------------------------------------------
# Mount routers — every router lives under /api to match what both
# the web app (useLocalData.js) and mobile app (useDB.js) expect.
# ---------------------------------------------------------------------------

PREFIX = "/api"

app.include_router(auth_router,               prefix=PREFIX)
app.include_router(incidents_router,          prefix=PREFIX)
app.include_router(alerts_router,             prefix=PREFIX)
app.include_router(evacuation_centers_router, prefix=PREFIX)
app.include_router(residents_router,          prefix=PREFIX)
app.include_router(resources_router,          prefix=PREFIX)
app.include_router(users_router,              prefix=PREFIX)
app.include_router(activity_log_router,       prefix=PREFIX)
app.include_router(dashboard_router,          prefix=PREFIX)
app.include_router(reports_router,            prefix=PREFIX)
app.include_router(map_router,                prefix=PREFIX)
app.include_router(risk_router,               prefix=PREFIX)
app.include_router(predict_router,            prefix=PREFIX)


@app.get("/")
def root():
    return {
        "message": "IDRMS API is running.",
        "docs": "Visit /docs for the interactive API reference.",
        "ml_endpoints": "Visit /docs#/ML%20Predict for flood risk prediction endpoints.",
        "train_models": "Run 'python ml/train_model.py' once to generate ML model files.",
    }
