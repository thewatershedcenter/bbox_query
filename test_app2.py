#  %%
from argparse import Namespace
from app_ept2 import *
import pandas as pd
import geopandas as gpd
from shapely import geometry as gm
import subprocess
import json
import os
import numpy as np
import pandas as pd
import dask.dataframe as dd
import dask.array as da
from time import time
from dask.diagnostics import ProgressBar
from shapely.geometry import Point, Polygon

vector1 = 'test/test_buff.shp'
vector2 = 'test/fid_5.gpkg'

ept = 'https://storage.googleapis.com/monument_bucket/CarrHirzDelta_1/entwine/ept.json'

out = 'poo'

os.makedirs(out, exist_ok=True)

global args
args = Namespace(vector=vector1, vector2=vector2, ept=ept, out=out)


def test_get_ept_srs():
    '''tests that srs can be retrieved'''
    srs = get_ept_srs(args.ept)
    print(srs)

    assert srs == 'EPSG:6339'


# add additional args
args.hesher = abs(hash(args.ept)) % (10 ** 8)
args.srs = get_ept_srs(args.ept)


def test_read_and_transform_vector():
    '''tests that vector file can be read and transformed to srs'''

    srs = get_ept_srs(args.ept)

    # bounds of test tile the shape falls in 
    usgs = pd.DataFrame({'x': [489000, 489000, 489749.99, 489749.99],
                         'y': [4514250, 4514999.99, 4514999.99, 4514250]})

    # make points 
    points = gpd.points_from_xy(usgs['x'], usgs['y'])

    # make polygon
    poly = gm.Polygon([[p.x, p.y] for p in points])

    # get transformed polygon of interest
    s = read_and_transform_vector(args.vector, srs)

    print(poly.contains(s.geometry.values[0]))

    assert poly.contains(s.geometry.values[0])


def test_make_box_ALSO_divide_bbox_ALSO_make_pipe():
    '''tests both make_box and divide_bbox'''

    srs = get_ept_srs(args.ept)
    s = read_and_transform_vector(args.vector2, srs)
    # get vector file basename
    fname = os.path.basename(args.vector2).split('.')[0]
    # find bbox of s
    print('making bbox')
    t0 = time()
    box = make_bbox(s)

    t1 = time()
    print(f'making the bbox took {round((t1-t0), 2)}s')

    size = 100

    global bxs

    t0 = time()
    bxs = divide_bbox(box, size)

    t1 = time()
    print(f'divide_bbox took {round((t1-t0), 2)}s')

    print(f'bbox divided into {len(bxs)} sub-boxes')
    assert len(bxs) > 1
    print('Succesfully tested divide_bbox!')

    # get rid of boxes that do not intersect polygon
    bxs = cull_empty_bxs(bxs, s)

    print('Building delayed task graph')
    lazy = get_lazy_dfs(bxs, args.ept, srs)

    points = dd.from_delayed(lazy)
    points = rechunk_ddf(points)
    points.to_hdf(os.path.join(args.out, f'{fname}_*.hdf5'), '/data', compute=True)


# %%
