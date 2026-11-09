"""Phase D, step 1: fixed features for every 1 km cell in Himachal Pradesh.

PURPOSE
  The daily run scores a fixed set of points. Their fixed features (terrain,
  drainage and roads, faults, lithology, geomorphology, land cover) do not
  change with date, so they are computed once here and stored in GEE.
  Points: the centre of every 1 km cell of a UTM 43N grid inside HP
  (55,253 cells). Real road distances are kept, so cells more than 500 m
  from a motorable road can be marked "lower confidence".

  The features come from stack.extract_static(), the same code used to build
  the training data, so training and prediction cannot drift apart.

  The job is split into 8 north-south latitude strips that run in parallel
  on Google's servers; the laptop can be off once they are submitted.

INPUTS
  geoBoundaries ADM1 (HP boundary), data/step3/lithology_mapping_v1.csv,
  and the GEE assets used by the feature modules (roads, faults, lithology,
  geomorphology).

OUTPUTS (new GEE table assets; nothing overwritten)
  users/rajsuraj777/hp_grid_static_v1_a ... _h
  Each point: id ("c_<col>_<row>" in the 1 km grid), col, row, lon, lat,
  and the 20 fixed features.

RUN
  .venv/Scripts/python -W ignore src/phaseD_01_static_grid.py            (count only)
  .venv/Scripts/python -W ignore src/phaseD_01_static_grid.py --submit   (start the 8 jobs)
"""
import sys

import ee

ee.Initialize(project="idyllic-return-468714-j4")   # before the imports: modules build EE objects
import land_cover as LC  # noqa: E402
import stack as ST       # noqa: E402

LITH_CSV = "data/step3/lithology_mapping_v1.csv"
HP_ID = "1811400B21086746745937"
ASSET = "users/rajsuraj777/hp_grid_static_v1"
N_STRIPS = 8
LAT_MIN, LAT_MAX = 30.3, 33.3    # HP lies between about 30.4 and 33.2 N

hp = ee.FeatureCollection("WM/geoLab/geoBoundaries/600/ADM1").filter(ee.Filter.eq("shapeID", HP_ID)).first().geometry()
grid = ee.Projection("EPSG:32643").atScale(1000)

# One point per 1 km cell centre inside HP, with the cell's column/row index
# (pixel indices, not metres) and its centre coordinates
cells = ee.Image(1).rename("one") \
    .addBands(ee.Image.pixelCoordinates(grid).int().rename(["col", "row"])) \
    .addBands(ee.Image.pixelLonLat()) \
    .reproject(grid).clip(hp)
points = cells.sample(region=hp, projection=grid, scale=1000, geometries=True, tileScale=4) \
    .map(lambda f: f.set("id", ee.String("c_").cat(ee.Number(f.get("col")).format("%d"))
                         .cat("_").cat(ee.Number(f.get("row")).format("%d")),
                         "lon", f.get("longitude"), "lat", f.get("latitude")))

META = ["id", "col", "row", "lon", "lat"]
FEATURES = ST.static_bands() + LC.BANDS

if "--submit" not in sys.argv:
    print("points in HP:", points.size().getInfo())
    print("features:", len(FEATURES), FEATURES)
    sys.exit()

step = (LAT_MAX - LAT_MIN) / N_STRIPS
for k in range(N_STRIPS):
    lo, hi = LAT_MIN + k * step, LAT_MIN + (k + 1) * step
    part = points.filter(ee.Filter.And(ee.Filter.gte("lat", lo), ee.Filter.lt("lat", hi)))
    out = ST.extract_static(part, LITH_CSV).select(META + FEATURES)
    name = f"hp_grid_static_v1_{chr(97 + k)}"
    task = ee.batch.Export.table.toAsset(collection=out, description=name, assetId=f"{ASSET}_{chr(97 + k)}")
    task.start()
    print(f"strip {chr(97 + k)}: lat {lo:.3f}-{hi:.3f} -> {ASSET}_{chr(97 + k)} task {task.id}", flush=True)
