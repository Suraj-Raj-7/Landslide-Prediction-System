"""Python mirror of GEE module Current/22_step3_faults_module.

image() -> ee.Image with
  dist_fault_m   distance (m) to the nearest NGDR 1:50k fault or thrust line
  dist_thrust_m  distance (m) to the nearest thrust: a line counts as a thrust
                 if its fault_type OR its fault_name contains 'THRUST'
                 (J&K and Ladakh type most named thrusts as 'FAULT INFERRED';
                 type alone would give them ~0% thrusts vs 26-48% with names)
Searched within 80 km so no value is empty.
"""
import ee

ASSETS = ["users/rajsuraj777/HP_fault", "users/rajsuraj777/UK_fault",
          "users/rajsuraj777/JK_fault", "users/rajsuraj777/LADAKH_fault"]
BANDS = ["dist_fault_m", "dist_thrust_m"]
RADIUS_M = 80000


def lines():
    def tag(f):
        t = ee.String(ee.Algorithms.If(f.get("fault_type"), f.get("fault_type"), "")).toUpperCase()
        n = ee.String(ee.Algorithms.If(f.get("fault_name"), f.get("fault_name"), "")).toUpperCase()
        return f.set("is_thrust", t.index("THRUST").gte(0).Or(n.index("THRUST").gte(0)))
    return ee.FeatureCollection([ee.FeatureCollection(a) for a in ASSETS]).flatten().map(tag)


def image():
    fl = lines()
    return ee.Image.cat([
        fl.distance(searchRadius=RADIUS_M, maxError=10).rename("dist_fault_m"),
        fl.filter(ee.Filter.eq("is_thrust", 1)).distance(searchRadius=RADIUS_M, maxError=10).rename("dist_thrust_m"),
    ])
