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
import dask.dataframe as ddf
import dask.array as da
from time import time

vector1 = 'test/test_buff.shp'

vector2 = 'test/'

ept = 'https://storage.googleapis.com/monument_bucket/CarrHirzDelta_1/entwine/ept.json'

out = 'poo'

os.makedirs(out, exist_ok=True)

global args
args = Namespace(vector=vector1, ept=ept, out=out)


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
    
    # get srs
    srs = get_ept_srs(args.ept)

    # get transformed polygon of interest
    s = read_and_transform_vector(args.vector, srs)

    # find bbox of s
    box = make_bbox(s)

    assert box == ([489013.26329637936, 489116.2366349314],
                   [4514616.760521351, 4514838.612628906])
    print('Succesfully tested make_bbox!')

    size = 10

    bxs = divide_bbox(box, size)

    print(len(bxs))
    assert len(bxs) == 253
    print('Succesfully tested divide_bbox!')

    pipe = make_pipe(args.ept, bxs[2], srs)
    assert isinstance(pipe.arrays[0], np.ndarray)
    assert len(pipe.arrays[0]) > 0
    print(f'Pipeline executed returning a {type(pipe.arrays[0])} of {len(pipe.arrays[0])} points.')

    points = get_points_as_df(args.ept, bxs[2], srs)
    assert isinstance(points, pd.DataFrame)
    print(f'get_points_as_df succesfully returned a df of length {len(points)}')

    lazy = get_lazy_dfs(bxs, args.ept, srs)

    t0 = time()
    points = ddf.from_delayed(lazy)

    t1 = time()
    print(f'from_delayed took {(t1-t0)/60}min')

    t0 = time()
    points = rechunk_ddf(points)

    t1 = time()
    print(f'rechunk took {(t1-t0)/60}min')

    t0 = time()
    points.to_hdf('/media/data/Downloads/test_output.hdf', '/data-*', compute=True)

    t1 = time()
    print(f'to_hdf took {(t1-t0)/60}min')

# %%
test_make_box_ALSO_divide_bbox_ALSO_make_pipe()
# %%
test_get_ept_srs()

# %%
test_read_and_transform_vector()


# %%
