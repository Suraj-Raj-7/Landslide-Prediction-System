"""Phase C, step 1: train and compare three models with blocked cross-validation.

PURPOSE
  Compare logistic regression (baseline), Random Forest and XGBoost on the
  Phase B training table, with cross-validation that holds out whole YEARS
  (main test) or whole EVENT DATES (second test), never random rows.
  Measure how much the models rely on distance to road.

INPUTS
  data/phaseB/training_table_v1.csv   3,136 rows: 969 positives (label 1),
                                      969 Type 1 + 1,198 Type 2 negatives (label 0)

OUTPUTS (data/phaseC/)
  cv_metrics.csv            ROC AUC, PR AUC, Brier score per model and CV scheme
  oof_predictions.csv       out-of-fold probability for every row, model, scheme
  threshold_table.csv       hit rate and false-alarm rates at thresholds 0.1-0.9
  permutation_importance.csv  drop in ROC AUC when each feature is shuffled
  road_check.csv            with vs without road features, and AUC per negative type
  fig_roc_pr.png, fig_importance.png, fig_thresholds.png

METHOD AND BASIS
  - Blocked CV: random CV overstates skill when data have time or space
    structure; hold out whole blocks instead (Roberts et al. 2017, Ecography
    40:913-929). LHASA v2 gives the same warning (Stanley et al. 2021).
  - Models: logistic regression; Random Forest (Breiman 2001, Machine Learning
    45:5-32); XGBoost (Chen & Guestrin 2016, KDD), the model of LHASA v2.
  - Features: the 42 of the feature stack minus 4:
      ndvi_pre_n, imerg_images_31d, imerg_provisional_31d  (data-quality counts,
      not ground conditions; ndvi_pre_n rises from 18 to 41 images between
      2005-12 and 2021-26, so it would tell the model the year), and
      aspect_deg (circular; aspect_sin / aspect_cos carry the same information).
  - Category columns (rock, landform, land cover) are one-hot encoded.
  - Hit rate = share of positives with probability >= threshold.
    False-alarm rate = share of negatives above the threshold, reported
    separately for Type 1 (same place, safe day) and Type 2 (similar slope,
    storm day). Type 1 dates are random days at landslide spots, so
    Type 1 rate x 30 approximates false alarms per month at one such spot
    (mostly monsoon months). Real district-level counts come from the
    storm replays in Phase E.

RUN
  .venv/Scripts/python -W ignore src/phaseC_01_train_compare.py
"""
import os
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss,
                             precision_recall_curve, roc_auc_score, roc_curve)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

SEED = 20261023
N_FOLDS = 5
IN_CSV = "data/phaseB/training_table_v1.csv"
OUT = "data/phaseC"
THRESHOLDS = np.round(np.arange(0.1, 0.91, 0.1), 1)

META = ["id", "label", "neg_type", "src_id", "state", "admin_unit", "lat", "lon", "event_date"]
DROP = ["ndvi_pre_n", "imerg_images_31d", "imerg_provisional_31d", "aspect_deg"]
CAT = ["glim_code", "rock_code", "gm_code", "lc_class", "lc_class_30m"]
ROAD = ["dist_road_m", "dist_major_road_m"]


def log1p_pos(x):
    """log(1 + x) with negatives clipped to 0; evens out long-tailed distances and rain."""
    return np.log1p(np.clip(x, 0, None))


def make_model(name, num, cat):
    """Build one model as a pipeline: fill gaps, encode categories, then classify."""
    skewed = [c for c in num if c.startswith(("dist_", "imerg_", "chirps_", "hand_", "snowmelt_", "swe_"))]
    plain = [c for c in num if c not in skewed]
    onehot = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    if name == "logistic":
        # Linear model: log the long-tailed columns and scale everything
        prep = ColumnTransformer([
            ("skewed", Pipeline([("fill", SimpleImputer(strategy="median")),
                                 ("log", FunctionTransformer(log1p_pos)),
                                 ("scale", StandardScaler())]), skewed),
            ("plain", Pipeline([("fill", SimpleImputer(strategy="median")),
                                ("scale", StandardScaler())]), plain),
            ("cat", onehot, cat)])
        clf = LogisticRegression(C=1.0, max_iter=5000)
    else:
        # Tree models do not need scaling or logs
        prep = ColumnTransformer([("num", SimpleImputer(strategy="median"), num), ("cat", onehot, cat)])
        if name == "random_forest":
            clf = RandomForestClassifier(n_estimators=500, min_samples_leaf=3, n_jobs=-1, random_state=SEED)
        else:
            clf = XGBClassifier(n_estimators=400, max_depth=4, learning_rate=0.05, subsample=0.8,
                                colsample_bytree=0.8, eval_metric="logloss", n_jobs=-1, random_state=SEED)
    return Pipeline([("prep", prep), ("clf", clf)])


def cross_validate(df, features, groups, model_name, importance=False):
    """Out-of-fold probabilities; optionally permutation importance on each held-out fold."""
    num = [c for c in features if c not in CAT]
    cat = [c for c in features if c in CAT]
    X, y = df[features], df["label"].values
    oof = np.zeros(len(df))
    imp = []
    cv = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    for k, (tr, te) in enumerate(cv.split(X, y, groups)):
        model = make_model(model_name, num, cat).fit(X.iloc[tr], y[tr])
        oof[te] = model.predict_proba(X.iloc[te])[:, 1]
        if importance:
            r = permutation_importance(model, X.iloc[te], y[te], scoring="roc_auc",
                                       n_repeats=5, random_state=SEED, n_jobs=-1)
            imp.append(pd.Series(r.importances_mean, index=features, name=k))
    return oof, (pd.concat(imp, axis=1).mean(axis=1) if importance else None)


def rates(df, p, thr):
    """Hit rate and false-alarm rates at one threshold."""
    flag = p >= thr
    pos = df["label"].values == 1
    t1 = (df["neg_type"] == "same_place_safe_day").values
    t2 = (df["neg_type"] == "similar_place_storm_day").values
    return {"threshold": thr,
            "hit_rate": flag[pos].mean(),
            "false_alarm_rate_type1": flag[t1].mean(),
            "false_alarm_rate_type2": flag[t2].mean(),
            "false_alarms_per_month_at_one_spot": 30 * flag[t1].mean(),
            "missed_slides": int((~flag[pos]).sum())}


def main():
    os.makedirs(OUT, exist_ok=True)
    df = pd.read_csv(IN_CSV)
    features = [c for c in df.columns if c not in META + DROP]
    no_road = [c for c in features if c not in ROAD]
    schemes = {"by_year": pd.to_datetime(df["event_date"]).dt.year.values,
               "by_event_date": df["event_date"].values}
    models = ["logistic", "random_forest", "xgboost"]
    print(f"rows {len(df)} | positives {int(df.label.sum())} | features used {len(features)}")
    print("left out:", DROP)

    metrics, oof_cols, thr_rows, imp_all = [], {}, [], {}
    for scheme, groups in schemes.items():
        for m in models:
            p, imp = cross_validate(df, features, groups, m, importance=(scheme == "by_year"))
            oof_cols[f"{m}__{scheme}"] = p
            if imp is not None:
                imp_all[m] = imp
            metrics.append({"model": m, "cv": scheme, "features": "all",
                            "roc_auc": roc_auc_score(df.label, p),
                            "pr_auc": average_precision_score(df.label, p),
                            "brier": brier_score_loss(df.label, p)})
            for t in THRESHOLDS:
                thr_rows.append({"model": m, "cv": scheme, **rates(df, p, t)})
            print(f"{scheme:<14}{m:<14} ROC AUC {metrics[-1]['roc_auc']:.3f}  PR AUC {metrics[-1]['pr_auc']:.3f}", flush=True)

    # ---- road check (year CV): refit without road features; AUC per negative type ----
    road_rows = []
    pos = df.label == 1
    for m in models:
        p_no, _ = cross_validate(df, no_road, schemes["by_year"], m)
        oof_cols[f"{m}__by_year__no_road"] = p_no
        metrics.append({"model": m, "cv": "by_year", "features": "no_road",
                        "roc_auc": roc_auc_score(df.label, p_no),
                        "pr_auc": average_precision_score(df.label, p_no),
                        "brier": brier_score_loss(df.label, p_no)})
        for t in THRESHOLDS:
            thr_rows.append({"model": m, "cv": "by_year_no_road", **rates(df, p_no, t)})
        for name, p in [("all", oof_cols[f"{m}__by_year"]), ("no_road", p_no)]:
            for nt in ["same_place_safe_day", "similar_place_storm_day"]:
                sub = pos | (df.neg_type == nt)
                road_rows.append({"model": m, "features": name, "negatives": nt,
                                  "roc_auc": roc_auc_score(df.label[sub], p[sub.values])})
        print(f"no road       {m:<14} ROC AUC {metrics[-1]['roc_auc']:.3f}  PR AUC {metrics[-1]['pr_auc']:.3f}", flush=True)

    pd.DataFrame(metrics).round(4).to_csv(f"{OUT}/cv_metrics.csv", index=False)
    pd.DataFrame(thr_rows).round(4).to_csv(f"{OUT}/threshold_table.csv", index=False)
    pd.DataFrame(road_rows).round(4).to_csv(f"{OUT}/road_check.csv", index=False)
    imp_df = pd.DataFrame(imp_all).round(5).sort_values("xgboost", ascending=False)
    imp_df.to_csv(f"{OUT}/permutation_importance.csv", index_label="feature")
    pd.concat([df[["id", "label", "neg_type", "state", "event_date"]], pd.DataFrame(oof_cols).round(5)],
              axis=1).to_csv(f"{OUT}/oof_predictions.csv", index=False)

    # ---- figures ----
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    for m in models:
        p = oof_cols[f"{m}__by_year"]
        fpr, tpr, _ = roc_curve(df.label, p)
        pr, rc, _ = precision_recall_curve(df.label, p)
        ax[0].plot(fpr, tpr, label=f"{m} (AUC {roc_auc_score(df.label, p):.2f})")
        ax[1].plot(rc, pr, label=f"{m} (AP {average_precision_score(df.label, p):.2f})")
    ax[0].plot([0, 1], [0, 1], "k:", lw=0.8)
    ax[0].set(xlabel="False-alarm rate (all negatives)", ylabel="Hit rate", title="ROC, year-blocked CV")
    ax[1].set(xlabel="Hit rate", ylabel="Precision (depends on sample ratio)", title="Precision-recall, year-blocked CV")
    for a in ax:
        a.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig_roc_pr.png", dpi=150)

    top = imp_df.head(15)
    fig, ax = plt.subplots(figsize=(7, 5))
    top[::-1].plot.barh(ax=ax)
    ax.set(xlabel="Drop in ROC AUC when the feature is shuffled", title="Permutation importance (top 15, year CV)")
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig_importance.png", dpi=150)

    th = pd.DataFrame(thr_rows)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for m in models:
        s = th[(th.model == m) & (th.cv == "by_year")]
        ax.plot(s.threshold, s.hit_rate, "-o", label=f"{m}: hit rate")
        ax.plot(s.threshold, s.false_alarm_rate_type1, "--", label=f"{m}: false alarms, safe days")
    ax.set(xlabel="Threshold", ylabel="Share", title="Hit rate vs false-alarm rate (year CV)")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig_thresholds.png", dpi=150)
    print("done; outputs in", OUT)


if __name__ == "__main__":
    main()
