"""Python mirror of GEE script Current/13_step2_drainage_roads_run.

Spot-checks the Step 2 image at known points, compares landslides with random
points, extracts at all positives_v5 (nulls stay null), writes a local CSV and
(with --export) starts the Drive export.
Usage: python -I 13_step2_drainage_roads_run.py OUT_DIR [--export]
"""
import csv
import sys
import time

import ee

import drainage_roads as DR

ee.Initialize(project="idyllic-return-468714-j4")
OUT_DIR = sys.argv[1]
STREAM_KM2 = 2   # calibrated 2026-10-20 against OSM streams (best mean F1, 4 test areas)
CRS, SCALE = "EPSG:32643", 30
POS = ee.FeatureCollection("users/rajsuraj777/positives_v5")
img = DR.image(STREAM_KM2)
META = ["id", "state", "admin_unit", "source", "tier", "lat", "lon", "event_date", "event_end"]


def fmt(v):
    return None if v is None else round(v)


# ---- 1. Spot-checks ----
spots = ee.FeatureCollection([
    ee.Feature(ee.Geometry.Point([77.1720, 31.1040]), {"name": "Shimla Mall Road (on road)"}),
    ee.Feature(ee.Geometry.Point([77.1090, 31.9565]), {"name": "Kullu NH-3 (on highway)"}),
    ee.Feature(ee.Geometry.Point([76.9295, 31.7095]), {"name": "Mandi, Beas river bank"}),
    ee.Feature(ee.Geometry.Point([78.3000, 32.5500]), {"name": "Remote Spiti massif"}),
    ee.Feature(ee.Geometry.Point([77.6500, 32.1000]), {"name": "Remote high ridge, Kullu"}),
])
for f in img.reduceRegions(spots, ee.Reducer.first(), SCALE, CRS).getInfo()["features"]:
    p = f["properties"]
    print(f'{p["name"]:<30}', {b: fmt(p.get(b)) for b in DR.BANDS})

# ---- 2. Extract at positives ----
sampled = img.reduceRegions(POS, ee.Reducer.first(), SCALE, CRS)
rows = [f["properties"] for f in sampled.getInfo()["features"]]
print("rows:", len(rows))
print(f'{"band":<19}{"nulls":>6}{"min":>9}{"median":>9}{"p90":>9}{"max":>9}')
for b in DR.BANDS:
    v = sorted(r[b] for r in rows if r.get(b) is not None)
    print(f"{b:<19}{len(rows) - len(v):>6}{v[0]:>9.0f}{v[len(v) // 2]:>9.0f}"
          f"{v[int(len(v) * .9)]:>9.0f}{v[-1]:>9.0f}")

# ---- 3. Landslides vs random points (same study area) ----
cfg_units = ["1811400B21086746745937", "1811400B3558497485804",
             "1811400B42025667129192", "1811400B23769854471902"]
gb = ee.FeatureCollection("WM/geoLab/geoBoundaries/600/ADM1")
study = gb.filter(ee.Filter.inList("shapeID", cfg_units)).geometry()
rnd = ee.FeatureCollection.randomPoints(study, 1500, 7, 100)
rr = [f["properties"] for f in img.reduceRegions(rnd, ee.Reducer.first(), SCALE, CRS).getInfo()["features"]]
for b in DR.BANDS:
    a = sorted(r[b] for r in rows if r.get(b) is not None)
    c = sorted(r[b] for r in rr if r.get(b) is not None)
    print(f"{b:<19} median landslides {a[len(a) // 2]:>7.0f} | random {c[len(c) // 2]:>7.0f}  (random nulls {1500 - len(c)})")

with open(f"{OUT_DIR}/positives_drainage_roads_v2.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, META + DR.BANDS, extrasaction="ignore")
    w.writeheader()
    w.writerows(sorted(rows, key=lambda r: r["id"]))
print("wrote positives_drainage_roads_v2.csv")

if "--export" in sys.argv:
    task = ee.batch.Export.table.toDrive(
        collection=sampled, description="positives_drainage_roads_v2",
        folder="ICTD_Landslides_Project", fileFormat="CSV", selectors=META + DR.BANDS)
    task.start()
    while task.status()["state"] in ("READY", "RUNNING"):
        time.sleep(10)
    print("drive export:", task.status()["state"], task.status().get("error_message", ""))
