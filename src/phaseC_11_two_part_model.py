"""Phase C, step 11: a two-part model, WHERE x WHEN.

PURPOSE
  phaseC_08/09 showed that rain alone tells WHEN a slide happens better than
  the single model (timing ROC AUC 0.82 vs 0.68-0.78), while the model tells
  WHERE better than rain. Cause: half the negatives are other slopes on the
  same storm days, as wet as the slides, so one model trained on all
  negatives gives rain too little weight.

  Fix tested here, following the structure of NASA's LHASA, which combines a
  susceptibility map (where) with a rainfall trigger (when) (Kirschbaum &
  Stanley 2018; Stanley et al. 2021):
    WHERE part: slides vs other slopes on the same storm days (Type 2);
                fixed features + pre-event NDVI + glacier flag.
    WHEN part:  slides vs safe days at the same places (Type 1);
                rain features only (live: IMERG; full: IMERG + CHIRPS + ERA5-Land).
    Score = P(where) x P(when).
  Both parts are Random Forests with the same settings as before, trained
  inside the same year-blocked folds (whole years held out). The WHERE part is
  also scored road-neutral (road distances set to the fold's training-positive
  median), as decided for the whole-HP map.

  Compared, on the same rows and folds, with the single models
  (data/phaseC/road_neutral_oof.csv) and with rain on the day alone.

INPUTS   data/phaseB/training_table_v1.csv, data/phaseC/road_neutral_oof.csv
OUTPUTS  data/phaseC/two_part_oof.csv, data/phaseC/two_part_comparison.csv
RUN      .venv/Scripts/python -W ignore src/phaseC_11_two_part_model.py
"""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

from phaseC_01_train_compare import CAT, DROP, META, N_FOLDS, ROAD, SEED, make_model
from phaseC_07_train_live import CHIRPS, ERA5

IMERG = ["imerg_d0", "imerg_ant1d", "imerg_ant3d", "imerg_ant7d", "imerg_ant15d", "imerg_ant30d", "imerg_max1d_7d"]
HP_HIT = 0.55            # HP hit rate of the current Watch level


def parts(df, when_feats):
    """Feature lists of the two parts."""
    allf = [c for c in df.columns if c not in META + DROP]
    dated = set(IMERG + CHIRPS + ERA5)
    where = [c for c in allf if c not in dated]           # fixed + ndvi_pre365 + era5_glacier
    return where, when_feats


def oof_two_part(df, where, when, when_model="random_forest"):
    X, y = df, df["label"].values
    t1 = (df.neg_type == "same_place_safe_day").values
    t2 = (df.neg_type == "similar_place_storm_day").values
    years = pd.to_datetime(df.event_date).dt.year.values
    out = {k: np.zeros(len(df)) for k in ["where", "where_neutral", "when"]}
    cv = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)   # same folds as before
    for tr, te in cv.split(X, y, years):
        trw = tr[(y[tr] == 1) | t2[tr]]
        trn = tr[(y[tr] == 1) | t1[tr]]
        mw = make_model("random_forest", [c for c in where if c not in CAT], [c for c in where if c in CAT]) \
            .fit(X.iloc[trw][where], y[trw])
        mn = make_model(when_model, when, []).fit(X.iloc[trn][when], y[trn])
        out["where"][te] = mw.predict_proba(X.iloc[te][where])[:, 1]
        Xn = X.iloc[te][where].copy()
        med = X.iloc[tr][y[tr] == 1][ROAD].median()
        for c in ROAD:
            Xn[c] = med[c]
        out["where_neutral"][te] = mw.predict_proba(Xn)[:, 1]
        out["when"][te] = mn.predict_proba(X.iloc[te][when])[:, 1]
    return out


def evaluate(df, p, name):
    pos = (df.label == 1).values
    t1 = (df.neg_type == "same_place_safe_day").values
    t2 = (df.neg_type == "similar_place_storm_day").values
    hp = (df.state == "HP").values
    row = {"method": name}
    for reg, m in [("all", np.ones(len(df), bool)), ("HP", hp)]:
        row[f"timing_auc_{reg}"] = roc_auc_score(df.label[m & (pos | t1)], p[m & (pos | t1)])
        row[f"full_auc_{reg}"] = roc_auc_score(df.label[m], p[m])
    # HP operating point: threshold catching 55% of HP slides
    thr = np.quantile(p[hp & pos], 1 - HP_HIT)
    row["HP_safe_days_flagged_at_55pct_hit"] = (p[hp & t1] >= thr).mean()
    row["HP_storm_day_other_slopes_flagged_at_55pct_hit"] = (p[hp & t2] >= thr).mean()
    # and the reverse: HP slides caught when 16% of HP safe days are flagged
    thr16 = np.quantile(p[hp & t1], 1 - 0.16)
    row["HP_slides_caught_at_16pct_safe_days"] = (p[hp & pos] >= thr16).mean()
    return row


def main():
    df = pd.read_csv("data/phaseB/training_table_v1.csv")
    rn = pd.read_csv("data/phaseC/road_neutral_oof.csv")
    assert (df.id.values == rn.id.values).all()
    rows, oof = [], df[["id", "label", "neg_type", "state", "event_date"]].copy()

    rows.append(evaluate(df, df.imerg_d0.values, "Rain on the day alone"))
    for name, col in [("Single model, live 28, real roads", "rf_28_live__real"),
                      ("Single model, live 28, road-neutral", "rf_28_live__neutral"),
                      ("Single model, full 38, real roads", "rf_38_features__real"),
                      ("Single model, full 38, road-neutral", "rf_38_features__neutral")]:
        rows.append(evaluate(df, rn[col].values, name))

    # WHEN part as a Random Forest, and as a logistic regression on log rain
    # (the classic rainfall-threshold form; long-tailed rain is log-transformed
    # and scaled inside make_model)
    for label, when in [("live", IMERG), ("full", IMERG + CHIRPS + ERA5)]:
        for wm, wtag in [("random_forest", "RF"), ("logistic", "LR")]:
            where, when_f = parts(df, when)
            o = oof_two_part(df, where, when_f, wm)
            key = f"{label}_{wtag}"
            for k, v in o.items():
                oof[f"{key}__{k}"] = v.round(5)
            rows.append(evaluate(df, o["when"], f"WHEN part alone ({label}, {wtag})"))
            rows.append(evaluate(df, o["where"] * o["when"], f"Two-part {label}, when={wtag}, real roads"))
            rows.append(evaluate(df, o["where_neutral"] * o["when"], f"Two-part {label}, when={wtag}, road-neutral"))
            print(f"{key}: where {len(where)} features, when {len(when_f)} features", flush=True)

    res = pd.DataFrame(rows).round(3)
    res.to_csv("data/phaseC/two_part_comparison.csv", index=False)
    oof.to_csv("data/phaseC/two_part_oof.csv", index=False)
    pd.set_option("display.width", 250)
    print(res.to_string(index=False))


if __name__ == "__main__":
    main()
