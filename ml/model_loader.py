"""
ml/model_loader.py
==================
Loads trained models from ml/model/ and provides the predict function.

Dataset schema: Mendeley Flood Prediction Dataset
  https://data.mendeley.com/datasets/rt9k5wcwg9/1
  20 features, each an integer 1-10 severity/quality score.
"""

import os, json
import joblib
import pandas as pd
from typing import List

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")

_feature_cols: List[str] = []
_scaler       = None
_dt           = None
_rf           = None
_lr           = None
_summary: dict = {}
_loaded       = False


def _load():
    global _feature_cols, _scaler, _dt, _rf, _lr, _summary, _loaded

    required = [
        "feature_columns.json", "scaler.pkl",
        "decision_tree.pkl", "random_forest.pkl", "logistic_regression.pkl",
    ]
    missing = [f for f in required if not os.path.exists(os.path.join(MODEL_DIR, f))]
    if missing:
        raise FileNotFoundError(
            f"ML model files not found: {missing}\n"
            f"Run:  python ml/train_model.py"
        )

    with open(os.path.join(MODEL_DIR, "feature_columns.json")) as f:
        _feature_cols = json.load(f)

    _scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
    _dt     = joblib.load(os.path.join(MODEL_DIR, "decision_tree.pkl"))
    _rf     = joblib.load(os.path.join(MODEL_DIR, "random_forest.pkl"))
    _lr     = joblib.load(os.path.join(MODEL_DIR, "logistic_regression.pkl"))

    summary_path = os.path.join(MODEL_DIR, "model_summary.json")
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            _summary = json.load(f)

    _loaded = True
    print("[ML] Models loaded from", MODEL_DIR)


_load()


def _build_row(features: dict) -> pd.DataFrame:
    """
    Build a one-row DataFrame in the exact column order the models expect.
    All 20 Mendeley features must be present in `features` as integers 1-10.
    """
    row = {col: features.get(col, 5) for col in _feature_cols}
    return pd.DataFrame([row])[_feature_cols]


def predict_flood_risk(features: dict, model_name: str = "random_forest") -> dict:
    """
    Predict flood risk label (LOW / MEDIUM / HIGH).

    Parameters
    ----------
    features   : dict of the 20 Mendeley feature names → integer values 1-10
    model_name : "decision_tree" | "random_forest" | "logistic_regression"

    Returns
    -------
    dict with flood_risk_label, confidence_pct, probabilities, model_used
    """
    X = _build_row(features)

    if model_name == "logistic_regression":
        X_input = pd.DataFrame(_scaler.transform(X), columns=_feature_cols)
        model   = _lr
    elif model_name == "decision_tree":
        X_input = X
        model   = _dt
    else:
        X_input = X
        model   = _rf

    prediction  = model.predict(X_input)[0]
    proba_array = model.predict_proba(X_input)[0]
    classes     = list(model.classes_)

    proba_dict = {c: round(float(p), 4) for c, p in zip(classes, proba_array)}
    confidence = round(float(max(proba_array)) * 100, 2)

    return {
        "flood_risk_label": prediction,
        "confidence_pct":   confidence,
        "probabilities":    proba_dict,
        "model_used":       model_name,
    }


def get_model_summary() -> dict:
    return _summary


def get_feature_importances(top_n: int = 10) -> list:
    pairs = sorted(zip(_feature_cols, _rf.feature_importances_),
                   key=lambda x: x[1], reverse=True)
    return [{"feature": f, "importance": round(float(imp), 6)}
            for f, imp in pairs[:top_n]]
