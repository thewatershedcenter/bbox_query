from app_ept import *
import pandas as pd
import geopandas as gpd
from shapely import geometry as gm

vector = '/test/test_buff.shp'

outpath = '.'
fname = 'GALNAKRAFTORNA'

usgs = pd.DataFrame({'x': [489000, 489000, 489749.99, 489749.99],
                     'y': [4514250, 4514999.99, 4514999.99, 4514250]})


def test_get_ept_srs():
    ept = 'https://storage.googleapis.com/monument_bucket/CarrHirzDelta_1/entwine/ept.json'
    assert get_ept_srs(ept) == 'EPSG:6339'


def test_transform_vector():
    # bounds of test tile the shape falls in 
    usgs = pd.DataFrame({'x': [489000, 489000, 489749.99, 489749.99],
                     'y': [4514250, 4514999.99, 4514999.99, 4514250]})

    # make points 
    points = gpd.points_from_xy(usgs['x'], usgs['y'])

    # make polygon
    poly = gm.Polygon([[p.x, p.y] for p in usgs.geometry])

    # get transformed polygon of interest
    s = transform_vector(vector, srs)

    assert poly.contains(s.geometry.values[0]) == 'pig'
