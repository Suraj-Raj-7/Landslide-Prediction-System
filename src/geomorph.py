"""Python mirror of GEE module Current/24_step3_geomorph_module.

polygons() -> the four NGDR 1:250k Geomorphology layers (HP, UK, J&K, Ladakh)
with gm_code = 1 + index of 'legend_sho' in GM_CLASSES (0 = unmapped/none).
image() -> gm_code painted as an integer band.
"""
import ee

ASSETS = ["users/rajsuraj777/HP_geomorph", "users/rajsuraj777/UK_geomorph",
          "users/rajsuraj777/JK_geomorph", "users/rajsuraj777/LADAKH_geomorph"]
GM_CLASSES = ["Aeolian Sand Dune", "Aeolian dune complex", "Alluvial Plain", "Anthropogenic terrain", "Avalanche Chute", "Dam and Reservoir", "Deltaic Plain", "Flood Plain", "Glacial Cirque- Arete- Horn", "Glacial Lake and Nunatak", "Glacial Moraine", "Glacial Terrain", "Glacial Valley", "Highly Dissected Hills and Valleys", "Highly Dissected Plateau", "Kame Terrace", "Lacustrine Plain", "Lacustrine Swamp and Marsh", "Lacustrine Terrain", "Lake Island", "Low Dissected Hills and Valleys", "Mass Wasting Products", "Moderately Dissected Hills and Valleys", "Pediment Pediplain Complex", "Piedmont Slope", "Quarry and Mine Dump", "Snow Cover", "Valley Glacier", "Waterbodies-Other", "Waterbody - River"]
BANDS = ["gm_code"]


def polygons():
    keys = ee.List(GM_CLASSES)

    def tag(f):
        k = ee.String(ee.Algorithms.If(f.get("legend_sho"), f.get("legend_sho"), "")).trim()
        return f.set("gm_code", keys.indexOf(k).add(1))   # indexOf -1 (unmapped) -> 0

    return ee.FeatureCollection([ee.FeatureCollection(a) for a in ASSETS]).flatten().map(tag)


def image():
    return ee.Image(0).int().paint(polygons(), "gm_code").rename("gm_code")
