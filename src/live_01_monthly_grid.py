"""Live system, step 1 (monthly): the HP grid file used by every daily run.

WHAT IT MAKES
  One file, data/live/grid_live.csv.gz, with one row per 1 km cell of HP
  (55,253 cells): the fixed features (terrain, rock, roads, land cover...),
  the district, and the vegetation feature ndvi_pre365 (median NDVI over
  the past year). The daily run reads this file and only adds rain.

WHY MONTHLY, NOT DAILY
  Computing vegetation for all cells takes GEE about 40 minutes, and it
  hardly changes: moving its 365-day window by 30 / 60 / 90 days changed it
  by a median of 0.003 / 0.007 / 0.010 on 150 HP landslide points, against a
  spread of 0.19 between places (test of 6 Nov 2026, CHANGELOG). So it is
  refreshed once a month; the window ends the day before the refresh date,
  so no future data is used.

WHY A FILE
  The daily run (on GitHub) then needs no access to private GEE assets; it
  only reads public datasets (IMERG, GFS, ERA5-Land).

HOW TO RUN (two steps, once a month)
  .venv/Scripts/python -W ignore src/live_01_monthly_grid.py submit     # starts 8 GEE exports (~40 min)
  .venv/Scripts/python -W ignore src/live_01_monthly_grid.py download   # when they are done: writes the file
OUTPUTS  users/rajsuraj777/live/grid_ndvi_<YYYYMM>_a ... _h (GEE assets),
         data/live/grid_live.csv.gz, data/live/grid_live_info.json
"""
import datetime as dt
import json
import os
import sys

import ee

ee.Initialize(project="idyllic-return-468714-j4")
import pandas as pd  # noqa: E402

import vegetation as VG  # noqa: E402
from phaseD_02_storm_features import add_district  # noqa: E402

FOLDER = "users/rajsuraj777/live"
OUT = "data/live/grid_live.csv.gz"


def submit():
    today = dt.date.today().isoformat()          # NDVI window: the 365 days before today
    tag = today[:7].replace("-", "")
    try:
        ee.data.getAsset(FOLDER)
    except ee.EEException:
        ee.data.createAsset({"type": "FOLDER"}, FOLDER)
    for c in "abcdefgh":
        pts = ee.FeatureCollection(f"users/rajsuraj777/hp_grid_static_v1_{c}").map(lambda f: f.set("event_date", today))
        out = VG.extract(add_district(pts), "event_date", 30)
        name = f"grid_ndvi_{tag}_{c}"
        task = ee.batch.Export.table.toAsset(collection=out, description=name, assetId=f"{FOLDER}/{name}")
        task.start()
        print(f"{name}: NDVI window ends {today} (exclusive), task {task.id}")
    os.makedirs("data/live", exist_ok=True)
    json.dump({"tag": tag, "ndvi_window_ends": today}, open("data/live/grid_pending.json", "w"))


def download():
    info = json.load(open("data/live/grid_pending.json"))
    parts = [ee.data.computeFeatures({"expression": ee.FeatureCollection(f"{FOLDER}/grid_ndvi_{info['tag']}_{c}"),
                                      "fileFormat": "PANDAS_DATAFRAME"}) for c in "abcdefgh"]
    g = pd.concat(parts, ignore_index=True).drop(columns=["geo", "event_date"], errors="ignore")
    keep = ["id", "lon", "lat", "district"] + [c for c in g.columns if c not in ("id", "lon", "lat", "district")]
    g[keep].to_csv(OUT, index=False)
    info.update({"cells": len(g), "columns": keep, "made": dt.datetime.now().isoformat(timespec="minutes")})
    json.dump(info, open("data/live/grid_live_info.json", "w"), indent=2)
    print(f"{OUT}: {len(g)} cells, {os.path.getsize(OUT) / 1e6:.1f} MB; NDVI window ends {info['ndvi_window_ends']}")


if __name__ == "__main__":
    {"submit": submit, "download": download}[sys.argv[1]]()
