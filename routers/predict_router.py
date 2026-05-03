"""
routers/predict_router.py
==========================
ML Prediction endpoints for IDRMS flood vulnerability.

Dataset: Mendeley Flood Prediction Dataset
  https://data.mendeley.com/datasets/rt9k5wcwg9/1
  20 features (MonsoonIntensity, Deforestation, Urbanization, etc.)
  each scored 1-10.  Target: flood_risk_label (LOW / MEDIUM / HIGH)

Endpoints
---------
POST /api/predict/flood/          – predict for ONE location/area
POST /api/predict/batch/          – predict for multiple areas at once
GET  /api/predict/model-info/     – training metrics + dataset citation
GET  /api/predict/feature-importance/ – top influencing factors
GET  /api/predict/health/         – confirm models loaded
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ml.model_loader import (
    predict_flood_risk,
    get_model_summary,
    get_feature_importances,
)

router = APIRouter(
    prefix="/predict",
    tags=["ML Predict – Flood Risk (Mendeley Dataset)"],
)

VALID_MODELS = {"decision_tree", "random_forest", "logistic_regression"}


# ── Pydantic schemas ───────────────────────────────────────────────────────

class FloodRiskInput(BaseModel):
    """
    All 20 features from the Mendeley Flood Prediction Dataset.
    Each is an integer from 1 (lowest severity) to 10 (highest severity).
    For infrastructure features (TopographyDrainage, RiverManagement,
    DamsQuality, DrainageSystems, Watersheds), higher = BETTER (safer).
    """
    model_config = {"protected_namespaces": ()}

    # Environmental factors
    MonsoonIntensity: int           = Field(5, ge=1, le=10, description="Heavy rainfall intensity (1=low, 10=extreme)")
    TopographyDrainage: int         = Field(5, ge=1, le=10, description="Natural terrain drainage quality (1=poor, 10=excellent)")
    RiverManagement: int            = Field(5, ge=1, le=10, description="River dredging/bank management quality (1=poor, 10=excellent)")
    Deforestation: int              = Field(5, ge=1, le=10, description="Tree loss severity (1=minimal, 10=severe)")
    Urbanization: int               = Field(5, ge=1, le=10, description="Urban sprawl level (1=low, 10=extreme)")
    ClimateChange: int              = Field(5, ge=1, le=10, description="Climate change impact (1=minimal, 10=severe)")
    DamsQuality: int                = Field(5, ge=1, le=10, description="Dam infrastructure quality (1=poor, 10=excellent)")
    Siltation: int                  = Field(5, ge=1, le=10, description="River siltation severity (1=low, 10=extreme)")
    AgriculturalPractices: int      = Field(5, ge=1, le=10, description="Harmful agricultural practice level (1=low, 10=high)")
    Encroachments: int              = Field(5, ge=1, le=10, description="Floodplain encroachment level (1=low, 10=severe)")
    IneffectiveDisasterPreparedness: int = Field(5, ge=1, le=10, description="Disaster preparedness gap (1=well-prepared, 10=very ineffective)")
    DrainageSystems: int            = Field(5, ge=1, le=10, description="Drainage infrastructure quality (1=poor, 10=excellent)")
    CoastalVulnerability: int       = Field(5, ge=1, le=10, description="Coastal exposure to surges (1=low, 10=extreme)")
    Landslides: int                 = Field(5, ge=1, le=10, description="Landslide risk level (1=low, 10=extreme)")
    Watersheds: int                 = Field(5, ge=1, le=10, description="Watershed health (1=degraded, 10=healthy)")
    DeterioratingInfrastructure: int = Field(5, ge=1, le=10, description="Infrastructure decay level (1=good, 10=critical)")
    PopulationScore: int            = Field(5, ge=1, le=10, description="Population density/exposure (1=low, 10=extreme)")
    WetlandLoss: int                = Field(5, ge=1, le=10, description="Wetland destruction severity (1=low, 10=extreme)")
    InadequatePlanning: int         = Field(5, ge=1, le=10, description="Urban planning deficiency (1=good plans, 10=no planning)")
    PoliticalFactors: int           = Field(5, ge=1, le=10, description="Governance/corruption impact (1=good governance, 10=very corrupt)")

    # Optional metadata
    model_name: str                 = Field("random_forest", description="decision_tree | random_forest | logistic_regression")
    location_name: Optional[str]    = Field(None, description="Label for this area (e.g., 'Zone 3 - Riverside')")
    area_id: Optional[int]          = Field(None, description="Optional area/zone ID")


class PredictionResult(BaseModel):
    model_config = {"protected_namespaces": ()}

    location_name:    Optional[str]
    area_id:          Optional[int]
    flood_risk_label: str
    confidence_pct:   float
    probabilities:    dict
    model_used:       str
    features_used:    dict
    predicted_at:     str


class BatchInput(BaseModel):
    model_config = {"protected_namespaces": ()}
    areas:      List[FloodRiskInput]
    model_name: str = Field("random_forest")


# ── Helper ─────────────────────────────────────────────────────────────────

FEATURE_KEYS = [
    "MonsoonIntensity", "TopographyDrainage", "RiverManagement",
    "Deforestation", "Urbanization", "ClimateChange", "DamsQuality",
    "Siltation", "AgriculturalPractices", "Encroachments",
    "IneffectiveDisasterPreparedness", "DrainageSystems", "CoastalVulnerability",
    "Landslides", "Watersheds", "DeterioratingInfrastructure",
    "PopulationScore", "WetlandLoss", "InadequatePlanning", "PoliticalFactors",
]

def _extract_features(payload: FloodRiskInput) -> dict:
    return {k: getattr(payload, k) for k in FEATURE_KEYS}


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/flood/", response_model=PredictionResult)
def predict_one(payload: FloodRiskInput):
    """
    Predict flood risk (LOW / MEDIUM / HIGH) for one area/location.

    Provide all 20 Mendeley dataset features (integers 1-10).
    The model returns a label, confidence %, and class probabilities.

    Primary model is Random Forest (highest accuracy).
    You may also choose 'decision_tree' or 'logistic_regression'.
    """
    if payload.model_name not in VALID_MODELS:
        raise HTTPException(400, f"Unknown model. Choose from: {sorted(VALID_MODELS)}")

    features = _extract_features(payload)
    result   = predict_flood_risk(features, model_name=payload.model_name)

    return PredictionResult(
        location_name    = payload.location_name,
        area_id          = payload.area_id,
        flood_risk_label = result["flood_risk_label"],
        confidence_pct   = result["confidence_pct"],
        probabilities    = result["probabilities"],
        model_used       = result["model_used"],
        features_used    = features,
        predicted_at     = datetime.utcnow().isoformat(),
    )


@router.post("/batch/")
def predict_batch(payload: BatchInput):
    """
    Predict flood risk for multiple areas at once (max 500).
    Results sorted HIGH → MEDIUM → LOW.
    """
    if not payload.areas:
        raise HTTPException(400, "areas list is empty.")
    if len(payload.areas) > 500:
        raise HTTPException(400, "Maximum 500 areas per batch.")

    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    results, errors = [], []

    for area in payload.areas:
        area.model_name = payload.model_name
        try:
            results.append(predict_one(area))
        except HTTPException as e:
            errors.append({"area_id": area.area_id, "location_name": area.location_name, "error": e.detail})

    results.sort(key=lambda x: order.get(x.flood_risk_label, 3))

    return {
        "total":        len(results),
        "high_count":   sum(1 for r in results if r.flood_risk_label == "HIGH"),
        "medium_count": sum(1 for r in results if r.flood_risk_label == "MEDIUM"),
        "low_count":    sum(1 for r in results if r.flood_risk_label == "LOW"),
        "model_used":   payload.model_name,
        "errors":       errors,
        "predicted_at": datetime.utcnow().isoformat(),
        "results":      results,
    }


@router.get("/model-info/")
def model_info():
    """Training metrics and dataset citation — show during defense."""
    summary = get_model_summary()
    return {
        "dataset": {
            "name":   "Mendeley Flood Prediction Dataset",
            "url":    "https://data.mendeley.com/datasets/rt9k5wcwg9/1",
            "mirror": "Kaggle Playground Series Season 4 Episode 5 (same schema)",
            "description": (
                "20 environmental and socio-economic features (MonsoonIntensity, "
                "Deforestation, Urbanization, DrainageSystems, PopulationScore, etc.) "
                "each scored 1-10. Target variable is FloodProbability (0-1), "
                "converted to LOW/MEDIUM/HIGH for IDRMS classification."
            ),
        },
        "target_variable": "flood_risk_label: LOW (<0.35) | MEDIUM (0.35-0.60) | HIGH (>=0.60)",
        "features": summary.get("features", []),
        "training": {
            "dataset_size": summary.get("dataset_size"),
            "split":        summary.get("split"),
            "smote":        summary.get("smote_applied"),
            "trained_at":   summary.get("trained_at"),
        },
        "models": summary.get("models", {}),
        "primary_metric": "Recall on HIGH class — missing a HIGH-risk area is the worst outcome",
    }


@router.get("/feature-importance/")
def feature_importance(top_n: int = 10):
    """Top features from the Random Forest — which factor matters most?"""
    if not 1 <= top_n <= 20:
        raise HTTPException(400, "top_n must be 1-20.")
    return {
        "model":   "random_forest",
        "top_n":   top_n,
        "feature_importances": get_feature_importances(top_n=top_n),
    }


@router.get("/health/")
def health():
    """Confirm all 3 models are loaded."""
    summary = get_model_summary()
    return {
        "status":        "ok",
        "models_loaded": ["decision_tree", "random_forest", "logistic_regression"],
        "dataset_source": summary.get("dataset_url", "Mendeley Data"),
        "trained_at":    summary.get("trained_at", "unknown"),
        "message":       "ML models are loaded and ready to predict flood risk.",
    }
