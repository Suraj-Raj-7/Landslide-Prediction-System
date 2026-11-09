"""Phase C, step 4: train and save the final model.

PURPOSE
  Train the chosen model (Random Forest with road features, decision of
  23 Oct 2026) on ALL rows of the training table and save it for the daily
  run (Phase D). Uses exactly the recipe tested in phaseC_01_train_compare.py
  (same features, same preprocessing, same settings), imported from there so
  the two cannot drift apart.

  Skill numbers for the report come from the cross-validation (phaseC_01..03),
  not from this script: a model scored on its own training rows always looks
  better than it is. The training-row AUC printed here is only a sanity check.

INPUTS
  data/phaseB/training_table_v1.csv

OUTPUTS
  models/rf_roads_v1.joblib     fitted pipeline (fill gaps -> one-hot -> Random Forest)
  models/rf_roads_v1_meta.json  features, alert levels, versions, data checksum, CV scores

RUN
  .venv/Scripts/python -W ignore src/phaseC_04_train_final.py
"""
import hashlib
import json
import os
from datetime import date

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import roc_auc_score

from phaseC_01_train_compare import CAT, DROP, META, SEED, make_model

IN_CSV = "data/phaseB/training_table_v1.csv"
OUT_MODEL = "models/rf_roads_v1.joblib"
OUT_META = "models/rf_roads_v1_meta.json"

# Provisional alert levels (Suraj, 24 Oct 2026); to be finalised after Phase E
LEVELS = {"watch": 0.35, "warning": 0.45}


def sha256(path):
    """Checksum of the training file, so the model can be traced to its exact data."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    df = pd.read_csv(IN_CSV)
    features = [c for c in df.columns if c not in META + DROP]
    num = [c for c in features if c not in CAT]
    cat = [c for c in features if c in CAT]

    model = make_model("random_forest", num, cat).fit(df[features], df["label"])

    # Sanity check only (in-sample); not a skill estimate
    p = model.predict_proba(df[features])[:, 1]
    print(f"trained on {len(df)} rows ({int(df.label.sum())} positives), {len(features)} features")
    print(f"in-sample ROC AUC {roc_auc_score(df.label, p):.3f} (sanity check only)")
    print(f"share of rows at Watch or above: {np.mean(p >= LEVELS['watch']):.3f}")

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, OUT_MODEL, compress=3)

    cv = pd.read_csv("data/phaseC/cv_metrics.csv")
    rf = cv[(cv.model == "random_forest") & (cv.features == "all")]
    meta = {
        "model": "Random Forest with road features",
        "file": OUT_MODEL,
        "trained_on": IN_CSV,
        "training_data_sha256": sha256(IN_CSV),
        "training_rows": int(len(df)),
        "positives": int(df.label.sum()),
        "trained_date": date.today().isoformat(),
        "features_in_order": features,
        "categorical_features": cat,
        "left_out_features": DROP,
        "settings": {"n_estimators": 500, "min_samples_leaf": 3, "random_state": SEED},
        "alert_levels_provisional": LEVELS,
        "valid_area": "cells within 500 m of a motorable road (documentation section 17.8)",
        "target": "reported landslides near roads",
        "cv_scores": {r.cv: {"roc_auc": r.roc_auc, "pr_auc": r.pr_auc} for r in rf.itertuples()},
        "versions": {"scikit-learn": sklearn.__version__, "pandas": pd.__version__, "numpy": np.__version__},
    }
    with open(OUT_META, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    print(f"saved {OUT_MODEL} ({os.path.getsize(OUT_MODEL) / 1e6:.1f} MB) and {OUT_META}")

    # Reload check: the saved file must give the same predictions
    again = joblib.load(OUT_MODEL).predict_proba(df[features])[:, 1]
    print("reload gives identical predictions:", bool(np.allclose(p, again)))


if __name__ == "__main__":
    main()
