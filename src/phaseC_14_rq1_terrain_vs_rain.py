"""Phase C, step 14: Research question 1, does rainfall add to terrain?

PURPOSE
  RQ1 of the project (Assignment 1): does past and forecast rainfall improve
  landslide prediction beyond a static terrain baseline? This script answers
  the "past rainfall" part directly: the same Random Forest recipe, the same
  year-blocked cross-validation, with feature sets that add one group at a
  time:
    1. terrain and other fixed features only (no vegetation, no rain)
    2. + pre-event vegetation (NDVI over the 365 days before)
    3. + IMERG rain (the live model's 28 features)
    4. + CHIRPS rain, ERA5-Land soil moisture and snow (all 38 features)
  Scores: overall ROC AUC (landslides vs all negatives), for HP rows, and the
  timing test (landslides vs safe days at the same places, where terrain is
  identical, so a terrain-only model can only guess).

  Nothing is chosen from these results; they answer the research question.

INPUTS   data/phaseB/training_table_v1.csv
OUTPUTS  data/phaseC/rq1_terrain_vs_rain_all_rows.csv (first run, not a fair test; see below)
         data/phaseC/rq1_terrain_vs_rain.csv (fair test: landslides vs other slopes on storm days)
RUN      .venv/Scripts/python -W ignore src/phaseC_14_rq1_terrain_vs_rain.py
"""
import pandas as pd
from sklearn.metrics import roc_auc_score

from phaseC_01_train_compare import DROP, META, cross_validate
from phaseC_07_train_live import CHIRPS, ERA5
from phaseC_11_two_part_model import IMERG


def main():
    df = pd.read_csv("data/phaseB/training_table_v1.csv")
    full = [c for c in df.columns if c not in META + DROP]
    fixed = [c for c in full if c not in IMERG + CHIRPS + ERA5 + ["ndvi_pre365", "era5_glacier"]]
    sets = [("Terrain and fixed features only", fixed),
            ("+ pre-event vegetation (NDVI)", fixed + ["ndvi_pre365", "era5_glacier"]),
            ("+ IMERG rain (live model)", fixed + ["ndvi_pre365", "era5_glacier"] + IMERG),
            ("+ CHIRPS rain, soil moisture, snow (full model)", full)]
    years = pd.to_datetime(df.event_date).dt.year.values
    hp = (df.state == "HP").values
    t1 = df.neg_type.isin(["positive", "same_place_safe_day"]).values
    rows = []
    for name, feats in sets:
        p, _ = cross_validate(df, feats, years, "random_forest")
        rows.append({"features": name, "n_features": len(feats),
                     "roc_auc_all": roc_auc_score(df.label, p),
                     "roc_auc_HP": roc_auc_score(df.label[hp], p[hp]),
                     "roc_auc_timing": roc_auc_score(df.label[t1], p[t1])})
        print(rows[-1], flush=True)
    res = pd.DataFrame(rows).round(3)
    res.to_csv("data/phaseC/rq1_terrain_vs_rain_all_rows.csv", index=False)
    print(res.to_string(index=False))

    # Finding from the run above: on all rows, the terrain-only model scores
    # BELOW 0.5. Each landslide has a same-place twin (Type 1) with identical
    # terrain and the opposite label, usually in another year; when one is
    # tested the other is in training, so a terrain-only model learns "this
    # spot = the opposite label". That run is therefore not a fair RQ1 test.
    # Fair version: landslides vs other slopes on the same storm days (Type 2)
    # only, trained without the twins, so terrain is informative and the
    # question is whether rain adds to it.
    sub = df[df.neg_type.isin(["positive", "similar_place_storm_day"])].reset_index(drop=True)
    yrs = pd.to_datetime(sub.event_date).dt.year.values
    hp2 = (sub.state == "HP").values
    rows2 = []
    for name, feats in sets:
        p, _ = cross_validate(sub, feats, yrs, "random_forest")
        rows2.append({"features": name, "n_features": len(feats),
                      "roc_auc_where_all": roc_auc_score(sub.label, p),
                      "roc_auc_where_HP": roc_auc_score(sub.label[hp2], p[hp2])})
        print(rows2[-1], flush=True)
    res2 = pd.DataFrame(rows2).round(3)
    res2.to_csv("data/phaseC/rq1_terrain_vs_rain.csv", index=False)
    print("\nFair RQ1 test (landslides vs other slopes on storm days):\n" + res2.to_string(index=False))


if __name__ == "__main__":
    main()
