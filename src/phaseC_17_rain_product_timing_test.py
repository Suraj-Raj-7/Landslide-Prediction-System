"""Phase C, step 17: does a different rain product time landslides better than IMERG?

PURPOSE
  Rain on the day alone separates landslides from the same places on safe days
  (the timing test) with ROC AUC 0.824 using IMERG (phaseC_09). Part of the
  limit is that IMERG's ~10 km pixel can miss a storm on one side of a ridge.
  This script scores other free products by the same rule.

RULE (stated before seeing any result)
  Score = rain on the day only, no model. A product counts as better than
  IMERG only if (a) its AUC is higher on the same events and (b) the 95%
  year-block bootstrap interval of (product AUC - IMERG AUC) is entirely
  above 0. Comparisons are like for like on the day definition:
    GSMaP IST day    vs IMERG IST day
    GSMaP UTC day    vs IMERG UTC day
    PDIR-Now UTC day vs IMERG UTC day (PDIR-Now only comes as UTC days)
  All IMERG values here are re-pulled in phaseC_16 with the same sampling as
  GSMaP. Run for all rows and for HP rows.

BOOTSTRAP
  Whole years are resampled with replacement (2,000 draws, fixed seed), since
  events in one year share weather and are not independent.

INPUTS   data/phaseB/training_table_v1.csv, data/phaseC/rain_gee_d0.csv,
         data/phaseC/rain_pdirnow_d0.csv
OUTPUTS  data/phaseC/rain_product_timing_test.csv
RUN      .venv/Scripts/python -W ignore src/phaseC_17_rain_product_timing_test.py
"""
import os

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

SEED, N_BOOT = 20261106, 2000
PAIRS = [("gsmap_d0_ist", "imerg_d0_ist"),
         ("gsmap_d0_utc", "imerg_d0_utc"),
         ("pdirnow_d0_utc", "imerg_d0_utc")]


def year_bootstrap(y, a, b, years, rng):
    """95% interval of AUC(a) - AUC(b), resampling whole years."""
    uy = np.unique(years)
    idx = {yr: np.where(years == yr)[0] for yr in uy}
    diffs = []
    for _ in range(N_BOOT):
        pick = np.concatenate([idx[yr] for yr in rng.choice(uy, len(uy))])
        if y[pick].min() == y[pick].max():
            continue  # a draw with only one class cannot be scored
        diffs.append(roc_auc_score(y[pick], a[pick]) - roc_auc_score(y[pick], b[pick]))
    return np.percentile(diffs, [2.5, 97.5])


def main():
    df = pd.read_csv("data/phaseB/training_table_v1.csv")
    df = df[df.neg_type.isin(["positive", "same_place_safe_day"])]
    df = df.merge(pd.read_csv("data/phaseC/rain_gee_d0.csv"), on="id")
    if os.path.exists("data/phaseC/rain_pdirnow_d0.csv"):
        df = df.merge(pd.read_csv("data/phaseC/rain_pdirnow_d0.csv").drop(columns="event_date"),
                      on="id", how="left")
    rng = np.random.default_rng(SEED)
    rows = []
    for region, sub in [("all", df), ("HP", df[df.state == "HP"])]:
        for prod, base in PAIRS:
            if prod not in sub:
                continue
            s = sub.dropna(subset=[prod, base])  # same events for both products
            y, years = s.label.values, pd.to_datetime(s.event_date).dt.year.values
            a, b = s[prod].values, s[base].values
            lo, hi = year_bootstrap(y, a, b, years, rng)
            auc_p, auc_b = roc_auc_score(y, a), roc_auc_score(y, b)
            rows.append({"region": region, "product": prod, "baseline": base, "n_rows": len(s),
                         "n_missing_product": int(sub[prod].isna().sum()),
                         "auc_product": auc_p, "auc_imerg": auc_b, "diff": auc_p - auc_b,
                         "diff_ci_low": lo, "diff_ci_high": hi,
                         "better_by_rule": bool(auc_p > auc_b and lo > 0)})
            print(rows[-1], flush=True)
    res = pd.DataFrame(rows).round(3)
    res.to_csv("data/phaseC/rain_product_timing_test.csv", index=False)
    print(res.to_string(index=False))


if __name__ == "__main__":
    main()
