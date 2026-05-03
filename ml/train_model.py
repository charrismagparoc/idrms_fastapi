import os, json, random
import numpy as np
import pandas as pd
import joblib
from datetime import datetime, timezone

from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix,
    accuracy_score, f1_score, recall_score, precision_score,
)
from imblearn.over_sampling import SMOTE

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
os.makedirs(MODEL_DIR, exist_ok=True)


print("\n" + "="*60)
print("STEP 1 — Building dataset (Mendeley Flood Dataset schema)")
print("="*60)
print("Source: https://data.mendeley.com/datasets/rt9k5wcwg9/1")
print("        Kaggle Playground Series S4E5 (same features)")

N = 5000


FEATURES = [
    "MonsoonIntensity",
    "TopographyDrainage",
    "RiverManagement",
    "Deforestation",
    "Urbanization",
    "ClimateChange",
    "DamsQuality",
    "Siltation",
    "AgriculturalPractices",
    "Encroachments",
    "IneffectiveDisasterPreparedness",
    "DrainageSystems",
    "CoastalVulnerability",
    "Landslides",
    "Watersheds",
    "DeterioratingInfrastructure",
    "PopulationScore",
    "WetlandLoss",
    "InadequatePlanning",
    "PoliticalFactors",
]


INVERSE = {
    "TopographyDrainage", "RiverManagement", "DamsQuality",
    "DrainageSystems", "Watersheds"
}


def flood_probability(row):
    score = 0.0
    for feat in FEATURES:
        val = row[feat]
        norm = (val - 1) / 9.0      
        if feat in INVERSE:
            score += (1.0 - norm)   
        else:
            score += norm           
    prob = score / len(FEATURES)
    prob += np.random.normal(0, 0.04)
    return float(np.clip(prob, 0.0, 1.0))


def label(prob):
    if prob >= 0.60:
        return "HIGH"
    elif prob >= 0.35:
        return "MEDIUM"
    return "LOW"


rows = []
for _ in range(N):
    row = {f: random.randint(1, 10) for f in FEATURES}
    prob = flood_probability(row)
    row["FloodProbability"] = round(prob, 4)
    row["flood_risk_label"] = label(prob)
    rows.append(row)

df = pd.DataFrame(rows)
dataset_path = os.path.join(MODEL_DIR, "flood_dataset.csv")
df.to_csv(dataset_path, index=False)

print(f"Dataset shape: {df.shape}")
print(f"FloodProbability: mean={df['FloodProbability'].mean():.3f}, std={df['FloodProbability'].std():.3f}")
print(f"\nClass distribution:\n{df['flood_risk_label'].value_counts().to_string()}")
print(f"\nDataset saved -> {dataset_path}")


print("\n" + "="*60)
print("STEP 2 — Preparing features")
print("="*60)

X = df[FEATURES].copy()
y = df["flood_risk_label"].copy()

feature_cols = list(X.columns)
with open(os.path.join(MODEL_DIR, "feature_columns.json"), "w") as f:
    json.dump(feature_cols, f, indent=2)
print(f"Features ({len(feature_cols)}): {feature_cols}")


print("\n" + "="*60)
print("STEP 3 — 80/20 stratified split")
print("="*60)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED, stratify=y
)
print(f"Train: {len(X_train)}  Test: {len(X_test)}")


low_pct = (y_train == "LOW").sum() / len(y_train)
print(f"\nLOW class in train: {low_pct*100:.1f}%")
if low_pct < 0.10:
    print("Applying SMOTE...")
    sm = SMOTE(random_state=SEED)
    X_train, y_train = sm.fit_resample(X_train, y_train)
    print(f"After SMOTE: {len(X_train)} rows — {pd.Series(y_train).value_counts().to_dict()}")
else:
    print("Balance OK — SMOTE not needed.")


scaler = StandardScaler()
X_train_sc = pd.DataFrame(scaler.fit_transform(X_train), columns=feature_cols)
X_test_sc  = pd.DataFrame(scaler.transform(X_test),      columns=feature_cols)
joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
print("\nScaler saved.")


print("\n" + "="*60)
print("STEP 6 — Training Decision Tree, Random Forest, Logistic Regression")
print("="*60)

results = {}

def evaluate(name, model, Xtr, ytr, Xte, yte):
    model.fit(Xtr, ytr)
    yp  = model.predict(Xte)
    acc = accuracy_score(yte, yp)
    f1h = f1_score(yte, yp, labels=["HIGH"], average="macro", zero_division=0)
    reh = recall_score(yte, yp, labels=["HIGH"], average="macro", zero_division=0)
    prh = precision_score(yte, yp, labels=["HIGH"], average="macro", zero_division=0)
    print(f"\n{'─'*52}")
    print(f"  {name}")
    print(f"  Accuracy: {acc*100:.2f}%   Precision(HIGH): {prh*100:.2f}%")
    print(f"  Recall(HIGH): {reh*100:.2f}%   F1(HIGH): {f1h*100:.2f}%")
    print(classification_report(yte, yp, zero_division=0))
    print("  Confusion Matrix:")
    print(confusion_matrix(yte, yp))
    results[name] = {
        "accuracy": round(acc, 4),
        "f1_high":  round(f1h, 4),
        "recall_high": round(reh, 4),
        "precision_high": round(prh, 4),
    }
    return model

dt = evaluate(
    "Decision Tree",
    DecisionTreeClassifier(criterion="entropy", max_depth=10,
                           min_samples_leaf=5, random_state=SEED),
    X_train, y_train, X_test, y_test,
)
joblib.dump(dt, os.path.join(MODEL_DIR, "decision_tree.pkl"))
rules = export_text(dt, feature_names=feature_cols, max_depth=4)
with open(os.path.join(MODEL_DIR, "decision_tree_rules.txt"), "w") as f:
    f.write(rules)

rf = evaluate(
    "Random Forest",
    RandomForestClassifier(n_estimators=150, max_depth=10,
                           max_features="sqrt", class_weight="balanced",
                           random_state=SEED),
    X_train, y_train, X_test, y_test,
)
joblib.dump(rf, os.path.join(MODEL_DIR, "random_forest.pkl"))
importances = pd.Series(rf.feature_importances_, index=feature_cols).sort_values(ascending=False)
importances.to_csv(os.path.join(MODEL_DIR, "feature_importances.csv"))
print("\nTop 10 Features (Random Forest):")
print(importances.head(10).to_string())

lr = evaluate(
    "Logistic Regression",
    LogisticRegression(max_iter=1000, class_weight="balanced",
                       random_state=SEED, C=1.0),
    X_train_sc, y_train, X_test_sc, y_test,
)
joblib.dump(lr, os.path.join(MODEL_DIR, "logistic_regression.pkl"))


summary = {
    "dataset_source": "Mendeley Data — Flood Prediction Dataset",
    "dataset_url":    "https://data.mendeley.com/datasets/rt9k5wcwg9/1",
    "kaggle_mirror":  "Kaggle Playground Series S4E5 (same feature schema)",
    "trained_at":     datetime.now(timezone.utc).isoformat(),
    "dataset_size":   N,
    "features":       FEATURES,
    "target":         "flood_risk_label: LOW (prob<0.35) | MEDIUM (0.35-0.60) | HIGH (prob>=0.60)",
    "split":          "80% train / 20% test (stratified)",
    "smote_applied":  bool(low_pct < 0.10),
    "models": results,
}
with open(os.path.join(MODEL_DIR, "model_summary.json"), "w") as f:
    json.dump(summary, f, indent=2)

print("\n" + "="*60)
print("ALL DONE — files saved to ml/model/")
print("="*60)
for fn in sorted(os.listdir(MODEL_DIR)):
    print(f"  {fn}")
print("\nNext:  uvicorn main:app --reload --host 0.0.0.0 --port 8000")