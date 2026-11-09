"""Python mirror of GEE script Current/05_step0_audit (Step 0 audit).

Runs the same checks through the Earth Engine Python API and prints results.
Also saves a PNG of the three state outlines with all positives, so the J&K
(GAUL level0) extent can be inspected. Usage: python -I 05_step0_audit.py OUT_DIR
"""
import json
import sys
import urllib.request

import ee

ee.Initialize(project="idyllic-return-468714-j4")
out_dir = sys.argv[1] if len(sys.argv) > 1 else "."

# ---- 1. State geometries, kept separate ----
admin0 = ee.FeatureCollection("FAO/GAUL/2015/level0")
admin1 = ee.FeatureCollection("FAO/GAUL/2015/level1")
hp = admin1.filter(ee.Filter.eq("ADM1_NAME", "Himachal Pradesh"))
uk = admin1.filter(ee.Filter.eq("ADM1_NAME", "Uttarakhand"))
jk = admin0.filter(ee.Filter.eq("ADM0_NAME", "Jammu and Kashmir"))
hpGeom, ukGeom, jkGeom = hp.geometry(), uk.geometry(), jk.geometry()

positives = ee.FeatureCollection("users/rajsuraj777/positives_v4_corrected")
chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")


def iso_count(field):
    def flag(f):
        v = ee.String(ee.Algorithms.String(f.get(field)))
        return f.set("iso_ok", v.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}$").size().gt(0))
    return positives.map(flag).filter(ee.Filter.eq("iso_ok", 1)).size()


latest_event = ee.Date("2026-07-07")
summary = ee.Dictionary({
    "match_counts": {"HP": hp.size(), "UK": uk.size(), "JK": jk.size()},
    "area_km2": {
        "HP": hpGeom.area(100).divide(1e6),
        "UK": ukGeom.area(100).divide(1e6),
        "JK": jkGeom.area(100).divide(1e6),
    },
    "jk_bounds": jkGeom.bounds(100).coordinates(),
    "n_positives": positives.size(),
    "by_state": positives.aggregate_histogram("state"),
    "by_source": positives.aggregate_histogram("source"),
    "by_tier": positives.aggregate_histogram("tier"),
    "also_in_glc": positives.aggregate_histogram("also_in_glc"),
    "raw_event_date_first5": positives.limit(5).aggregate_array("event_date"),
    "event_date_type": ee.Algorithms.ObjectType(positives.first().get("event_date")),
    "event_date_iso": iso_count("event_date"),
    "event_end_iso": iso_count("event_end"),
    "min_event_date": positives.aggregate_min("event_date"),
    "max_event_date": positives.aggregate_max("event_date"),
    "property_names": positives.first().propertyNames(),
    "chirps_latest": chirps.sort("system:time_start", False).first().date().format("YYYY-MM-dd"),
    "chirps_window_images": chirps.filterDate(latest_event.advance(-30, "day"),
                                              latest_event.advance(1, "day")).size(),
    "roads_n": ee.FeatureCollection("users/rajsuraj777/HP_roads_osm").size(),
    "litho_n": ee.FeatureCollection("users/rajsuraj777/HP_lithology").size(),
}).getInfo()
print(json.dumps(summary, indent=1))

# ---- 5. Point-in-state: actual polygon for every point ----
stateFC = ee.FeatureCollection([
    ee.Feature(hpGeom, {"actual_state": "HP"}),
    ee.Feature(ukGeom, {"actual_state": "UK"}),
    ee.Feature(jkGeom, {"actual_state": "JK"}),
])
stateGeoms = ee.Dictionary({"HP": hpGeom, "UK": ukGeom, "JK": jkGeom})
tagged = ee.Join.saveFirst("match").apply(
    positives, stateFC,
    ee.Filter.intersects(leftField=".geo", rightField=".geo", maxError=10))
inside = ee.FeatureCollection(tagged).map(
    lambda f: f.set("actual_state", ee.Feature(f.get("match")).get("actual_state")).set("match", None))
outside = positives.filter(ee.Filter.inList("id", inside.aggregate_array("id")).Not()) \
    .map(lambda f: f.set("actual_state", "none"))
allTagged = inside.merge(outside)
mismatches = allTagged.map(
    lambda f: f.set("label_ok", ee.Algorithms.IsEqual(f.get("state"), f.get("actual_state")))
).filter(ee.Filter.eq("label_ok", False)).map(
    lambda f: f.set("dist_to_label_state_m",
                    f.geometry().distance(ee.Geometry(stateGeoms.get(f.get("state"))), 10).round()))

print("Points by actual polygon:", allTagged.aggregate_histogram("actual_state").getInfo())
mm = mismatches.getInfo()["features"]
print("Mismatches:", len(mm))
for f in sorted(mm, key=lambda f: f["properties"]["id"]):
    p, (lon, lat) = f["properties"], f["geometry"]["coordinates"]
    print(f'  {p["id"]:<12} label={p["state"]} actual={p["actual_state"]:<4} '
          f'dist_to_label_m={p["dist_to_label_state_m"]:>7} lat={lat:.5f} lon={lon:.5f} '
          f'date={p["event_date"]} src={p["source"]}')

# ---- Map PNG: state outlines + positives (red) + mismatches (magenta) ----
region = hpGeom.union(ukGeom, 100).union(jkGeom, 100).bounds(100)
img = ee.Image().byte().paint(stateFC, 1, 2).visualize(palette=["000000"]) \
    .blend(ee.Image().byte().paint(hp, 1).visualize(palette=["ffcccc"], opacity=0.5)) \
    .blend(ee.Image().byte().paint(uk, 1).visualize(palette=["cce0ff"], opacity=0.5)) \
    .blend(ee.Image().byte().paint(jk, 1).visualize(palette=["ffe0b3"], opacity=0.5)) \
    .blend(ee.Image().byte().paint(stateFC, 1, 2).visualize(palette=["000000"])) \
    .blend(positives.style(color="d00000", pointSize=2)) \
    .blend(mismatches.style(color="ff00ff", pointSize=5))
url = img.getThumbURL({"region": region, "dimensions": 1100, "format": "png"})
urllib.request.urlretrieve(url, f"{out_dir}/step0_states_map.png")
print("Map saved:", f"{out_dir}/step0_states_map.png")
