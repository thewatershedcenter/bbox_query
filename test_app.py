#%%
from dataclasses import dataclass
from app_ept import *
import pandas as pd
import geopandas as gpd
from shapely import geometry as gm
import subprocess
import json

# TODO: add a dataclas called fake_args to act like args
# wrap the end of app_ept in a functions so we can test here more directly


@dataclass
class FakeArgs:
    """Class for acting like we are getting args from argparse."""
    vector: str
    ept: str
    out: str


vector1 = 'test/test_buff.shp'
vector2 = 'test/'
ept = 'https://storage.googleapis.com/monument_bucket/CarrHirzDelta_1/entwine/ept.json'
out = '.'

args = FakeArgs(vector1, ept, out)

vpath = os.path.dirname(args.vector)
global vpath

def test_get_ept_srs():
    '''tests that srs can be retrieved'''
    assert get_ept_srs(args.ept) == 'EPSG:6339'


def test_transform_vector():
    '''tests that vector file can be read and transformed to srs'''
    # get srs
    srs = get_ept_srs(args.ept)

    # bounds of test tile the shape falls in 
    usgs = pd.DataFrame({'x': [489000, 489000, 489749.99, 489749.99],
                         'y': [4514250, 4514999.99, 4514999.99, 4514250]})

    # make points 
    points = gpd.points_from_xy(usgs['x'], usgs['y'])

    # make polygon
    poly = gm.Polygon([[p.x, p.y] for p in points])

    # get transformed polygon of interest
    s = read_and_transform_vector(args.vector, srs, 'arbitrary_string')

    assert poly.contains(s.geometry.values[0])


def test_fetch_points_file():
    '''tests when vector points to single file'''
    # get srs
    srs = get_ept_srs(args.ept)

    # get bbox, fname
    hesher = abs(hash(args.ept)) % (10 ** 8)
    bbox, fname = bbox_from_vector(args.vector, srs, hesher)

    # put into the bboxes list
    bboxes = [bbox]
    fnames= [fname]

    # download the pointcloud
    query_from_list(bboxes, srs, out, fnames, args.ept)

    # make sure there are points
    cmd = f'pdal info {fname}.las'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    count = json.loads(result.stdout.decode("utf-8"))['stats']['statistic'][0]['count']
    print(count)
    assert count > 100


# change the vector to just dir
args.vector = vector2

vpath = os.path.dirname(args.vector)
global vpath


def test_fetch_points_dir():
    '''tests when vector points to dir'''
    # get srs
    srs = get_ept_srs(args.ept)

    # empty list for boxes
    bboxes = []
    fnames = []

    # ls the dector_dir
    vectors = [os.path.join(args.vector, f)
                   for f in os.listdir(vector2)
                   if f.endswith('.gpkg')  
                   or f.endswith('.shp') 
                   or f.endswith('.geojson')]

    hesher = abs(hash(args.ept)) % (10 ** 8)

    for vector in vectors:
        bbox, fname = bbox_from_vector(vector, srs, hesher)
        bboxes.append(bbox)
        fnames.append(fname)

    # download the pointcloud
    query_from_list(bboxes, srs, out, fnames, args.ept)

    # make sure there are points
    for fname in fnames:
        cmd = f'pdal info {fname}.las'
        result = subprocess.run(cmd, shell=True, capture_output=True)
        count = json.loads(result.stdout.decode("utf-8"))['stats']['statistic'][0]['count']
        print(count)
        assert count > 100
