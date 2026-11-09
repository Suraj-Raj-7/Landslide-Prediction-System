"""Phase E, step 2: whole-HP grid with vegetation and district, once per replay year (GEE exports).

PURPOSE
  The replay days need, for all 55,253 HP cells, the fixed features, the
  district, NDVI over the past year (ndvi_pre365) and IMERG rain. This script
  exports the first three; IMERG is added per day in phaseE_03.

WHY ONE NDVI PER YEAR (decision 6 Nov 2026, with evidence)
  A first version exported everything per day (46 days x 8 strips). GEE ran
  the tasks one at a time at 3-11 minutes each (well over a day in total);
  timing showed NDVI is ~95% of the cost (259 s vs 13 s for IMERG on the same
  points). NDVI is a median over 365 days, so it barely moves when its window
  ends a few weeks earlier: on 150 HP landslide points, ending the window 30 /
  60 / 90 days earlier changed it by a median of 0.003 / 0.007 / 0.010
  (95th percentile 0.029 / 0.045 / 0.058; correlation >= 0.98), against a
  spread of 0.19 between places. So NDVI is computed once per year, with the
  window ending the day before that year's FIRST replay day: no later data
  enters any replay day (no leakage), and the largest gap is 91 days (2010).
  The cancelled per-day tasks are recorded in data/phaseE/replay_tasks.log.

INPUTS   data/phaseE/replay_dates.csv, users/rajsuraj777/hp_grid_static_v1_a ... _h
OUTPUTS  users/rajsuraj777/replays/grid_ndvi_<YYYY>_a ... _h (new GEE table assets)
         data/phaseE/replay_tasks.log
RUN      .venv/Scripts/python -W ignore src/phaseE_02_replay_features.py
"""
import ee

ee.Initialize(project="idyllic-return-468714-j4")
import pandas as pd  # noqa: E402

import vegetation as VG  # noqa: E402
from phaseD_02_storm_features import add_district  # noqa: E402

FOLDER = "users/rajsuraj777/replays"


def existing_assets():
    return {a["name"].split("/")[-1]
            for a in ee.data.listAssets({"parent": f"projects/earthengine-legacy/assets/{FOLDER}"})["assets"]}


def main():
    rd = pd.read_csv("data/phaseE/replay_dates.csv")
    ref = rd.assign(year=rd.date.str[:4]).groupby("year").date.min()   # first replay day per year
    have = existing_assets()
    with open("data/phaseE/replay_tasks.log", "a", encoding="utf-8") as log:
        for year, d in ref.items():
            for c in "abcdefgh":
                name = f"grid_ndvi_{year}_{c}"
                if name in have:
                    print(name, "exists, skipped")
                    continue
                pts = ee.FeatureCollection(f"users/rajsuraj777/hp_grid_static_v1_{c}").map(
                    lambda f: f.set("event_date", d))   # NDVI window ends the day before d
                out = VG.extract(add_district(pts), "event_date", 30)
                task = ee.batch.Export.table.toAsset(collection=out, description=name, assetId=f"{FOLDER}/{name}")
                task.start()
                log.write(f"ndvi {year} (window ends {d}) {c}\t{task.id}\n")
                print(f"{name} (NDVI window ends day before {d}) task {task.id}", flush=True)


if __name__ == "__main__":
    main()
