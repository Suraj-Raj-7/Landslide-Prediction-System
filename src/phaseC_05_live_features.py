"""Phase C, step 5: which features can the live system actually use?

PURPOSE
  The daily run needs every feature for TODAY. Latency in GEE (checked 24 Oct
  2026): IMERG about 2 days behind, ERA5-Land about 12 days, CHIRPS about 24
  days. So in a live run the CHIRPS features (7) and the ERA5-Land soil
  moisture / snow features (4) are missing for the most recent days.

  This data test retrains the chosen model (Random Forest with roads, same
  recipe) with those feature groups removed and measures the cost with the
  same year-blocked cross-validation, overall and on the Type 1 test
  (positives vs same-place safe days).

INPUTS   data/phaseB/training_table_v1.csv
OUTPUTS  data/phaseC/live_feature_test.csv
RUN      .venv/Scripts/python -W ignore src/phaseC_05_live_features.py
"""
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from phaseC_01_train_compare import DROP, META, cross_validate

CHIRPS = ["chirps_d0", "chirps_ant1d", "chirps_ant3d", "chirps_ant7d", "chirps_ant15d", "chirps_ant30d"]
ERA5 = ["sm_l1_dm1", "sm_l2_dm1", "swe_dm1_mm", "snowmelt_ant7d_mm"]


def main():
    df = pd.read_csv("data/phaseB/training_table_v1.csv")
    full = [c for c in df.columns if c not in META + DROP]
    sets = {"all 38 (current model)": full,
            "no CHIRPS": [c for c in full if c not in CHIRPS],
            "no ERA5-Land soil/snow": [c for c in full if c not in ERA5],
            "no CHIRPS, no ERA5-Land (IMERG + fixed only)": [c for c in full if c not in CHIRPS + ERA5]}
    years = pd.to_datetime(df.event_date).dt.year.values
    t1 = df.neg_type.isin(["positive", "same_place_safe_day"]).values
    hp = (df.state == "HP").values
    rows = []
    for name, feats in sets.items():
        p, _ = cross_validate(df, feats, years, "random_forest")
        rows.append({"features": name, "n_features": len(feats),
                     "roc_auc": roc_auc_score(df.label, p),
                     "pr_auc": average_precision_score(df.label, p),
                     "roc_auc_type1": roc_auc_score(df.label[t1], p[t1]),
                     "roc_auc_HP": roc_auc_score(df.label[hp], p[hp])})
        print(rows[-1], flush=True)
    pd.DataFrame(rows).round(4).to_csv("data/phaseC/live_feature_test.csv", index=False)


if __name__ == "__main__":
    main()
