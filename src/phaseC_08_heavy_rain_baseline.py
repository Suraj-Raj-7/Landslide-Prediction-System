"""Phase C, step 8: does the model beat a simple heavy-rain rule?

PURPOSE
  A baseline any official could apply without a model: warn when rain on
  the day reaches IMD's "heavy rain" category, 64.5 mm in 24 hours (IMD
  national bulletins: heavy 64.5-115.5 mm, very heavy 115.6-204.4 mm,
  extremely heavy >= 204.5 mm). Here "rain on the day" is IMERG over the
  IST day (imerg_d0), the same value the model sees.

  Fair comparison: the rule flags a certain share of same-place safe days
  (Type 1). Each model's threshold is set so it flags the SAME share of
  safe days; then we compare how many recorded landslides each catches.
  A second, stronger rain-only rule is added: rain on the day plus the 7
  days before (imerg_d0 + imerg_ant7d), with its threshold set to the same
  safe-day false-alarm rate.

  Model scores are out-of-fold (whole years held out), from:
    data/phaseC/oof_predictions.csv     38-feature model, real roads
    data/phaseC/road_neutral_oof.csv    38 and 28 features, real and road-neutral

OUTPUTS  data/phaseC/heavy_rain_baseline.csv
RUN      .venv/Scripts/python -W ignore src/phaseC_08_heavy_rain_baseline.py
"""
import numpy as np
import pandas as pd

IMD_HEAVY_MM = 64.5


def main():
    t = pd.read_csv("data/phaseB/training_table_v1.csv")
    rn = pd.read_csv("data/phaseC/road_neutral_oof.csv")
    assert (t.id.values == rn.id.values).all()          # same row order
    scores = {
        "Full model (38 features), real roads": rn["rf_38_features__real"].values,
        "Full model (38 features), road-neutral": rn["rf_38_features__neutral"].values,
        "Live model (28 features), real roads": rn["rf_28_live__real"].values,
        "Live model (28 features), road-neutral": rn["rf_28_live__neutral"].values,
    }
    rain7 = (t.imerg_d0 + t.imerg_ant7d).values

    rows = []
    for region, mask in [("All three states", np.ones(len(t), bool)), ("HP only", (t.state == "HP").values)]:
        pos = mask & (t.label == 1).values
        safe = mask & (t.neg_type == "same_place_safe_day").values
        rule = t.imerg_d0.values >= IMD_HEAVY_MM
        fa = rule[safe].mean()                           # the rule's safe-day false-alarm rate
        rows.append({"region": region, "method": f"Rule: rain on the day >= {IMD_HEAVY_MM} mm (IMD heavy)",
                     "safe_days_flagged": fa, "slides_caught": rule[pos].mean(),
                     "n_slides": int(pos.sum()), "n_safe_days": int(safe.sum())})
        thr7 = np.quantile(rain7[safe], 1 - fa)
        rows.append({"region": region, "method": f"Rule: rain on the day + 7 days before >= {thr7:.0f} mm",
                     "safe_days_flagged": (rain7[safe] >= thr7).mean(), "slides_caught": (rain7[pos] >= thr7).mean(),
                     "n_slides": int(pos.sum()), "n_safe_days": int(safe.sum())})
        for name, p in scores.items():
            thr = np.quantile(p[safe], 1 - fa)
            rows.append({"region": region, "method": name,
                         "safe_days_flagged": (p[safe] >= thr).mean(), "slides_caught": (p[pos] >= thr).mean(),
                         "n_slides": int(pos.sum()), "n_safe_days": int(safe.sum())})
    res = pd.DataFrame(rows).round(3)
    res.to_csv("data/phaseC/heavy_rain_baseline.csv", index=False)
    pd.set_option("display.width", 200)
    print(res.to_string(index=False))

    # ---- the same comparison over a range of strictness levels ----
    # "timing" test: landslides vs same-place safe days (where the rain rule is fair)
    # "full" test: landslides vs all negatives, incl. other slopes on storm days
    # (a rain rule cannot tell slopes apart within one rain cell)
    from sklearn.metrics import roc_auc_score
    methods = {"Rain on the day (rule family)": t.imerg_d0.values,
               "Rain on the day + 7 days before": rain7, **scores}
    curve = []
    for region, mask in [("All three states", np.ones(len(t), bool)), ("HP only", (t.state == "HP").values)]:
        pos = mask & (t.label == 1).values
        for test, negmask in [("timing", (t.neg_type == "same_place_safe_day").values),
                              ("full", (t.label == 0).values)]:
            neg = mask & negmask
            sub = pos | neg
            for name, p in methods.items():
                row = {"region": region, "test": test, "method": name,
                       "roc_auc": roc_auc_score(t.label.values[sub], p[sub])}
                for fa in [0.02, 0.05, 0.10, 0.16, 0.25]:
                    thr = np.quantile(p[neg], 1 - fa)
                    row[f"caught_at_{int(fa * 100)}pct_false_alarm"] = (p[pos] >= thr).mean()
                curve.append(row)
    curve = pd.DataFrame(curve).round(3)
    curve.to_csv("data/phaseC/heavy_rain_baseline_curve.csv", index=False)
    print("\n" + curve.to_string(index=False))


if __name__ == "__main__":
    main()
