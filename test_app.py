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

vector = 'test/nftiles/north_fork_tiles.shp'

ept = 'https://storage.googleapis.com/monument_bucket/CarrHirzDelta_1/entwine/ept.json'

out = 'poo'

os.makedirs(out, exist_ok=True)

global args
args = Namespace(vector=vector, ept=ept, out=out)


def test_get_ept_srs():
    '''tests that srs can be retrieved'''
    srs = get_ept_srs(args.ept)
    print(srs)

    assert srs == 'EPSG:6339'


# add additional args
args.hesher = abs(hash(args.ept)) % (10 ** 8)
args.srs = get_ept_srs(args.ept)





# %%
