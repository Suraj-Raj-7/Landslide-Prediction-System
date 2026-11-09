"""Phase C, step 3: alert-threshold options for the candidate models.

PURPOSE
  For each candidate model (both keep the road features), list what each
  threshold would mean: share of reported slides caught (hit rate) and how
  often it would raise a false alarm. Numbers are given for all three states
  and for HP alone (the target state). Uses the year-blocked out-of-fold
  predictions, so every row is scored by a model that never saw its year.

  Candidates:
    xgboost__by_year        best overall, but clearly worse on the Type 1
                            (same place, safe day) test (phaseC_02)
    random_forest__by_year  close overall, not worse on the Type 1 test

  False alarms per month at one spot = Type 1 false-alarm rate x 30
  (Type 1 = random days at landslide spots, mostly monsoon months). A proxy
  only; district-level counts come from the Phase E replays.

INPUTS   data/phaseC/oof_predictions.csv
OUTPUTS  data/phaseC/threshold_options.csv
RUN      .venv/Scripts/python -W ignore src/phaseC_03_threshold_options.py
"""
import numpy as np
import pandas as pd

OUT = "data/phaseC"
CANDIDATES = {"xgboost__by_year": np.arange(0.10, 0.61, 0.05),
              "random_forest__by_year": np.arange(0.20, 0.56, 0.05)}


def summarise(g, p, thr):
    """Hit rate and false-alarm rates for one group of rows at one threshold."""
    flag = g[p] >= thr
    pos = g.label == 1
    t1 = g.neg_type == "same_place_safe_day"
    t2 = g.neg_type == "similar_place_storm_day"
    return flag[pos].mean(), flag[t1].mean(), flag[t2].mean()


def main():
    oof = pd.read_csv(f"{OUT}/oof_predictions.csv")
    hp = oof[oof.state == "HP"]
    rows = []
    for model, thresholds in CANDIDATES.items():
        for thr in np.round(thresholds, 2):
            hit, fa1, fa2 = summarise(oof, model, thr)
            hit_hp, fa1_hp, fa2_hp = summarise(hp, model, thr)
            rows.append({"model": model.replace("__by_year", ""), "threshold": thr,
                         "hit_rate": hit, "hit_rate_HP": hit_hp,
                         "false_alarm_safe_day": fa1, "false_alarm_safe_day_HP": fa1_hp,
                         "false_alarm_storm_day_other_slope": fa2,
                         "false_alarms_per_month_one_spot": 30 * fa1,
                         "false_alarms_per_month_one_spot_HP": 30 * fa1_hp})
    t = pd.DataFrame(rows).round(3)
    t.to_csv(f"{OUT}/threshold_options.csv", index=False)
    pd.set_option("display.width", 220)
    print(t.to_string(index=False))
    print(f"\nHP rows: {int((hp.label == 1).sum())} positives, "
          f"{int((hp.neg_type == 'same_place_safe_day').sum())} Type 1, "
          f"{int((hp.neg_type == 'similar_place_storm_day').sum())} Type 2")


if __name__ == "__main__":
    main()
