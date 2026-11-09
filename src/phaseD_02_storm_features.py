"""Phase D, step 2: daily features for every HP grid point on one date.

PURPOSE
  Builds the full input for a whole-HP risk map on a chosen day: the fixed
  features already stored for the 55,253 grid points (phaseD_01) plus the
  dated features (NDVI over the past year, IMERG rain on the day and before),
  computed with the SAME functions used for the training data
  (vegetation.extract, dynamic.extract). Each point also gets its HP
  district name (geoBoundaries ADM2), for district alert levels.

  First use: 14 Aug 2023, the HP day with the most recorded landslides in the
  inventory (31), for the interim storm map. The same script later serves
  the storm replays (Phase E).

INPUTS   users/rajsuraj777/hp_grid_static_v1_a ... _h
OUTPUTS  users/rajsuraj777/storm_<YYYYMMDD>_a ... _h   (new GEE table assets)
RUN      .venv/Scripts/python -W ignore src/phaseD_02_storm_features.py 2023-08-14
"""
import sys

import ee

ee.Initialize(project="idyllic-return-468714-j4")   # before the imports: modules build EE objects
import dynamic as DY      # noqa: E402
import vegetation as VG   # noqa: E402

HP_ID = "1811400B21086746745937"
HP_DISTRICTS = ["Bilaspur", "Chamba", "Hamirpur", "Kangra", "Kinnaur", "Kullu", "Lahul & Spiti",
                "Mandi", "Shimla", "Sirmaur", "Solan", "Una"]

hp = ee.FeatureCollection("WM/geoLab/geoBoundaries/600/ADM1").filter(ee.Filter.eq("shapeID", HP_ID)).first().geometry()
districts = ee.FeatureCollection("WM/geoLab/geoBoundaries/600/ADM2").filterBounds(hp) \
    .filter(ee.Filter.inList("shapeName", HP_DISTRICTS))


def add_district(points):
    """Exact point-in-polygon lookup of the HP district. Outer join: cells that
    fall just outside every district outline (the state and district outlines
    differ slightly at the border) are kept as "unassigned", not dropped."""
    j = ee.Join.saveFirst("d", outer=True).apply(
        points, districts, ee.Filter.intersects(leftField=".geo", rightField=".geo", maxError=1))
    return ee.FeatureCollection(j).map(lambda f: f.set(
        "district", ee.Algorithms.If(f.get("d"), ee.Feature(f.get("d")).get("shapeName"), "unassigned"), "d", None))


def submit(date, tag, folder="users/rajsuraj777"):
    """Start one export task per grid strip (a..h) for one date.
    Asset names: <folder>/storm_<tag>_<strip>. Also used by phaseE_02."""
    ids = []
    for c in "abcdefgh":
        pts = ee.FeatureCollection(f"users/rajsuraj777/hp_grid_static_v1_{c}").map(lambda f: f.set("event_date", date))
        out = DY.extract(VG.extract(add_district(pts), "event_date", 30), "event_date", 1000)
        task = ee.batch.Export.table.toAsset(collection=out, description=f"storm_{tag}_{c}",
                                             assetId=f"{folder}/storm_{tag}_{c}")
        task.start()
        ids.append(task.id)
        print(f"strip {c} -> {folder}/storm_{tag}_{c} task {task.id}", flush=True)
    return ids


if __name__ == "__main__":
    DATE = sys.argv[1]
    TAG = DATE.replace("-", "") + (sys.argv[2] if len(sys.argv) > 2 else "")   # optional suffix, e.g. "_v2"
    submit(DATE, TAG)
