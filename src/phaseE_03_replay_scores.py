"""Phase E, step 3: score every HP cell on every replay day with held-out-year models.

PURPOSE
  For each replay day (phaseE_01), the whole-HP features exported by phaseE_02
  are scored by models trained WITHOUT that day's year (criterion 3 in
  documentation §17.10), exactly as the storm map (phaseD_03) does:
    rf   the live Random Forest (28 features: IMERG + fixed)
    2p   the two-part model: WHERE (Random Forest, no rain) x WHEN (logistic
         regression on log rain), phaseC_11
  each with road-neutral road distances (main map) and real ones.
  Only scores are saved here; levels and the district rule are applied in
  phaseE_04, so they can be compared without rescoring.

  Models are trained once per held-out year and reused for all days of
  that year. Downloaded features are not kept (about 15 MB per day); only a
  compact per-cell score file per day.

  Inputs per day: the year's grid (fixed features, district, NDVI; phaseE_02)
  plus IMERG rain for that day, computed with the same function as training
  (dynamic.image_for_date) but read at IMERG's own 0.1 deg pixels (one small
  request per day) and given to each cell from the pixel that contains it.
  This matches the point extraction used in training except for cells right
  at a pixel edge (checked against the 14 Aug 2023 export; see check_imerg).

INPUTS   users/rajsuraj777/replays/grid_ndvi_<YYYY>_a ... _h, data/phaseE/replay_dates.csv,
         data/phaseB/training_table_v1.csv, models/rf_roads_live_v1_meta.json
OUTPUTS  data/phaseE/scores/<YYYY-MM-DD>.csv.gz
         (id, lon, lat, district, dist_road_m, imerg_d0, rf_neutral, rf_real, 2p_neutral, 2p_real)
RUN      .venv/Scripts/python -W ignore src/phaseE_03_replay_scores.py
"""
import json
import os

import ee
import numpy as np
import pandas as pd

from phaseC_01_train_compare import CAT, ROAD, make_model
from phaseC_11_two_part_model import IMERG

ee.Initialize(project="idyllic-return-468714-j4")
import dynamic as DY  # noqa: E402  (after Initialize: the module builds EE objects)
FOLDER = "users/rajsuraj777/replays"
OUT_DIR = "data/phaseE/scores"


HP_BOX = [75.4, 30.2, 79.2, 33.4]   # lon/lat box around HP, with margin
IMERG_PROJ = ee.ImageCollection("NASA/GPM_L3/IMERG_V07").first().projection()
ERA5_PROJ = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").first().projection()
# Dated inputs read per day, each at its own native grid:
#   IMERG rain features (0.1 deg IMERG grid) and the ERA5-Land glacier flag
#   (era5_glacier, from snow water equivalent; ERA5-Land's own 0.1 deg grid).
DAILY = [(IMERG, IMERG_PROJ), (["era5_glacier"], ERA5_PROJ)]


def load_year_grid(year):
    """Fixed features + district + NDVI for all HP cells (phaseE_02 assets)."""
    parts = [ee.data.computeFeatures({"expression": ee.FeatureCollection(f"{FOLDER}/grid_ndvi_{year}_{c}"),
                                      "fileFormat": "PANDAS_DATAFRAME"}) for c in "abcdefgh"]
    return pd.concat(parts, ignore_index=True).drop(columns=["geo"], errors="ignore")


def pixels(date, bands, proj):
    """Values of some dynamic.image_for_date bands at every native pixel over HP."""
    img = DY.image_for_date(date).select(bands)
    fc = img.sample(region=ee.Geometry.Rectangle(HP_BOX), projection=proj, geometries=True)
    df = ee.data.computeFeatures({"expression": fc, "fileFormat": "PANDAS_DATAFRAME"})
    xy = np.array([g["coordinates"] for g in df.geo])
    return df[bands].values, xy


def add_daily(grid, date):
    """Give each cell the values of the pixel that contains it, for each daily input."""
    # Training read these with reduceRegions(scale=1000) in EPSG:4326: each point
    # is first snapped to the centre of its 1000 m (0.0089831 deg) sampling
    # pixel, and the image is read there. Do the same, so edge cells match.
    step = 1000 / 111319.490793
    cells = (np.floor(grid[["lon", "lat"]].values / step) + 0.5) * step
    out = grid.copy()
    for bands, proj in DAILY:
        vals, xy = pixels(date, bands, proj)
        near = np.argmin((cells[:, None, 0] - xy[None, :, 0]) ** 2 + (cells[:, None, 1] - xy[None, :, 1]) ** 2, axis=1)
        out[bands] = vals[near]
    return out


def check_imerg():
    """Compare with the full point export of 14 Aug 2023 (phaseD_02, data/phaseD)."""
    ref = pd.read_csv("data/phaseD/storm_20230814_v2_features.csv")
    cols = [c for bands, _ in DAILY for c in bands]
    mine = add_daily(ref.drop(columns=cols), "2023-08-14")
    for c in cols:
        d = (mine[c] - ref[c]).abs()
        print(f"{c}: identical {np.mean(d < 0.01):.4f}, max diff {d.max():.2f}, corr {np.corrcoef(mine[c], ref[c])[0, 1]:.5f}")


def train_year(t, features, year):
    """All models for one held-out year, plus the road-neutral road distances."""
    train = t[pd.to_datetime(t.event_date).dt.year != year]
    num = [c for c in features if c not in CAT]
    cat = [c for c in features if c in CAT]
    rf = make_model("random_forest", num, cat).fit(train[features], train.label)
    where = [c for c in features if c not in IMERG]
    trw = train[train.neg_type.isin(["positive", "similar_place_storm_day"])]
    trn = train[train.neg_type.isin(["positive", "same_place_safe_day"])]
    m_where = make_model("random_forest", [c for c in where if c not in CAT], [c for c in where if c in CAT]) \
        .fit(trw[where], trw.label)
    m_when = make_model("logistic", IMERG, []).fit(trn[IMERG], trn.label)
    road_median = train[train.label == 1][ROAD].median()

    def score(X):
        return {"rf": rf.predict_proba(X[features])[:, 1],
                "2p": m_where.predict_proba(X[where])[:, 1] * m_when.predict_proba(X[IMERG])[:, 1]}
    return score, road_median


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    features = json.load(open("models/rf_roads_live_v1_meta.json"))["features_in_order"]
    t = pd.read_csv("data/phaseB/training_table_v1.csv")
    dates = sorted(pd.read_csv("data/phaseE/replay_dates.csv").date.unique())
    todo = [d for d in dates if not os.path.exists(f"{OUT_DIR}/{d}.csv.gz")]
    print(f"{len(todo)} of {len(dates)} days to score", flush=True)
    models, grids = {}, {}
    for d in todo:
        year = int(d[:4])
        if year not in models:
            models[year] = train_year(t, features, year)
            print(f"models trained without {year}", flush=True)
        score, road_median = models[year]
        if year not in grids:
            try:
                grids[year] = load_year_grid(year)
            except ee.EEException as e:   # export not finished yet: skipped, picked up on the next run
                print(f"{d}: grid for {year} not ready ({str(e)[:80]})", flush=True)
                grids[year] = None
        if grids[year] is None:
            continue
        g = add_daily(grids[year], d)
        real = score(g)
        gn = g.copy()
        for c in ROAD:
            gn[c] = road_median[c]
        neutral = score(gn)
        out = g[["id", "lon", "lat", "district", "dist_road_m", "imerg_d0"]].copy()
        for m in ["rf", "2p"]:
            out[f"{m}_neutral"], out[f"{m}_real"] = neutral[m], real[m]
        out.round(4).to_csv(f"{OUT_DIR}/{d}.csv.gz", index=False)
        print(f"{d}: {len(out)} cells scored", flush=True)


if __name__ == "__main__":
    import sys
    check_imerg() if "--check" in sys.argv else main()
