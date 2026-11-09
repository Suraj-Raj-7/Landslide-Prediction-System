"""Phase C, step 10: partial dependence, a physics check of the live model.

PURPOSE
  A partial dependence curve shows how the model's average score changes
  when one input is varied over its range while all other inputs keep their
  observed values. If the model has learned sensible physics, risk should
  rise with antecedent rain and with slope (up to very steep rock faces,
  where little soil is left to slide).

  Model: the live model (rf_roads_live_v1, 28 features), fitted on all rows.
  Inputs shown: rain on the day, 7-day rain, 30-day rain, slope. The curves
  span the 5th-95th percentile of each input; the rug marks show where the
  training data actually lie.

INPUTS   models/rf_roads_live_v1.joblib, data/phaseB/training_table_v1.csv
OUTPUTS  docs/figures/pdp_<feature>.png, docs/figures/pdp_panel.png,
         data/phaseC/partial_dependence.csv
RUN      .venv/Scripts/python -W ignore src/phaseC_10_partial_dependence.py
"""
import json
import os

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.inspection import partial_dependence

FEATURES = {"imerg_d0": "Rain on the day (mm, IMERG)",
            "imerg_ant7d": "Rain in the 7 days before (mm, IMERG)",
            "imerg_ant30d": "Rain in the 30 days before (mm, IMERG)",
            "slope_deg": "Slope (degrees)"}


def main():
    os.makedirs("docs/figures", exist_ok=True)
    model = joblib.load("models/rf_roads_live_v1.joblib")
    cols = json.load(open("models/rf_roads_live_v1_meta.json"))["features_in_order"]
    df = pd.read_csv("data/phaseB/training_table_v1.csv")
    X = df[cols]

    rows = []
    fig, axes = plt.subplots(1, 4, figsize=(16, 3.8), sharey=True)
    for ax, (f, label) in zip(axes, FEATURES.items()):
        pd_res = partial_dependence(model, X, [f], percentiles=(0.05, 0.95), grid_resolution=40, kind="average")
        x, y = pd_res["grid_values"][0], pd_res["average"][0]
        rows += [{"feature": f, "value": a, "average_score": b} for a, b in zip(x, y)]
        for target in (ax, None):
            if target is None:                      # single-feature figure
                f1, target = plt.subplots(figsize=(5, 3.8))
            target.plot(x, y, lw=2, color="#1f6f8b")
            target.plot(X[f].clip(x.min(), x.max()), [y.min() - 0.01] * len(X), "|", color="grey", alpha=0.15)
            target.set_xlabel(label)
            target.set_ylabel("Average model score")
            target.grid(alpha=0.3)
            if target is not ax:
                f1.tight_layout()
                f1.savefig(f"docs/figures/pdp_{f}.png", dpi=150)
                plt.close(f1)
    fig.suptitle("Partial dependence, live model (28 features)")
    fig.tight_layout()
    fig.savefig("docs/figures/pdp_panel.png", dpi=150)
    pd.DataFrame(rows).round(4).to_csv("data/phaseC/partial_dependence.csv", index=False)

    # Short summary: score at the low, middle and high end of each curve
    s = pd.DataFrame(rows)
    for f in FEATURES:
        g = s[s.feature == f]
        print(f"{f:<14} low {g.value.iloc[0]:8.1f} -> {g.average_score.iloc[0]:.3f} | "
              f"mid {g.value.iloc[len(g) // 2]:8.1f} -> {g.average_score.iloc[len(g) // 2]:.3f} | "
              f"high {g.value.iloc[-1]:8.1f} -> {g.average_score.iloc[-1]:.3f} | "
              f"max score {g.average_score.max():.3f} at {g.value.iloc[g.average_score.argmax()]:.1f}")


if __name__ == "__main__":
    main()
