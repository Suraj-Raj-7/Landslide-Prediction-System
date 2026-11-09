"""Phase C, step 2: compare models on the Type 1 test only, and check road coverage.

PURPOSE
  Type 1 negatives are the same places as the positives on safe days, so road
  distance is identical for both and cannot help. This test isolates how well
  each model reads the weather (the part that changes from day to day), which
  is what a daily warning depends on.

  Decision rule, fixed before running: XGBoost with road features is "clearly
  worse" than a road-free model if its ROC AUC on positives vs Type 1 is lower
  AND the 95% interval of the difference lies entirely below zero. Intervals
  come from a block bootstrap that resamples whole years (2,000 repeats),
  because rows from the same year share weather and are not independent
  (Roberts et al. 2017).

  Also: false-alarm rate on safe days at equal hit rates, and how much of the
  training data lies within 300 / 500 m of a motorable road (basis for
  limiting the risk map to road corridors).

INPUTS
  data/phaseC/oof_predictions.csv   (from phaseC_01_train_compare.py)
  data/phaseB/training_table_v1.csv

OUTPUTS (data/phaseC/)
  type1_check.csv          AUC on the Type 1 test per run, with 95% intervals
  type1_differences.csv    XGBoost-with-roads minus each road-free run, with 95% intervals
  type1_equal_hit.csv      safe-day false-alarm rate at hit rates 50-80%

RUN
  .venv/Scripts/python -W ignore src/phaseC_02_type1_check.py
"""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

SEED = 20261023
N_BOOT = 2000
OUT = "data/phaseC"
REF = "xgboost__by_year"
RUNS = ["logistic__by_year", "random_forest__by_year", "xgboost__by_year",
        "logistic__by_year__no_road", "random_forest__by_year__no_road", "xgboost__by_year__no_road"]


def main():
    oof = pd.read_csv(f"{OUT}/oof_predictions.csv")
    sub = oof[oof.neg_type.isin(["positive", "same_place_safe_day"])].reset_index(drop=True)
    sub["year"] = pd.to_datetime(sub.event_date).dt.year
    y = sub.label.values
    print(f"Type 1 test: {int(y.sum())} positives vs {int((y == 0).sum())} same-place safe days")

    # ---- point estimates and year-block bootstrap ----
    years = sub.year.unique()
    idx_by_year = {yr: np.where(sub.year.values == yr)[0] for yr in years}
    rng = np.random.default_rng(SEED)
    boot = {r: [] for r in RUNS}
    for _ in range(N_BOOT):
        pick = rng.choice(years, size=len(years), replace=True)
        idx = np.concatenate([idx_by_year[yr] for yr in pick])
        if y[idx].min() == y[idx].max():   # a resample with only one class has no AUC
            continue
        for r in RUNS:
            boot[r].append(roc_auc_score(y[idx], sub[r].values[idx]))
    boot = {r: np.array(v) for r, v in boot.items()}

    rows = []
    for r in RUNS:
        rows.append({"run": r, "roc_auc_type1": roc_auc_score(y, sub[r]),
                     "ci_low": np.percentile(boot[r], 2.5), "ci_high": np.percentile(boot[r], 97.5)})
    pd.DataFrame(rows).round(4).to_csv(f"{OUT}/type1_check.csv", index=False)
    print(pd.DataFrame(rows).round(3).to_string(index=False))

    # Same rule for every model that keeps the road features (XGBoost first,
    # then Random Forest and logistic regression as fallbacks)
    diffs = []
    for ref in [REF, "random_forest__by_year", "logistic__by_year"]:
        for r in RUNS:
            if "no_road" not in r:
                continue
            d = boot[ref] - boot[r]
            lo, hi = np.percentile(d, [2.5, 97.5])
            diffs.append({"comparison": f"{ref} minus {r}",
                          "auc_difference": roc_auc_score(y, sub[ref]) - roc_auc_score(y, sub[r]),
                          "ci_low": lo, "ci_high": hi,
                          "clearly_worse": bool(hi < 0)})
    pd.DataFrame(diffs).round(4).to_csv(f"{OUT}/type1_differences.csv", index=False)
    print("\n" + pd.DataFrame(diffs).round(3).to_string(index=False))

    # ---- safe-day false alarms at equal hit rate ----
    eq = []
    for target in [0.5, 0.6, 0.7, 0.8]:
        row = {"hit_rate": target}
        for r in RUNS:
            thr = np.quantile(sub.loc[y == 1, r], 1 - target)
            row[r] = (sub.loc[y == 0, r] >= thr).mean()
        eq.append(row)
    pd.DataFrame(eq).round(3).to_csv(f"{OUT}/type1_equal_hit.csv", index=False)
    print("\nsafe-day false-alarm rate at equal hit rate:\n" + pd.DataFrame(eq).round(2).to_string(index=False))

    # ---- road coverage of the training data ----
    t = pd.read_csv("data/phaseB/training_table_v1.csv")
    print("\nshare of rows within X m of a motorable road:")
    for nt, g in t.groupby("neg_type"):
        d = g.dist_road_m
        print(f"  {nt:<26} <=300 m {(d <= 300).mean():.3f}  <=500 m {(d <= 500).mean():.3f}  max {d.max():.0f} m")


if __name__ == "__main__":
    main()
