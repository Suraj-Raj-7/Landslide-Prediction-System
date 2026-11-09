"""Phase B: start the GEE feature-extraction jobs for the negatives.

  type1: rain/soil/snow (dynamic) + NDVI only; the fixed features are copied
         later from the positives table (same location).
  type2: all 42 features via stack.extract_features.
Each type is split into chunks by date and exported to GEE assets (with point
geometry), named users/rajsuraj777/negB_<type>_<chunk>. The jobs run on Google's
servers; the laptop can be off once they are submitted.
Usage: python -I phaseB_extract.py type1|type2 POINTS_CSV SRC_DIR LITH_CSV N_CHUNKS
"""
import csv
import sys

import ee

kind, pts_csv, src_dir, lith_csv, n_chunks = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
sys.path.insert(0, src_dir)
ee.Initialize(project="idyllic-return-468714-j4")   # before imports: modules build EE objects
import dynamic as DY      # noqa: E402
import stack as ST        # noqa: E402
import vegetation as VG   # noqa: E402

rows = list(csv.DictReader(open(pts_csv, encoding="utf-8")))
dates = sorted({r["event_date"] for r in rows})
META = ["id", "src_id", "neg_type", "state", "admin_unit", "lat", "lon", "event_date"]

for c in range(n_chunks):
    ds = set(dates[c::n_chunks])                        # interleaved: similar load per chunk
    part = [r for r in rows if r["event_date"] in ds]
    fc = ee.FeatureCollection([
        ee.Feature(ee.Geometry.Point([float(r["lon"]), float(r["lat"])]),
                   {k: r[k] for k in META}) for r in part])
    if kind == "type1":
        out = DY.extract(VG.extract(fc, "event_date", 30), "event_date", 1000)
        bands = VG.BANDS + DY.BANDS + ["imerg_images_31d", "imerg_provisional_31d"]
    else:
        out = ST.extract_features(fc, lith_csv, "event_date")
        bands = ST.all_bands()
    asset = f"users/rajsuraj777/negB_{kind}_{chr(97 + c)}"
    task = ee.batch.Export.table.toAsset(collection=out.select(META + bands), description=f"negB_{kind}_{chr(97 + c)}",
                                         assetId=asset)
    task.start()
    print(kind, "chunk", chr(97 + c), "points", len(part), "dates", len(ds), "->", asset, "task", task.id, flush=True)
