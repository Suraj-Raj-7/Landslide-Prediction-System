"""Python mirror of GEE script Current/10_step1_terrain_run.

Spot-checks the terrain image at reference towns, extracts it at all
positives_v5 points (masked pixels stay null, no -9999), prints value
ranges and null counts, writes a local CSV and (with --export) starts the
Drive export. Usage: python -I 10_step1_terrain_run.py OUT_DIR [--export]
"""
import csv
import sys
import time

import ee

import terrain as T

ee.Initialize(project="idyllic-return-468714-j4")
OUT_DIR = sys.argv[1]
POS = ee.FeatureCollection("users/rajsuraj777/positives_v5")
img = T.terrain_image()
META = ["id", "state", "admin_unit", "source", "tier", "lat", "lon", "event_date", "event_end"]

# ---- 1. Reference towns (expected elevation from published values) ----
towns = ee.FeatureCollection([
    ee.Feature(ee.Geometry.Point([77.1734, 31.1048]), {"name": "Shimla (Ridge)", "expect_m": 2205}),
    ee.Feature(ee.Geometry.Point([77.1095, 31.9579]), {"name": "Kullu (Dhalpur)", "expect_m": 1220}),
    ee.Feature(ee.Geometry.Point([78.0418, 30.3243]), {"name": "Dehradun (Clock Tower)", "expect_m": 640}),
])
for f in img.reduceRegions(towns, ee.Reducer.first(), T.L, T.CRS).getInfo()["features"]:
    p = f["properties"]
    print(f'{p["name"]:<24} expect ~{p["expect_m"]} m  got {p["elevation_m"]:.0f} m  '
          f'slope {p["slope_deg"]:.1f}  tpi {p["tpi_500m"]:.0f}  twi {p["twi"]:.1f}')

# ---- 2. Extract at all positives (reduceRegions keeps every feature) ----
sampled = img.reduceRegions(POS, ee.Reducer.first(), T.L, T.CRS)
rows = [f["properties"] for f in sampled.getInfo()["features"]]
print("rows:", len(rows))
print(f'{"band":<13}{"nulls":>6}{"min":>11}{"mean":>11}{"max":>11}')
for b in T.BANDS:
    v = [r[b] for r in rows if r.get(b) is not None]
    print(f"{b:<13}{len(rows) - len(v):>6}{min(v):>11.4g}{sum(v) / len(v):>11.4g}{max(v):>11.4g}")

with open(f"{OUT_DIR}/positives_terrain_v2.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, META + T.BANDS, extrasaction="ignore")
    w.writeheader()
    w.writerows(sorted(rows, key=lambda r: r["id"]))
print("wrote positives_terrain_v2.csv")

# ---- 3. Drive export (same table) ----
if "--export" in sys.argv:
    task = ee.batch.Export.table.toDrive(
        collection=sampled, description="positives_terrain_v2", folder="ICTD_Landslides_Project",
        fileFormat="CSV", selectors=META + T.BANDS)
    task.start()
    while task.status()["state"] in ("READY", "RUNNING"):
        time.sleep(10)
    print("drive export:", task.status()["state"], task.status().get("error_message", ""))
