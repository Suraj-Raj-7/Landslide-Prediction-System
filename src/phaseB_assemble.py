"""Phase B: build negatives_features_v1.csv and training_table_v1.csv.

Reads the finished GEE assets users/rajsuraj777/negB_type1_* and negB_type2_*.
Type 1 rows get their FIXED features copied from the positive at the same
location (src_id); their rain/soil/snow/NDVI come from GEE for the new date.
Positives: positives_features_v1.csv without Ladakh (label 1).
Prints gaps per column and a positives-vs-negatives comparison of key features.
Usage: python -I phaseB_assemble.py POSITIVES_FEATURES_CSV OUT_DIR
"""
import csv
import sys

import ee

pos_csv, out_dir = sys.argv[1], sys.argv[2]
ee.Initialize(project="idyllic-return-468714-j4")

FEATURES = ['elevation_m', 'slope_deg', 'aspect_deg', 'aspect_sin', 'aspect_cos', 'plan_curv', 'profile_curv',
            'tpi_500m', 'twi', 'dist_stream_m', 'hand_m', 'dist_road_m', 'dist_major_road_m', 'glim_code',
            'rock_code', 'dist_fault_m', 'dist_thrust_m', 'gm_code', 'lc_class', 'lc_class_30m', 'ndvi_pre365',
            'ndvi_pre_n', 'imerg_d0', 'imerg_ant1d', 'imerg_ant3d', 'imerg_ant7d', 'imerg_ant15d', 'imerg_ant30d',
            'imerg_max1d_7d', 'chirps_d0', 'chirps_ant1d', 'chirps_ant3d', 'chirps_ant7d', 'chirps_ant15d',
            'chirps_ant30d', 'sm_l1_dm1', 'sm_l2_dm1', 'swe_dm1_mm', 'snowmelt_ant7d_mm', 'era5_glacier',
            'imerg_images_31d', 'imerg_provisional_31d']
DATED = {'ndvi_pre365', 'ndvi_pre_n', 'imerg_d0', 'imerg_ant1d', 'imerg_ant3d', 'imerg_ant7d', 'imerg_ant15d',
         'imerg_ant30d', 'imerg_max1d_7d', 'chirps_d0', 'chirps_ant1d', 'chirps_ant3d', 'chirps_ant7d',
         'chirps_ant15d', 'chirps_ant30d', 'sm_l1_dm1', 'sm_l2_dm1', 'swe_dm1_mm', 'snowmelt_ant7d_mm',
         'era5_glacier', 'imerg_images_31d', 'imerg_provisional_31d'}
STATIC = [f for f in FEATURES if f not in DATED]
COLS = ["id", "label", "neg_type", "src_id", "state", "admin_unit", "lat", "lon", "event_date"] + FEATURES


def read_assets(prefix):
    ids = [a["id"] for a in ee.data.listAssets({"parent": "projects/earthengine-legacy/assets/users/rajsuraj777"})["assets"]
           if a["id"].split("/")[-1].startswith(prefix)]
    rows = []
    for a in sorted(ids):
        rows += [f["properties"] for f in ee.FeatureCollection(a).getInfo()["features"]]
        print("read", a.split("/")[-1], len(rows))
    return rows


pos = {r["id"]: r for r in csv.DictReader(open(pos_csv, encoding="utf-8"))}
train_pos = [dict(r, label=1, neg_type="positive", src_id="") for r in pos.values() if r["admin_unit"] != "Ladakh"]

t1 = read_assets("negB_type1_")
for r in t1:
    p = pos[r["src_id"]]
    for f in STATIC:
        r[f] = p[f]
    r["label"] = 0
t2 = read_assets("negB_type2_")
for r in t2:
    r["label"] = 0
negs = t1 + t2


def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, COLS, extrasaction="ignore")
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["label"], r["id"])):
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in COLS})


write(f"{out_dir}/negatives_features_v1.csv", negs)
write(f"{out_dir}/training_table_v1.csv", train_pos + negs)
print("negatives:", len(negs), "(type1", len(t1), "type2", len(t2), ") | positives:", len(train_pos),
      "| training rows:", len(train_pos) + len(negs))

gaps = {f: sum(1 for r in negs if r.get(f) in (None, "")) for f in FEATURES}
print("negatives: columns with gaps:", {f: g for f, g in gaps.items() if g})


def med(rows, f):
    v = sorted(float(r[f]) for r in rows if r.get(f) not in (None, ""))
    return round(v[len(v) // 2], 3) if v else None


print(f"{'feature':<16}{'positives':>11}{'type1':>11}{'type2':>11}")
for f in ['slope_deg', 'dist_road_m', 'dist_stream_m', 'elevation_m', 'imerg_d0', 'imerg_ant7d', 'imerg_ant30d',
          'sm_l1_dm1', 'ndvi_pre365']:
    print(f"{f:<16}{med(train_pos, f):>11}{med(t1, f):>11}{med(t2, f):>11}")
