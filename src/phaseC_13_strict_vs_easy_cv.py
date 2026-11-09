"""Phase C, step 13: how much does the testing method change the score?

PURPOSE
  Our scores come from a strict test: whole years are held out, so the model
  never sees the storm it is scored on. Many studies use an easier test:
  random rows are held out, so rows from the same storm (same day, nearby
  places, same weather) sit in both training and test data. Spatial and
  temporal dependence then makes the easy test look better than the model
  really is (Roberts et al. 2017; Brenning 2005).

  This script scores the SAME model recipes both ways, so the difference is
  due to the testing method only:
    - year-blocked 5-fold CV (our method; whole years held out)
    - event-date-blocked 5-fold CV (whole storm days held out)
    - random 5-fold CV (random rows, stratified by label)
  Models: single live model (28 features), single full model (38 features).
  Nothing is chosen from these results; they explain why our scores are what
  they are.

INPUTS   data/phaseB/training_table_v1.csv
OUTPUTS  data/phaseC/strict_vs_easy_cv.csv
RUN      .venv/Scripts/python -W ignore src/phaseC_13_strict_vs_easy_cv.py
"""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

from phaseC_01_train_compare import CAT, DROP, META, N_FOLDS, SEED, cross_validate, make_model
from phaseC_07_train_live import CHIRPS, ERA5


def random_cv(df, features):
    """Random rows held out (the easy test)."""
    num = [c for c in features if c not in CAT]
    cat = [c for c in features if c in CAT]
    X, y = df[features], df.label.values
    p = np.zeros(len(df))
    for tr, te in StratifiedKFold(N_FOLDS, shuffle=True, random_state=SEED).split(X, y):
        p[te] = make_model("random_forest", num, cat).fit(X.iloc[tr], y[tr]).predict_proba(X.iloc[te])[:, 1]
    return p


def main():
    df = pd.read_csv("data/phaseB/training_table_v1.csv")
    full = [c for c in df.columns if c not in META + DROP]
    live = [c for c in full if c not in CHIRPS + ERA5]
    hp = (df.state == "HP").values
    t1 = df.neg_type.isin(["positive", "same_place_safe_day"]).values
    rows = []
    for name, feats in [("Single live model (28)", live), ("Single full model (38)", full)]:
        tests = {"Whole years held out (ours)": cross_validate(df, feats, pd.to_datetime(df.event_date).dt.year.values, "random_forest")[0],
                 "Whole storm days held out": cross_validate(df, feats, df.event_date.values, "random_forest")[0],
                 "Random rows held out (easy)": random_cv(df, feats)}
        for test, p in tests.items():
            rows.append({"model": name, "test": test, "roc_auc_all": roc_auc_score(df.label, p),
                         "roc_auc_HP": roc_auc_score(df.label[hp], p[hp]),
                         "roc_auc_timing": roc_auc_score(df.label[t1], p[t1])})
            print(rows[-1], flush=True)
    pd.DataFrame(rows).round(3).to_csv("data/phaseC/strict_vs_easy_cv.csv", index=False)
    print(pd.DataFrame(rows).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
