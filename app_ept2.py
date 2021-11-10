import argparse
import os
import json
import subprocess
import requests
import geopandas as gpd
from shutil import rmtree
from dask import delayed, compute
import pdal
impot numpy as np

import warnings
warnings.filterwarnings('ignore')


def get_ept_srs(ept):
    x = requests.get(ept)
    ept_json = json.loads(x.text)
    srs = ept_json['srs']['horizontal']
    srs = f'EPSG:{srs}'
    return srs


def read_and_transform_vector(vector, srs, fname):
    # read the vector file
    s = gpd.read_file(vector)
    # get the integer from the srs
    srs_number = int(srs.split(':')[-1])

    if srs_number != s.crs.to_epsg():
        # make init epsg string
        init_srs = {'init': srs}
        # transform  s
        s = s.to_crs(init_srs)

    return(s)


if __main__:
    print(print(pdal.__version__))