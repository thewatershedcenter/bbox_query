#%% 
from app_ept import *
import pandas as pd
import geopandas as gpd
from shapely import geometry as gm
import subprocess
import json

vector = 'test/test_buff.shp'
vector2 = 'test/'
ept = 'https://storage.googleapis.com/monument_bucket/CarrHirzDelta_1/entwine/ept.json'
out = '.'
test_count = 442255


def test_get_ept_srs():
    '''tests that srs can be retrieved'''
    assert get_ept_srs(ept) == 'EPSG:6339'


def test_transform_vector():
    '''tests that vector file can be read and transformed to srs'''
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


def test_fetch_points_file():
    '''tests when vector points to single file'''
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
    assert json.loads(result.stdout.decode("utf-8"))['stats']['statistic'][0]['count'] > 100


def test_fetch_points_dir():
    '''tests when vector points to dir'''
    # get srs
    srs = get_ept_srs(ept)

    # empty list for boxes
    bboxes = []
    fnames = []

    # ls the dector_dir
    vectors = [os.path.join(vector2, f)
                   for f in os.listdir(vector2)
                   if f.endswith('.gpkg')  
                   or f.endswith('.shp') 
                   or f.endswith('.geojson')]

    for vector in vectors:
        bbox, fname = bbox_from_vector(vector, srs)
        bboxes.append(bbox)
        fnames.append(fname)

    # download the pointcloud
    query_from_list(bboxes, srs, out, fnames, ept)

    # make sure there are points
    for fname in fnames:
        cmd = f'pdal info {fname}.las'
        result = subprocess.run(cmd, shell=True, capture_output=True)
        assert json.loads(result.stdout.decode("utf-8"))['stats']['statistic'][0]['count'] > 100

