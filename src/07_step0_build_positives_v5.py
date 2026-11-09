"""Step 0 fixes: build positives_v5 from positives_v4_corrected.csv.

Applies coordinate fixes, date-parse fixes, duplicate drops and unfixable
drops; tags each point with its geoBoundaries v6 ADM1 unit; writes
positives_v5.csv and step0_changes_log.csv; optionally uploads the asset.

Usage: python -I 07_step0_build_positives_v5.py V4_CSV OUT_DIR [--upload]
"""
import csv
import sys
import time

import ee

V4_CSV, OUT_DIR = sys.argv[1], sys.argv[2]
UPLOAD = "--upload" in sys.argv
ASSET_ID = "users/rajsuraj777/positives_v5"

# geoBoundaries v6 ADM1 units, selected by shapeID (names contain non-ASCII
# characters such as 'Himāchal Pradesh', so name matching is fragile).
GB_UNITS = {
    "HP": "1811400B21086746745937",
    "UK": "1811400B3558497485804",
    "JK_UT": "1811400B42025667129192",
    "Ladakh": "1811400B23769854471902",
}
LABEL_OK = {"HP": {"HP"}, "UK": {"UK"}, "JK": {"JK_UT", "Ladakh"}}

rows = list(csv.DictReader(open(V4_CSV, encoding="utf-8")))
log = []


def find(rid):
    return next(r for r in rows if r["id"] == rid)


def note(action, rid, field, old, new, reason):
    log.append({"action": action, "id": rid, "field": field, "old": old, "new": new, "reason": reason})


# ---- 1. Coordinate fixes (evidence: Survey of India 15' toposheet in slide_no) ----
r = find("BH_8569")
note("fix", r["id"], "lon", r["lon"], "77.15313889",
     "Labelled HP/Solan, slide H.P./SOL/53F01/2018. Sheet 53F/1 spans 30.75-31.00N, "
     "77.00-77.25E; lat 30.997 fits, lon 75.153 lies in Punjab. Leading digit typo 75->77.")
r["lon"] = "77.15313889"

r = find("BH_35971")
note("fix", r["id"], "lat", r["lat"], "30.94500556",
     "Labelled UK/Uttarkashi, slide UK/Uttarkashi/53F_13/2019/05. Sheet 53F/13 spans "
     "30.75-31.00N, 77.75-78.00E; lon 77.853 fits, lat 31.945 lies in Kinnaur (HP). Digit typo 31->30.")
r["lat"] = "30.94500556"

# ---- 2. Date-parse fixes ----
r = find("BH_35861_1")
note("fix", r["id"], "event_date/event_end", r["event_date"], "2025-08-06",
     "Raw '06 August at 07.30 hrs, 18 August at 07.35 hrs and 26 August 2025 at 09.15hrs'. "
     "Parser read '18 August' as year 2018. All three dates are 2025.")
r["event_date"] = r["event_end"] = "2025-08-06"
new = dict(r)
new.update({"id": "BH_35861_3", "event_date": "2025-08-18", "event_end": "2025-08-18"})
rows.insert(rows.index(r) + 1, new)
note("add", "BH_35861_3", "event_date/event_end", "", "2025-08-18",
     "Third date in the same BH_35861 record, lost by the parser.")

# ---- 3. Unfixable rows: drop ----
DROPS = {
    "BH_8460_2": "Date 2025-08-01 came from a lone '1' in '27 October 2023, 1, 26 August 2025'. "
                 "The intended date cannot be recovered.",
    # Duplicates (same date; Bhusanket < 5 m apart = re-entered record,
    # NASA < 100 m apart = same event reported twice; NASA has no slide IDs).
    "NASA_5,088": "Duplicate of NASA_5,086: same date 2013-07-12, identical coordinates.",
    "NASA_5,234": "Duplicate of NASA_5,233: same date 2013-07-29, identical coordinates.",
    "NASA_3,895": "Duplicate of NASA_3,894: same date 2011-08-07, 29 m apart.",
    "BH_10901": "Duplicate of BH_10952: same date 2025-08-17, 0.9 m apart. BH_10901 has the "
                "numeric re-entry slide id 3436; BH_10952 has the full id JK/KAT/43P11/2025/049.",
    "BH_11272": "Duplicate of BH_10955: same date 2025-08-17, 0.9 m apart. BH_11272 has the "
                "numeric re-entry slide id 3491; BH_10955 has the full id JK/KAT/43P11/2025/052.",
}
for rid, why in DROPS.items():
    r = find(rid)
    note("drop", rid, "row", f'{r["state"]} {r["event_date"]} {r["lat"]},{r["lon"]}', "", why)
    rows.remove(r)

# ---- 4. Kept after review (logged so the report can cite them) ----
note("keep", "BH_35882", "event_date", "2005-07-29", "2005-07-29",
     "Slide no. says 2025 but the same 2025 survey series records past events "
     "(BH_35884 2015-08-29, BH_35885 2015-07-27). Raw '29 July and 30 July 2005' is unambiguous.")
note("keep", "12 NASA points in Ladakh", "state", "JK", "JK",
     "Inside geoBoundaries Ladakh: 9 near Leh (7 are the 2010-08-06 Leh cloudburst) and "
     "3 in Kargil district (NASA_4823, NASA_11484, NASA_5244). Real events. Kept with "
     "admin_unit=Ladakh so they can be filtered later.")

# ---- 5. Clean IDs: GEE upload turned 'NASA_9,892' into 'NASA_9_892'. Use NASA_9892. ----
for r in rows:
    if "," in r["id"]:
        r["id"] = r["id"].replace(",", "")
note("rename", "all NASA ids", "id", "NASA_9,892", "NASA_9892", "Comma removed (GEE rewrote it to '_').")

# ---- 6. Tag geoBoundaries ADM1 unit in Earth Engine ----
ee.Initialize(project="idyllic-return-468714-j4")
gb = ee.FeatureCollection("WM/geoLab/geoBoundaries/600/ADM1")
units = ee.FeatureCollection([
    ee.Feature(gb.filter(ee.Filter.eq("shapeID", sid)).first().geometry(), {"admin_unit": name})
    for name, sid in GB_UNITS.items()
])
COLS = ["id", "sl_no", "lat", "lon", "event_date", "event_end", "range_days", "state",
        "source", "tier", "also_in_glc", "slide_no"]


def to_feature(r):
    props = {k: r[k] for k in COLS}
    props["lat"], props["lon"] = float(r["lat"]), float(r["lon"])
    props["range_days"] = int(r["range_days"])
    props["slide_no"] = r["slide_no"].replace("\n", "")
    return ee.Feature(ee.Geometry.Point([props["lon"], props["lat"]]), props)


fc = ee.FeatureCollection([to_feature(r) for r in rows])
joined = ee.Join.saveFirst("u").apply(
    fc, units, ee.Filter.intersects(leftField=".geo", rightField=".geo", maxError=10))
got = ee.FeatureCollection(joined).map(
    lambda f: ee.Feature(None, {"id": f.get("id"), "unit": ee.Feature(f.get("u")).get("admin_unit")})
).getInfo()["features"]
unit_of = {g["properties"]["id"]: g["properties"]["unit"] for g in got}
for r in rows:
    r["admin_unit"] = unit_of.get(r["id"], "none")
    r["slide_no"] = r["slide_no"].replace("\n", "")

bad = [r for r in rows if r["admin_unit"] not in LABEL_OK[r["state"]]]
print("rows:", len(rows))
for s in ("HP", "UK", "JK"):
    print(f"  {s}: {sum(r['state'] == s for r in rows)}")
print("admin_unit:", {u: sum(r["admin_unit"] == u for r in rows) for u in [*GB_UNITS, "none"]})
print("label/unit mismatches:", len(bad))
for r in bad:
    print(f'  {r["id"]} label={r["state"]} unit={r["admin_unit"]} {r["lat"]},{r["lon"]} {r["slide_no"]}')

# ---- 7. Write CSVs ----
out_cols = COLS + ["admin_unit"]
with open(f"{OUT_DIR}/positives_v5.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, out_cols, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
with open(f"{OUT_DIR}/step0_changes_log.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, ["action", "id", "field", "old", "new", "reason"])
    w.writeheader()
    w.writerows(log)
print("wrote positives_v5.csv and step0_changes_log.csv")

# ---- 8. Upload as a new asset (never overwrites v4) ----
if UPLOAD:
    if bad:
        sys.exit("Not uploading: fix the mismatches above first.")
    final = ee.FeatureCollection([
        to_feature(r).set("admin_unit", r["admin_unit"]) for r in rows])
    task = ee.batch.Export.table.toAsset(collection=final, description="positives_v5",
                                         assetId=ASSET_ID)
    task.start()
    while task.status()["state"] in ("READY", "RUNNING"):
        time.sleep(10)
    print("upload:", task.status()["state"], task.status().get("error_message", ""))
