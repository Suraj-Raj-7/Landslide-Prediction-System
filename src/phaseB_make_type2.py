"""Phase B, Type 2 negatives: SIMILAR PLACE, STORM DAY.

For each storm date (positive event date, Ladakh excluded) take 2 negatives per
positive event, at most 10 per date. Each negative gets the state of a positive
on that date and a random location in that state with slope >= 10.9 deg,
distance to a motorable road <= 284 m, and >= 2 km from any recorded landslide
(any date). Thresholds = 10th/90th percentiles of the positives (data test).

Method: uniform random points in each state's bounding box (Python), checked in
GEE at their 30 m cell (UTM 43N) for: inside the state, slope, road distance,
2 km slide buffer. Batches of 2,000 until each state has enough candidates.
(A full 30 m stratifiedSample over whole states timed out.)
Usage: python -I phaseB_make_type2.py POSITIVES_FEATURES_CSV SRC_DIR OUT_DIR
"""
import csv
import random
import sys
from collections import Counter, defaultdict

import ee

SEED = 20261022
PER_EVENT, CAP = 2, 10
SLOPE_MIN, ROAD_MAX, BUFFER_M = 10.9, 284, 2000
BATCH = 2000
STATE_IDS = {"HP": "1811400B21086746745937", "UK": "1811400B3558497485804", "JK": "1811400B42025667129192"}

src, src_dir, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, src_dir)
import drainage_roads as DR  # noqa: E402
import terrain as TE         # noqa: E402

ee.Initialize(project="idyllic-return-468714-j4")
rng = random.Random(SEED)
rows = list(csv.DictReader(open(src, encoding="utf-8")))
train = [r for r in rows if r["admin_unit"] != "Ladakh"]

# ---- quotas: per date, states drawn from that date's positives ----
by_date = defaultdict(list)
for r in train:
    by_date[r["event_date"]].append(r["state"])
slots = []
for d, states in sorted(by_date.items()):
    q = min(PER_EVENT * len(states), CAP)
    for s in rng.choices(states, k=q):
        slots.append((d, s))
need = Counter(s for _, s in slots)
print("slots:", len(slots), dict(need), flush=True)

# ---- checking image ----
gb = ee.FeatureCollection("WM/geoLab/geoBoundaries/600/ADM1")
allpos = ee.FeatureCollection([ee.Feature(ee.Geometry.Point([float(r["lon"]), float(r["lat"])])) for r in rows])
near = ee.Image(0).byte().paint(allpos.map(lambda f: f.buffer(BUFFER_M, 50)), 1).rename("near")
slope = TE.terrain_image().select("slope_deg")
road = DR.roads().filter(ee.Filter.inList("highway", DR.MOTORABLE)) \
    .distance(searchRadius=ROAD_MAX + 30, maxError=10).unmask(9999).rename("road")

cands = {}
for s, n in need.items():
    g = gb.filter(ee.Filter.eq("shapeID", STATE_IDS[s])).first().geometry()
    b = g.bounds(1000).coordinates().getInfo()[0]
    xs, ys = [p[0] for p in b], [p[1] for p in b]
    inst = ee.Image(0).byte().paint(ee.FeatureCollection([ee.Feature(g)]), 1).rename("inst")
    img = ee.Image.cat([slope, road, near, inst])
    got, tries = [], 0
    while len(got) < n and tries < 20:
        tries += 1
        pts = [(rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys))) for _ in range(BATCH)]
        fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point(list(p)), {"i": i}) for i, p in enumerate(pts)])
        res = img.reduceRegions(fc, ee.Reducer.first(), 30, "EPSG:32643", tileScale=4).getInfo()["features"]
        for f in res:
            p = f["properties"]
            if (p.get("inst") == 1 and p.get("slope_deg", 0) >= SLOPE_MIN
                    and p.get("road", 9999) <= ROAD_MAX and p.get("near") == 0):
                got.append(pts[p["i"]])
        print(s, "batch", tries, "candidates", len(got), "/", n, flush=True)
    rng.shuffle(got)
    cands[s] = got

out, used = [], Counter()
for i, (d, s) in enumerate(slots):
    if used[s] >= len(cands[s]):
        print("ran out of candidates for", s)
        continue
    lon, lat = cands[s][used[s]]
    used[s] += 1
    out.append({"id": f"N2_{i:04d}", "src_id": "", "neg_type": "similar_place_storm_day", "state": s,
                "admin_unit": "JK_UT" if s == "JK" else s, "lat": round(lat, 6), "lon": round(lon, 6),
                "event_date": d})

with open(f"{out_dir}/negatives_type2_points.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, list(out[0].keys()))
    w.writeheader()
    w.writerows(out)
print("type2 points:", len(out), "| dates:", len({o["event_date"] for o in out}),
      "| states:", Counter(o["state"] for o in out), flush=True)
