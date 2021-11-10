import argparse
import os
import json
import subprocess
import requests
import geopandas as gpd
from shutil import rmtree
from dask import delayed, compute
import pdal
import numpy as np

import warnings
warnings.filterwarnings('ignore')


def get_ept_srs(ept):
    x = requests.get(ept)
    ept_json = json.loads(x.text)
    srs = ept_json['srs']['horizontal']
    srs = f'EPSG:{srs}'
    return srs


def read_and_transform_vector(vector, srs):
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


def make_bbox(geodf):
    '''returns bbox of a geodf in pdal format'''
    # get the bbox from the vector
    x, y = geodf.geometry.envelope.exterior.values[0].coords.xy
    minx, maxx, miny, maxy = min(x), max(x), min(y), max(y)

    # pack up the bbox
    box = ([minx, maxx], [miny, maxy])

    return(box)


def optimal_box_division_size():
    '''TODO: firgure out a way to optimize subbox size for
    any pointcloud, using dryruns?'''


def divide_bbox(box, size):
    '''divides box into subboxes of roughly size x size (m)'''

    # unpack the box
    ([minx, maxx], [miny, maxy]) = box

    # calculate x edges of tiles
    x = minx
    xs = []
    while x < maxx:
        xs.append([x, x + size])
        x = x + size
    if x < maxx:
        xs.append([x, maxx])

    # calculate y edges of tiles
    y = miny
    ys = []
    while y < maxy:
        ys.append([y, y + size])
        y = y + size
    if y < maxy:
        ys.append([y, maxy])

    # now use x and y edges to define tile corners
    bxs = []
    for x in xs:
        for y in ys:
            sub_box = (x, y)
            bxs.append(sub_box)

    return(bxs)

def make_pipe(ept, bbox, srs):
    '''Creates, validates and then returns the pdal pipeline'''

    # pipe as dict
    pipe = {
        'pipeline': [
            {
                'bounds': f'{bbox}',
                'filename': ept,
                'type': 'readers.ept',
                'spatialreference': srs
            },
            {
                'type': 'filters.elm'
            },
            {
                'type': 'filters.assign',
                'assignment': 'Classification[:]=0',
                'where': 'Classification > 20'
            },
            {
                'type': 'filters.outlier',
                'method': 'radius',
                'radius': 1.0,
                'min_k': 6
            },
            {
                'type': 'filters.hag_nn',
                'count': 2
            },
            {
                'type': 'filters.range',
                'limits': 'HeightAboveGround[0:88]'
            }
        ]
    }

    # make pipe into pdal pipe thing
    pipeline = pdal.Pipeline(json.dumps(pipe))

    # vlidate and return or raise complaint
    if pipeline.validate():
        return(pipeline)
    else:
        raise Exception('Bad pipeline (sorry to be so ambigous)!')


def parse_arguments():
    '''parses the arguments, returns args'''

    # init parser
    parser = argparse.ArgumentParser()

    # add args
    parser.add_argument(
        '--vector',
        type=str,
        required=False,
        help='Path to vector file for which points will be returned.',
    )

    parser.add_argument('--ept', type=str, required=True, help='path to ept')

    parser.add_argument(
        '--out', type=str, required=True, help='path to output directory'
    )

    # parse the args
    args = parser.parse_args()

    return(args)


if __name__ == '__main__':
    print(print(pdal.__version__))

    # parse the args
    args = parse_arguments()

    # get srs
    srs = get_ept_srs(args.ept)

    # read vector to geodf
    s = read_and_transform_vector(args.vector, srs)

    # find bbox of s
    box = make_bbox(s)

    # define sub box size, TODO: getthis from a function
    size = 3_500

    # make list of sub-boxes
    divide_bbox(box, size)





