"""Phase C, step 6: road-neutral prediction test.

PURPOSE
  Recorded landslides cluster on roads because slides on roads are the ones
  that get reported. A model trained on them learns "far from a road = safe",
  which would hide risk in remote parts of HP. Proposed fix (decision of
  1 Nov 2026), following the idea of keeping a bias-describing variable in
  the model but neutralising it for prediction (Steger et al. 2017, 2021):
    - train exactly as before (road features included);
    - when predicting, set dist_road_m and dist_major_road_m to the median of
      the training positives for every location ("as if observed like a
      roadside slope").

  Data test, in the same year-blocked cross-validation, for the 38-feature
  model and the 28-feature live model. In each fold the model is trained
  once and each held-out row is scored twice: with its real road distances
  and road-neutral (medians taken from that fold's training positives).

  Questions:
    1. Do the 70 recorded landslides more than 500 m from a road (9 in HP)
       score higher, and reach Watch / Warning more often?
    2. What happens to false alarms on same-place safe days (Type 1) and on
       other slopes on storm days (Type 2)?
  Caveats: question 1 rests on few cases; and the data have no confirmed
  non-landslide locations far from roads, so false alarms in remote areas
  cannot be measured.

INPUTS   data/phaseB/training_table_v1.csv
OUTPUTS  data/phaseC/road_neutral_test.csv, data/phaseC/road_neutral_oof.csv
RUN      .venv/Scripts/python -W ignore src/phaseC_06_road_neutral_test.py
"""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

from phaseC_01_train_compare import CAT, DROP, META, N_FOLDS, ROAD, SEED, make_model
from phaseC_07_train_live import CHIRPS, ERA5

LEVELS = {"watch": 0.35, "warning": 0.45}
REMOTE_M = 500


def oof_two_ways(df, features):
    """Out-of-fold scores with real road distances and road-neutral."""
    num = [c for c in features if c not in CAT]
    cat = [c for c in features if c in CAT]
    X, y = df[features], df["label"].values
    years = pd.to_datetime(df.event_date).dt.year.values
    real, neutral = np.zeros(len(df)), np.zeros(len(df))
    cv = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    for tr, te in cv.split(X, y, years):
        model = make_model("random_forest", num, cat).fit(X.iloc[tr], y[tr])
        real[te] = model.predict_proba(X.iloc[te])[:, 1]
        med = X.iloc[tr][y[tr] == 1][ROAD].median()      # this fold's training positives
        Xn = X.iloc[te].copy()
        for c in ROAD:
            Xn[c] = med[c]
        neutral[te] = model.predict_proba(Xn)[:, 1]
    return real, neutral


def summary(df, p, name, mode):
    pos = df.label == 1
    remote = pos & (df.dist_road_m > REMOTE_M)
    remote_hp = remote & (df.state == "HP")
    near = pos & (df.dist_road_m <= REMOTE_M)
    t1 = df.neg_type == "same_place_safe_day"
    t2 = df.neg_type == "similar_place_storm_day"
    t1test = (pos | t1).values
    row = {"model": name, "prediction": mode,
           "roc_auc_all": roc_auc_score(df.label, p),
           "roc_auc_type1_test": roc_auc_score(df.label[t1test], p[t1test]),
           "remote_positives_n": int(remote.sum()), "remote_positives_HP_n": int(remote_hp.sum()),
           "remote_mean_score": p[remote.values].mean(), "near_mean_score": p[near.values].mean()}
    for lv, thr in LEVELS.items():
        row[f"remote_at_{lv}"] = (p[remote.values] >= thr).mean()
        row[f"remote_HP_at_{lv}"] = (p[remote_hp.values] >= thr).mean()
        row[f"all_positives_at_{lv}"] = (p[pos.values] >= thr).mean()
        row[f"type1_false_alarm_at_{lv}"] = (p[t1.values] >= thr).mean()
        row[f"type2_false_alarm_at_{lv}"] = (p[t2.values] >= thr).mean()
    return row


def main():
    df = pd.read_csv("data/phaseB/training_table_v1.csv")
    full = [c for c in df.columns if c not in META + DROP]
    live = [c for c in full if c not in CHIRPS + ERA5]
    rows, oof = [], df[["id", "label", "neg_type", "state", "dist_road_m"]].copy()
    for name, feats in [("rf_38_features", full), ("rf_28_live", live)]:
        real, neutral = oof_two_ways(df, feats)
        oof[f"{name}__real"], oof[f"{name}__neutral"] = real.round(5), neutral.round(5)
        rows += [summary(df, real, name, "real road distance"), summary(df, neutral, name, "road-neutral")]
        print(f"{name} done", flush=True)
    res = pd.DataFrame(rows).round(3)
    res.to_csv("data/phaseC/road_neutral_test.csv", index=False)
    oof.to_csv("data/phaseC/road_neutral_oof.csv", index=False)
    pd.set_option("display.width", 250)
    print(res.T.to_string())

    # Fair comparison: road-neutral raises every score, so compare at the SAME
    # safe-day false-alarm rate (threshold set so that 16% / 25% of Type 1 rows
    # are flagged), and ask how many remote / all slides are caught there.
    eq = []
    pos = (df.label == 1).values
    remote = pos & (df.dist_road_m > REMOTE_M).values
    remote_hp = remote & (df.state == "HP").values
    t1 = (df.neg_type == "same_place_safe_day").values
    t2 = (df.neg_type == "similar_place_storm_day").values
    for name in ["rf_38_features", "rf_28_live"]:
        for mode in ["real", "neutral"]:
            p = oof[f"{name}__{mode}"].values
            for fa in [0.16, 0.25]:
                thr = np.quantile(p[t1], 1 - fa)
                eq.append({"model": name, "prediction": mode, "type1_false_alarm": fa,
                           "threshold": thr, "all_positives_caught": (p[pos] >= thr).mean(),
                           "remote_caught": (p[remote] >= thr).mean(),
                           "remote_HP_caught": (p[remote_hp] >= thr).mean(),
                           "type2_flagged": (p[t2] >= thr).mean()})
    eq = pd.DataFrame(eq).round(3)
    eq.to_csv("data/phaseC/road_neutral_equal_false_alarm.csv", index=False)
    print("\nat equal safe-day false-alarm rate:\n" + eq.to_string(index=False))


if __name__ == "__main__":
    main()
