"""Phase C, step 9: why does rain alone beat the model at telling WHEN?

PURPOSE
  phaseC_08 showed that rain on the day alone separates landslide days from
  same-place safe days better (ROC AUC 0.82) than the trained models
  (0.68-0.78). Suspected reason: Type 2 negatives share the storm day, so
  their rain is as heavy as the positives'; trained on all negatives, the
  model learns that rain alone does not separate the classes and gives it
  less weight.

  Diagnostic: the same live Random Forest (28 features), year-blocked CV,
  trained ONLY on positives vs same-place safe days (Type 1). If this model
  reads timing as well as the rain rule, the cause is the mix of negatives,
  and the fix is to give the "when" signal its own part of the model.

INPUTS   data/phaseB/training_table_v1.csv
OUTPUTS  data/phaseC/timing_diagnostic.csv
RUN      .venv/Scripts/python -W ignore src/phaseC_09_timing_diagnostic.py
"""
import pandas as pd
from sklearn.metrics import roc_auc_score

from phaseC_01_train_compare import DROP, META, cross_validate
from phaseC_07_train_live import CHIRPS, ERA5


def main():
    df = pd.read_csv("data/phaseB/training_table_v1.csv")
    live = [c for c in df.columns if c not in META + DROP + CHIRPS + ERA5]
    t1 = df[df.neg_type.isin(["positive", "same_place_safe_day"])].reset_index(drop=True)
    years = pd.to_datetime(t1.event_date).dt.year.values
    p, _ = cross_validate(t1, live, years, "random_forest")
    hp = (t1.state == "HP").values
    rows = [{"model": "Live RF trained on positives vs Type 1 only", "region": "all",
             "roc_auc_timing": roc_auc_score(t1.label, p)},
            {"model": "Live RF trained on positives vs Type 1 only", "region": "HP",
             "roc_auc_timing": roc_auc_score(t1.label[hp], p[hp])},
            {"model": "Rain on the day alone", "region": "all", "roc_auc_timing": roc_auc_score(t1.label, t1.imerg_d0)},
            {"model": "Rain on the day alone", "region": "HP", "roc_auc_timing": roc_auc_score(t1.label[hp], t1.imerg_d0[hp])}]
    res = pd.DataFrame(rows).round(3)
    res.to_csv("data/phaseC/timing_diagnostic.csv", index=False)
    print(res.to_string(index=False))


if __name__ == "__main__":
    main()
