"""Phase C, step 7: the live model (what the daily system runs).

PURPOSE
  CHIRPS (about 24 days late) and ERA5-Land (about 12 days late) do not exist
  for the most recent days, so the daily run cannot use them (data test in
  phaseC_05_live_features.py). Decision of 1 Nov 2026 (Option A): the live
  model uses IMERG rain + fixed features only, 28 features. Same recipe as
  the chosen model (Random Forest with road features, phaseC_01), so the
  only difference is the feature list.

  The 38-feature model (rf_roads_v1) stays as the "best with complete data"
  reference; this one is what runs live and what the Phase E replays use.

  Also builds its threshold table from year-blocked cross-validation and
  lists the scores that give the same HP hit rates as the provisional levels
  of the 38-feature model (Watch: 55% of HP slides, Warning: 33%).

INPUTS   data/phaseB/training_table_v1.csv
OUTPUTS  models/rf_roads_live_v1.joblib, models/rf_roads_live_v1_meta.json,
         data/phaseC/threshold_options_live.csv, data/phaseC/oof_live.csv
RUN      .venv/Scripts/python -W ignore src/phaseC_07_train_live.py
"""
import json
from datetime import date

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import average_precision_score, roc_auc_score

from phaseC_01_train_compare import CAT, DROP, META, SEED, cross_validate, make_model
from phaseC_04_train_final import sha256

IN_CSV = "data/phaseB/training_table_v1.csv"
CHIRPS = ["chirps_d0", "chirps_ant1d", "chirps_ant3d", "chirps_ant7d", "chirps_ant15d", "chirps_ant30d"]
ERA5 = ["sm_l1_dm1", "sm_l2_dm1", "swe_dm1_mm", "snowmelt_ant7d_mm"]
HP_HIT_TARGETS = {"watch": 0.55, "warning": 0.33}   # HP hit rates of the 38-feature levels


def rates(g, p, thr):
    """Hit rate and safe-day / storm-day false-alarm rates at one threshold."""
    flag = p >= thr
    return (flag[(g.label == 1).values].mean(),
            flag[(g.neg_type == "same_place_safe_day").values].mean(),
            flag[(g.neg_type == "similar_place_storm_day").values].mean())


def main():
    df = pd.read_csv(IN_CSV)
    features = [c for c in df.columns if c not in META + DROP + CHIRPS + ERA5]
    num = [c for c in features if c not in CAT]
    cat = [c for c in features if c in CAT]
    print("live features:", len(features))

    # ---- year-blocked CV (skill numbers for the report) ----
    years = pd.to_datetime(df.event_date).dt.year.values
    p, _ = cross_validate(df, features, years, "random_forest")
    hp = (df.state == "HP").values
    t1 = df.neg_type.isin(["positive", "same_place_safe_day"]).values
    scores = {"roc_auc": roc_auc_score(df.label, p), "pr_auc": average_precision_score(df.label, p),
              "roc_auc_HP": roc_auc_score(df.label[hp], p[hp]), "roc_auc_type1": roc_auc_score(df.label[t1], p[t1])}
    print({k: round(v, 3) for k, v in scores.items()})
    df[["id", "label", "neg_type", "state", "event_date"]].assign(p_live=np.round(p, 5)) \
        .to_csv("data/phaseC/oof_live.csv", index=False)

    rows = []
    for thr in np.round(np.arange(0.20, 0.56, 0.05), 2):
        a = rates(df, p, thr)
        h = rates(df[hp], p[hp], thr)
        rows.append({"threshold": thr, "hit_rate": a[0], "hit_rate_HP": h[0],
                     "false_alarm_safe_day": a[1], "false_alarm_safe_day_HP": h[1],
                     "false_alarm_storm_day_other_slope": a[2],
                     "false_alarms_per_month_one_spot_HP": 30 * h[1]})
    table = pd.DataFrame(rows).round(3)
    table.to_csv("data/phaseC/threshold_options_live.csv", index=False)
    print(table.to_string(index=False))

    # Scores that match the HP hit rates of the 38-feature levels
    hp_pos = p[hp & (df.label == 1).values]
    matched = {}
    for level, target in HP_HIT_TARGETS.items():
        thr = float(np.quantile(hp_pos, 1 - target))
        h = rates(df[hp], p[hp], thr)
        matched[level] = {"score": round(thr, 3), "hit_rate_HP": round(h[0], 3),
                          "false_alarm_safe_day_HP": round(h[1], 3)}
    print("levels matched to the same HP hit rates:", matched)

    # ---- final live model on all rows ----
    model = make_model("random_forest", num, cat).fit(df[features], df["label"])
    joblib.dump(model, "models/rf_roads_live_v1.joblib", compress=3)
    meta = {"model": "Random Forest with road features, live feature set (IMERG + fixed)",
            "file": "models/rf_roads_live_v1.joblib", "trained_on": IN_CSV,
            "training_data_sha256": sha256(IN_CSV), "training_rows": int(len(df)),
            "trained_date": date.today().isoformat(), "features_in_order": features,
            "categorical_features": cat, "left_out_features": DROP + CHIRPS + ERA5,
            "settings": {"n_estimators": 500, "min_samples_leaf": 3, "random_state": SEED},
            "cv_scores_year_blocked": {k: round(v, 4) for k, v in scores.items()},
            "levels_matched_to_38_feature_hit_rates": matched,
            "alert_levels": "provisional; to be set by Suraj and finalised after Phase E",
            "versions": {"scikit-learn": sklearn.__version__, "pandas": pd.__version__}}
    with open("models/rf_roads_live_v1_meta.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    print("saved models/rf_roads_live_v1.joblib")


if __name__ == "__main__":
    main()
