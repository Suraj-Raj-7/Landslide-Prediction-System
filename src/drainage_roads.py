"""Python mirror of GEE module Current/12_step2_drainage_roads_module.

image(stream_km2) returns one ee.Image with the Step 2 bands:
  dist_stream_m      distance (m) to the nearest MERIT Hydro stream cell, where a
                     stream is any cell with upstream area >= stream_km2 (km2).
  hand_m             MERIT Hydro height above nearest drainage (m). Experimental.
  dist_road_m        distance (m) to the nearest motorable OSM road (incl. unpaved
                     tracks and roads under construction; excl. paths/footways).
  dist_major_road_m  distance (m) to the nearest national/state-level road
                     (motorway, trunk, primary, secondary and their links).
"""
import ee

ROAD_ASSETS = ["users/rajsuraj777/HP_roads_osm", "users/rajsuraj777/UK_roads_osm",
               "users/rajsuraj777/JK_Ladakh_roads_osm"]
MOTORABLE = ["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link",
             "secondary", "secondary_link", "tertiary", "tertiary_link", "unclassified",
             "residential", "service", "living_street", "track", "road", "busway",
             "construction"]
MAJOR = ["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link",
         "secondary", "secondary_link"]
STREAM_RADIUS_M = 20000   # kernel limit is 512 px; 20 km at ~93 m = 432 px
ROAD_RADIUS_M = 80000   # 30 km left gaps in remote Ladakh/Spiti; 80 km leaves none
BANDS = ["dist_stream_m", "hand_m", "dist_road_m", "dist_major_road_m"]


def roads():
    return ee.FeatureCollection([ee.FeatureCollection(a) for a in ROAD_ASSETS]).flatten()


def image(stream_km2):
    merit = ee.Image("MERIT/Hydro/v1_0_1")
    mproj = merit.select("upa").projection()
    streams = merit.select("upa").gte(stream_km2).selfMask()
    dist_stream = streams.distance(ee.Kernel.euclidean(STREAM_RADIUS_M, "meters"), False) \
        .reproject(mproj).rename("dist_stream_m")   # compute on the ~93 m MERIT grid
    hand = merit.select("hnd").rename("hand_m")
    r = roads()
    dist_road = r.filter(ee.Filter.inList("highway", MOTORABLE)) \
        .distance(searchRadius=ROAD_RADIUS_M, maxError=10).rename("dist_road_m")
    dist_major = r.filter(ee.Filter.inList("highway", MAJOR)) \
        .distance(searchRadius=ROAD_RADIUS_M, maxError=10).rename("dist_major_road_m")
    return ee.Image.cat([dist_stream, hand, dist_road, dist_major])
