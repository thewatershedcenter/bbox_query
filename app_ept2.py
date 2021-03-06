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
import pandas as pd
import dask.dataframe as dd
import dask.array as da
from math import ceil
from shapely.geometry import Point, Polygon
from dask.diagnostics import ProgressBar

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

    nx = ceil((maxx - minx) / size)
    ny = ceil((maxy - miny) / size)
    print(f'This will make {nx*ny} boxes! ({nx} x {ny})')

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


def is_box_in(box, geodf):

    # unpack the box
    ([minx, maxx], [miny, maxy]) = box

    # make list of point coords
    p = [[minx, miny], [minx, maxy], [maxx, maxy], [maxx, miny], [minx, miny]]

    # make polygon box
    polybox = Polygon(p)

    # check for intersection
    return(polybox.intersects(geodf.geometry.values[0]))


def cull_empty_bxs(bxs, geodf):
    '''removes sub-boxes not intersecting polygon'''
    lazy = []
    for bx in bxs:
        lazy.append(delayed(is_box_in)(bx, geodf))

    # compute the mask and mask the list
    print('culling boxes')
    mask = compute(*lazy)
    fewer_bxs = [bxs[i] for i in range(len(bxs)) if mask[i]]
    print(f'Number of boxes reduce to {len(fewer_bxs)}')
    return(fewer_bxs)


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
        pipeline.execute()
        return(pipeline)
    else:
        raise Exception('Bad pipeline (sorry to be so ambigous)!')


def get_points_as_df(ept, bbox, srs):
    '''cals makepipe, returns just the array of points'''
    pipe = make_pipe(ept, bbox, srs)
    arr = pipe.arrays[0]
    df = pd.DataFrame(arr)
    return(df)


def get_lazy_dfs(bxs, ept, srs):
    lazy = []
    for bx in bxs:
        # fill lazy with delayed, executed pdal.pipeline objects
        lazy.append(delayed(get_points_as_df)(ept, bx, srs))

    return(lazy)


def rechunk_ddf(df):
    '''rechunks a dask df of unknown chunksize'''   
    cols = df.columns
    arr = df.to_dask_array(lengths=True)
    arr = da.rechunk(arr)
    df = dd.from_dask_array(arr, columns=cols)
    return(df)


def row_in_geodf(row, geodf):
    '''
    Returns delayed dask df of points from daskdf which lie
    within the geometry of geodf.
    '''
    poly = geodf.geometry.values[0]
    return(poly.contains(row.geometry))


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

    # get vector file basename
    fname = os.path.basename(args.vector).split('.')[0]

    # get srs
    srs = get_ept_srs(args.ept)

    # read vector to geodf
    s = read_and_transform_vector(args.vector, srs)

    # find bbox of s
    box = make_bbox(s)

    # define sub box size, TODO: getthis from a function
    size = 100

    # make list of sub-boxes
    bxs = divide_bbox(box, size)

    # get rid of boxes that do not intersect polygon
    bxs = cull_empty_bxs(bxs, s)

    # make list with delayed df from each box
    lazy = get_lazy_dfs(bxs, args.ept, srs)

    # make a dask df, rechunk it so chunks are not unknown
    print('from delayed and rechunk')
    with ProgressBar():
        points = dd.from_delayed(lazy)
    points = rechunk_ddf(points)

    # make an h5
    print('write hdf')
    with ProgressBar():
        points.to_hdf(os.path.join(args.out, f'{fname}_*.hdf5'),
                      '/data',
                      compute=True)

    # delete points, which is a ddf based on delayed graph from ept
    del points

    # TODO: break the stuff above here into a function?

    # replace it with ddf pointing to the h5s on disk
    print('read hdf')
    with ProgressBar():
        points = dd.read_hdf(os.path.join(args.out, f'{fname}_*.hdf5'),
                             '/data')

    # add geometry column of points
    print('apply geometry')
    with ProgressBar():
        points['geometry'] = points.apply(lambda row: Point(row.X,
                                                            row.Y,
                                                            row.Z), axis=1)

    # subset points to only include those in the polygon
    print('clip points')
    with ProgressBar():
        points = points.loc[points.apply(lambda row: row_in_geodf(row, s),
                                         axis=1,
                                         meta=('bool'))]

    print('compute')
    with ProgressBar():
        points.compute()
