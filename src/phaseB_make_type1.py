"""Phase B, Type 1 negatives: SAME PLACE, SAFE DAY.

For every non-Ladakh positive event, pick a date from a shared pool of ~250
dates whose months follow the positives' month mix, such that no recorded
landslide lies within 5 km and +/-30 days of that date. Dates are limited to
2005-01-01 .. 2025-09-30 (final IMERG). Writes negatives_type1_points.csv.
Usage: python -I phaseB_make_type1.py POSITIVES_FEATURES_CSV OUT_DIR
"""
import csv
import math
import random
import sys
from collections import Counter
from datetime import date, timedelta

SEED = 20261022
POOL_SIZE = 250
BUFFER_KM, GAP_DAYS = 5.0, 30
START, END = date(2005, 1, 1), date(2025, 9, 30)

src, out_dir = sys.argv[1], sys.argv[2]
rows = list(csv.DictReader(open(src, encoding="utf-8")))
allpos = [(float(r["lat"]), float(r["lon"]), date.fromisoformat(r["event_date"])) for r in rows]
train = [r for r in rows if r["admin_unit"] != "Ladakh"]
rng = random.Random(SEED)


def km(a, b, c, d):
    p1, p2 = math.radians(a), math.radians(c)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(d - b) / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


# ---- date pool: months weighted like the positives, years/days uniform ----
mw = Counter(int(r["event_date"][5:7]) for r in train)
months, weights = zip(*sorted(mw.items()))
pool = set()
while len(pool) < POOL_SIZE:
    m = rng.choices(months, weights)[0]
    y = rng.randint(START.year, END.year)
    d0 = date(y, m, 1)
    last = (date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)).day
    d = d0.replace(day=rng.randint(1, last))
    if START <= d <= END:
        pool.add(d)
pool = sorted(pool)

# ---- assign one safe date per positive event ----
out, failed = [], []
for r in train:
    la, lo = float(r["lat"]), float(r["lon"])
    near = [p for p in allpos if km(la, lo, p[0], p[1]) <= BUFFER_KM]
    cand = pool[:]
    rng.shuffle(cand)
    pick = next((d for d in cand if all(abs((d - p[2]).days) > GAP_DAYS for p in near)), None)
    if pick is None:
        failed.append(r["id"])
        continue
    out.append({"id": "N1_" + r["id"], "src_id": r["id"], "neg_type": "same_place_safe_day",
                "state": r["state"], "admin_unit": r["admin_unit"], "lat": r["lat"], "lon": r["lon"],
                "event_date": pick.isoformat()})

with open(f"{out_dir}/negatives_type1_points.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, list(out[0].keys()))
    w.writeheader()
    w.writerows(out)
print("type1 points:", len(out), "| failed:", failed, "| pool dates:", len(pool),
      "| distinct dates used:", len({o["event_date"] for o in out}))
print("months used:", sorted(Counter(int(o["event_date"][5:7]) for o in out).items()))
print("states:", Counter(o["state"] for o in out))
