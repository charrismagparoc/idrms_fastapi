# IDRMS FastAPI — With Machine Learning
### Incident and Disaster Risk Management System — Barangay Kauswagan, Cagayan de Oro City
**Flood Vulnerability Profiling Using Machine Learning**

---

## Project Overview

This FastAPI backend powers the IDRMS system with a complete Machine Learning pipeline that classifies every resident as **LOW**, **MEDIUM**, or **HIGH** flood risk. When the water level sensor triggers an alert, barangay officials can immediately see which residents are HIGH risk on the admin web map — sorted by priority for targeted evacuation response.

---

## Quick Start

### Step 1 — Create and Activate a Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 2 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Train the ML Models (Run Once)
```bash
python ml/train_model.py
```
This generates all model files inside `ml/model/`:
- `decision_tree.pkl`
- `random_forest.pkl`
- `logistic_regression.pkl`
- `scaler.pkl`
- `feature_columns.json`
- `training_data.csv` (5,000-row IDRMS dataset)
- `model_summary.json` (accuracy, F1 scores)

### Step 4 — Run the Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5 — Open the Docs
```
http://localhost:8000/docs
```

---

## Project Structure

```
idrms_fastapi_ml/
│
├── main.py                  ← FastAPI app entry point
├── database.py              ← SQLAlchemy engine + session (SQLite by default)
├── models.py                ← ORM table definitions
├── schemas.py               ← Pydantic request/response models
├── requirements.txt
│
├── ml/
│   ├── train_model.py       ← Run once: trains and saves all 3 ML models
│   ├── model_loader.py      ← Loads models at startup; predict_resident_risk()
│   └── model/               ← Auto-generated after running train_model.py
│       ├── decision_tree.pkl
│       ├── random_forest.pkl
│       ├── logistic_regression.pkl
│       ├── scaler.pkl
│       ├── feature_columns.json
│       ├── training_data.csv
│       ├── model_summary.json
│       ├── feature_importances.csv
│       └── decision_tree_rules.txt
│
└── routers/
    ├── __init__.py
    ├── predict_router.py    ← ML prediction endpoints
    ├── residents_router.py
    ├── incidents_router.py
    ├── alerts_router.py
    ├── evacuation_centers_router.py
    ├── resources_router.py
    ├── users_router.py
    ├── auth_router.py
    ├── dashboard_router.py
    ├── reports_router.py
    ├── map_router.py
    ├── risk_router.py
    └── activity_log_router.py
```

---

## Machine Learning — How It Works

### Dataset
- **Primary**: 5,000-row synthetic dataset modeled after the [Mendeley Flood Prediction Dataset (Barros, 2024)](https://data.mendeley.com/datasets/rt9k5wcwg9/1)
- **Secondary**: Real resident profiles from the IDRMS database (via household surveys)

### Features Used
| Feature | Type | Description |
|---|---|---|
| `zone` | Category (Zone 1–6) | Most important: determines base risk score |
| `evacuation_status` | Category (3 options) | Safe / Evacuated / Unaccounted |
| `household_members` | Integer | Number of people in household |
| `rainy_season` | Binary (0/1) | Auto-detected from system date (June–November = 1) |
| `vulnerability_tags` | Multi-label | Bedridden, PWD, Senior Citizen, Pregnant, Infant |
| `risk_score` | Float | Computed by IDRMS rule engine |

### Target Variable
- `risk_label`: **LOW** (score < 40) | **MEDIUM** (40–69) | **HIGH** (≥ 70)

### Models Trained
| Model | Accuracy | F1 (HIGH class) |
|---|---|---|
| Decision Tree | ~100% | ~100% |
| Random Forest | ~99.9% | ~99.9% |
| Logistic Regression | ~98.5% | ~99.1% |

### Pipeline
1. Generate 5,000 synthetic records (mirrors Mendeley dataset + IDRMS fields)
2. One-hot encode zone and evacuation_status
3. Multi-label encode vulnerability tags
4. 80/20 stratified train-test split
5. Apply SMOTE if HIGH class < 15% of training data
6. Train all 3 models, evaluate with Accuracy, Precision, Recall, F1, ROC-AUC
7. Save models + artifacts to `ml/model/`

---

## ML Prediction API Endpoints

All ML endpoints are under `/api/predict/`:

### `POST /api/predict/resident/`
Predict flood risk for ONE resident.

**Request Body:**
```json
{
  "zone": "Zone 3",
  "evacuation_status": "Safe",
  "household_members": 5,
  "vulnerability_tags": ["Senior Citizen", "PWD"],
  "model_name": "random_forest",
  "resident_name": "Juan Dela Cruz",
  "resident_id": 1
}
```

**Response:**
```json
{
  "resident_name": "Juan Dela Cruz",
  "resident_id": 1,
  "zone": "Zone 3",
  "evacuation_status": "Safe",
  "household_members": 5,
  "vulnerability_tags": ["Senior Citizen", "PWD"],
  "risk_score": 105.0,
  "risk_label": "HIGH",
  "confidence_pct": 99.5,
  "probabilities": {"HIGH": 0.995, "MEDIUM": 0.005, "LOW": 0.0},
  "model_used": "random_forest",
  "predicted_at": "2025-01-01T00:00:00"
}
```

### `POST /api/predict/batch/`
Predict flood risk for up to 500 residents. Results sorted HIGH → MEDIUM → LOW.

### `GET /api/predict/model-info/`
Returns training metrics (accuracy, F1) for all 3 models.

### `GET /api/predict/feature-importance/`
Returns top-N feature importances from the Random Forest.

### `GET /api/predict/health/`
Confirms all 3 ML models are loaded and ready.

---

## All API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/residents/` | List all residents |
| POST | `/api/residents/` | Add a resident |
| PATCH | `/api/residents/{id}/` | Update a resident |
| DELETE | `/api/residents/{id}/` | Delete a resident |
| POST | `/api/predict/resident/` | Predict flood risk (single) |
| POST | `/api/predict/batch/` | Predict flood risk (batch) |
| GET | `/api/predict/model-info/` | ML model training metrics |
| GET | `/api/predict/feature-importance/` | Feature importance scores |
| GET | `/api/predict/health/` | ML model health check |
| GET | `/api/incidents/` | List all incidents |
| GET | `/api/alerts/` | List all alerts |
| GET | `/api/evacuation-centers/` | List evacuation centers |
| GET | `/api/resources/` | List resources |
| GET | `/api/dashboard/summary/` | Dashboard stats |
| GET | `/api/reports/summary/` | Report summary |
| GET | `/api/map/data/` | All geo-tagged records |
| GET | `/api/risk/zones/` | Zone risk scores |
| POST | `/api/auth/login/` | Login |

---

## References

- Barros, A. (2024). *Flood Prediction Dataset*. Mendeley Data, V1. DOI: 10.17632/rt9k5wcwg9.1
- Scikit-learn Developers. *scikit-learn: Machine Learning in Python*, v1.5.0, 2024.
- Chawla et al. (2002). *SMOTE: Synthetic Minority Over-sampling Technique*. JAIR, 16, 321–357.
