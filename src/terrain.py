"""Python mirror of GEE module Current/09_step1_terrain_module.

terrain_image() returns one ee.Image with the Step 1 terrain bands on a fixed
metric grid (UTM 43N, 30 m), so values do not depend on export scale.
"""
import math

import ee

CRS = "EPSG:32643"   # UTM 43N. Covers 72-78E; UK reaches 81E (scale error < 0.3%).
L = 30               # cell size (m) of the metric grid
BANDS = ["elevation_m", "slope_deg", "aspect_deg", "aspect_sin", "aspect_cos",
         "plan_curv", "profile_curv", "tpi_500m", "twi"]


def fixed(w):
    return ee.Kernel.fixed(3, 3, w, 1, 1, False)


def derivatives(dem):
    """Zevenbergen & Thorne (1987) coefficients on a 3x3 window.

    Z&T window (north up):  Z1 Z2 Z3 / Z4 Z5 Z6 / Z7 Z8 Z9
      G = (Z6 - Z4) / 2L          dz/dx, east positive
      H = (Z2 - Z8) / 2L          dz/dy, north positive
      F = (-Z1 + Z3 + Z7 - Z9) / 4L^2
    GEE's ee.Kernel.fixed puts weight row 0 on the SOUTH neighbour (verified
    on test planes: a north-rising plane gave H = -1 with row 0 = north). So
    the kernels below list rows south -> north.
    """
    L2 = L * L
    D = dem.convolve(fixed([[0, 0, 0], [1 / (2 * L2), -1 / L2, 1 / (2 * L2)], [0, 0, 0]]))
    E = dem.convolve(fixed([[0, 1 / (2 * L2), 0], [0, -1 / L2, 0], [0, 1 / (2 * L2), 0]]))
    # rows: [Z7 Z8 Z9] (south), [Z4 Z5 Z6], [Z1 Z2 Z3] (north)
    F = dem.convolve(fixed([[1 / (4 * L2), 0, -1 / (4 * L2)], [0, 0, 0], [-1 / (4 * L2), 0, 1 / (4 * L2)]]))
    G = dem.convolve(fixed([[0, 0, 0], [-1 / (2 * L), 0, 1 / (2 * L)], [0, 0, 0]]))
    H = dem.convolve(fixed([[0, -1 / (2 * L), 0], [0, 0, 0], [0, 1 / (2 * L), 0]]))
    return D, E, F, G, H


def curvatures(dem):
    """Plan and profile curvature (1/m), Zevenbergen & Thorne (1987) eq.

    profile = -2 (D G^2 + E H^2 + F G H) / (G^2 + H^2)
    plan    =  2 (D H^2 + E G^2 - F G H) / (G^2 + H^2)
    Signs are checked on test surfaces in the Step 1 run (bowl and dome).
    """
    D, E, F, G, H = derivatives(dem)
    p2 = G.pow(2).add(H.pow(2)).max(1e-10)   # avoid 0/0 on perfectly flat cells
    profile = D.multiply(G.pow(2)).add(E.multiply(H.pow(2))).add(F.multiply(G).multiply(H)) \
        .multiply(-2).divide(p2).rename("profile_curv")
    plan = D.multiply(H.pow(2)).add(E.multiply(G.pow(2))).subtract(F.multiply(G).multiply(H)) \
        .multiply(2).divide(p2).rename("plan_curv")
    return plan, profile


def terrain_image():
    glo = ee.ImageCollection("COPERNICUS/DEM/GLO30_2024_1").select("DEM")
    native = glo.first().projection()
    # Mosaic (no clip), keep native resolution, then resample once onto the
    # metric grid. bilinear avoids blocky steps from the degree grid.
    dem = glo.mosaic().setDefaultProjection(native).resample("bilinear") \
        .reproject(crs=CRS, scale=L).rename("elevation_m")

    slope = ee.Terrain.slope(dem).rename("slope_deg")
    aspect = ee.Terrain.aspect(dem).rename("aspect_deg")
    rad = aspect.multiply(math.pi / 180)
    flat = slope.lt(1)   # aspect is meaningless on near-flat cells
    asp_sin = rad.sin().where(flat, 0).rename("aspect_sin")
    asp_cos = rad.cos().where(flat, 0).rename("aspect_cos")

    plan, profile = curvatures(dem)

    tpi = dem.subtract(dem.reduceNeighborhood(ee.Reducer.mean(),
                                              ee.Kernel.circle(500, "meters", False))) \
        .rename("tpi_500m")

    # TWI = ln(a / tan b) on the MERIT Hydro grid (~93 m), self-consistent:
    # a = upstream area / cell width (specific catchment area, m), b = slope
    # of MERIT elevation. MERIT 'upa' (km2) includes the cell itself, so a > 0.
    merit = ee.Image("MERIT/Hydro/v1_0_1")
    mproj = merit.select("upa").projection()
    width = mproj.nominalScale()
    sca = merit.select("upa").multiply(1e6).divide(width)
    mslope = ee.Terrain.slope(merit.select("elv").setDefaultProjection(mproj))
    tanb = mslope.multiply(math.pi / 180).tan().max(0.001)   # ~0.06 deg floor
    twi = sca.divide(tanb).log().setDefaultProjection(mproj).rename("twi")

    return ee.Image.cat([dem, slope, aspect, asp_sin, asp_cos, plan, profile, tpi, twi])
