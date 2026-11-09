"""Python mirror of GEE module Current/16_step3_lithology_module.

Reads the reviewed mapping table (lithology_mapping_v1.csv) and builds:
  polygons()  all four NGDR 1:50k lithology layers (HP, UK, J&K, Ladakh) with
              glim_code and rock_code added from the mapping table
  image()     glim_code and rock_code painted as integer bands (for rasters)
Codes: glim_code = index in GLIM_ORDER; rock_code = index in rock_names (0 = none).
"""
import csv

import ee

ASSETS = ["users/rajsuraj777/HP_lithology", "users/rajsuraj777/UK_lithology",
          "users/rajsuraj777/JK_lithology", "users/rajsuraj777/LADAKH_lithology"]
GLIM_ORDER = ["nd", "su", "ss", "sm", "sc", "ev", "mt", "pa", "pi", "pb", "va", "vi", "vb", "py", "wb", "ig"]
BANDS = ["glim_code", "rock_code"]


def load_mapping(csv_path):
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    rock_names = [""] + sorted({r["rock_main"] for r in rows if r["rock_main"]})
    glim = {r["lithologic"]: GLIM_ORDER.index(r["glim_class"]) for r in rows}
    rock = {r["lithologic"]: rock_names.index(r["rock_main"]) for r in rows}
    return glim, rock, rock_names


def polygons(csv_path):
    glim, rock, _ = load_mapping(csv_path)
    g, r = ee.Dictionary(glim), ee.Dictionary(rock)

    def tag(f):
        key = ee.String(ee.Algorithms.If(f.get("lithologic"), f.get("lithologic"), "")).trim().toUpperCase()
        return f.set({"glim_code": g.get(key, 0), "rock_code": r.get(key, 0)})

    return ee.FeatureCollection([ee.FeatureCollection(a) for a in ASSETS]).flatten().map(tag)


def image(csv_path):
    p = polygons(csv_path)
    return ee.Image.cat([ee.Image(0).int().paint(p, "glim_code").rename("glim_code"),
                         ee.Image(0).int().paint(p, "rock_code").rename("rock_code")])
