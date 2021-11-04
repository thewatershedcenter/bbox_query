from app_ept import *
import pandas as pd
import geopandas as gpd
from shapely import geometry as gm
import subprocess
import json

vector = 'test/test_buff.shp'
ept = 'https://storage.googleapis.com/monument_bucket/CarrHirzDelta_1/entwine/ept.json'
out = '.'
test_count = 442255

def test_get_ept_srs():
    assert get_ept_srs(ept) == 'EPSG:6339'


def test_transform_vector():
    # get srs
    srs = get_ept_srs(ept)

    # bounds of test tile the shape falls in 
    usgs = pd.DataFrame({'x': [489000, 489000, 489749.99, 489749.99],
                         'y': [4514250, 4514999.99, 4514999.99, 4514250]})

    # make points 
    points = gpd.points_from_xy(usgs['x'], usgs['y'])

    # make polygon
    poly = gm.Polygon([[p.x, p.y] for p in points])

    # get transformed polygon of interest
    s = read_and_transform_vector(vector, srs)

    assert poly.contains(s.geometry.values[0])


def test_fetch_points():
    # get srs
    srs = get_ept_srs(ept)

    # get bbox, fname
    bbox, fname = bbox_from_vector(vector, srs)

    # put into the bboxes list
    bboxes = [bbox]

    # download the pointcloud
    query_from_list(bboxes, srs, out, fname, ept)

    # make sure there are points
    cmd = f'pdal info {fname}.las'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    assert json.loads(result.stdout.decode("utf-8"))['stats']['statistic'][0]['count'] == test_count

test_fetch_points()
