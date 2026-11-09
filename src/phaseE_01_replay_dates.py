"""Phase E, step 1: choose the replay days by a fixed rule, before any scoring.

PURPOSE
  The storm replays set the final alert levels and the district rule
  (criteria in documentation §17.10). To keep that honest, the days are
  chosen here by rules written down first, not by looking at the maps.

RULES
  Storm days   every HP date with >= 3 recorded landslides in the positives
               table (v5). One busy day is a "storm"; neighbouring busy days
               are kept as separate storm days.
  Day before   for each storm day D, also D-1, because criterion 1 counts a
               hit if the district is on Watch or higher on D or D-1.
  Quiet days   for each year that has a storm day: 2 random days in the
               monsoon (15 Jun - 30 Sep) with no recorded HP landslide within
               3 days either side (fixed seed). "Quiet" means no RECORDED
               slide; the inventory is incomplete, so some may not be truly
               quiet, which makes the quiet-day false alarm count an upper
               bound.

INPUTS   data/positives_features_v1_local.csv
OUTPUTS  data/phaseE/replay_dates.csv (date, role, storm_date, n_hp_slides)
RUN      .venv/Scripts/python -W ignore src/phaseE_01_replay_dates.py
"""
import os

import numpy as np
import pandas as pd

MIN_SLIDES = 3
QUIET_PER_YEAR = 2
QUIET_GAP_DAYS = 3
SEED = 20261106


def main():
    p = pd.read_csv("data/positives_features_v1_local.csv")
    hp = p[p.state == "HP"]
    per_day = hp.groupby("event_date").size()
    storms = sorted(per_day[per_day >= MIN_SLIDES].index)

    rows = [{"date": d, "role": "storm_day", "storm_date": d, "n_hp_slides": int(per_day[d])} for d in storms]
    for d in storms:
        b = (pd.Timestamp(d) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        rows.append({"date": b, "role": "day_before", "storm_date": d, "n_hp_slides": int(per_day.get(b, 0))})

    # Quiet days: monsoon days far (> 3 days) from any recorded HP slide
    slide_days = pd.to_datetime(hp.event_date.unique())
    rng = np.random.default_rng(SEED)
    for yr in sorted({int(d[:4]) for d in storms}):
        days = pd.date_range(f"{yr}-06-15", f"{yr}-09-30")
        far = [d for d in days if np.min(np.abs((slide_days - d).days)) > QUIET_GAP_DAYS]
        for d in sorted(rng.choice(far, QUIET_PER_YEAR, replace=False)):
            rows.append({"date": pd.Timestamp(d).strftime("%Y-%m-%d"), "role": "quiet_day",
                         "storm_date": "", "n_hp_slides": 0})

    out = pd.DataFrame(rows).sort_values(["date", "role"]).reset_index(drop=True)
    os.makedirs("data/phaseE", exist_ok=True)
    out.to_csv("data/phaseE/replay_dates.csv", index=False)
    print(out.to_string(index=False))
    print(f"\n{len(storms)} storm days, {out.date.nunique()} distinct dates to compute")


if __name__ == "__main__":
    main()
