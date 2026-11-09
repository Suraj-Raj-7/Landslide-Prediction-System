"""Python mirror of GEE module Current/14_step4_landcover_module.

image() returns the Step 4 bands from ESA WorldCover v200 (2021, 10 m):
  lc_class        WorldCover class code at the point (10 m pixel).
  lc_class_30m    majority class in the 3x3 window (30 m), matching the
                  30 m grid of the terrain features and less sensitive to a
                  point landing on a single road or river pixel.
Codes: 10 tree, 20 shrub, 30 grass, 40 crop, 50 built-up, 60 bare/sparse,
70 snow/ice, 80 water, 90 herbaceous wetland, 95 mangrove, 100 moss/lichen.
Single 2021 snapshot: land cover at event time is NOT known.
"""
import ee

BANDS = ["lc_class", "lc_class_30m"]
CLASSES = {10: "tree", 20: "shrub", 30: "grass", 40: "crop", 50: "built", 60: "bare",
           70: "snow_ice", 80: "water", 90: "wetland", 95: "mangrove", 100: "moss_lichen"}


def image():
    wc = ee.ImageCollection("ESA/WorldCover/v200").first().select("Map")
    proj = wc.projection()
    mode = wc.reduceNeighborhood(ee.Reducer.mode(), ee.Kernel.square(1, "pixels")) \
        .reproject(proj).rename("lc_class_30m")
    return ee.Image.cat([wc.rename("lc_class"), mode]).toInt()
