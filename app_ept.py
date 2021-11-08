#!/usr/bin/env python3

import argparse
import os

# import pdal
import json
import subprocess
import requests
import geopandas as gpd

import warnings
warnings.filterwarnings('ignore')

# TODO:
#     Allow for reprojection
#     un-hardcode threads in make_pipe
#     un-hardcode resolution in make_pipe
#     make docstrings
#     update make_pipe docstring
#


def get_ept_srs(ept_url):
    x = requests.get(ept_url)
    ept_json = json.loads(x.text)
    srs = ept_json['srs']['horizontal']
    srs = f'EPSG:{srs}'
    return srs


def read_and_transform_vector(vector, srs, fname):
    # read the vector file
    s = gpd.read_file(vector)
    # get the intiger from the srs
    srs_number = int(srs.split(':')[-1])

    if srs_number != s.crs.to_epsg():
        # make init epsg string
        init_srs = {'init': srs}
        # transform  s
        s = s.to_crs(init_srs)

    # add a column to use with overlay in pipe
    s['Pohjola'] = 900

    # write with new name
    new_name = f'{os.path.dirname(vector)}/{fname}_{srs_number}.gpkg'
    s.to_file(new_name)

    return(s)


def bbox_from_vector(vector, srs, file_hash):
    # get the basename for namint the las
    fname = os.path.basename(vector).split('.')[0]
    fname = f'{fname}_{file_hash}'

    # load and transform vector file
    s = read_and_transform_vector(vector, srs, fname)

    # make fname of transformed file from above step, needed later
    srs_number = int(srs.split(':')[-1])
    fname = f'{fname}_{srs_number}'

    # get the bbox from the vector
    x, y = s.geometry.envelope.exterior.values[0].coords.xy
    minx, maxx, miny, maxy = min(x), max(x), min(y), max(y)

    # pack up the bbox
    box = ([minx, maxx], [miny, maxy])

    return(box, fname)


def ept_window_query(minx, maxx, miny, maxy, ept, srs, outpath, tag):
    ''' '''

    f = f'{vpath}/{tag}.gpkg'
    of = os.path.join(outpath, tag + '.las')

    # make pipeline
    bbox = ([minx, maxx], [miny, maxy])
    pipeline = make_pipe(ept, bbox, of, srs)
    json_file = os.path.join(outpath, f'{tag}.json')
    with open(json_file, 'w') as j:
        json.dump(pipeline, j)

    # make pdal comand
    cmd = f'pdal pipeline -i {json_file} --developer-debug && rm {json_file}'
    _ = subprocess.run(cmd, shell=True, capture_output=True)
    if len(_.stderr) > 0:
        print(_.stderr)


def make_pipe(ept, bbox, clip_file, out_path, srs, threads=4, resolution=1):
    '''Creates, validates and then returns the pdal pipeline

    Arguments:
    ept        -- String - Path to ept file.
    vector     -- String - Path to vetcor file for which points will
                  be returned.
    bbox       -- Tuple  - Bounding box in srs coordintes,
                  in the form: ([minx, maxx], [miny, maxy]).
    out_path   -- String - Path where the CHM shall be saved. Must
                  include .tif exstension.
    srs        -- String - EPSG identifier for srs  being used. Defaults
                  to EPSG:3857
                  because that is what ept files tend to use.
    threads    -- Int    - Number os threads to be used by the reader.ept.
                  Defaults to 4.
    resolution -- Int or Float - resolution (srs units) used by writers.gdal
    '''

    pipe = {
        'pipeline': [
            {
                'bounds': f'{bbox}',
                'filename': ept,
                'type': 'readers.ept',
                'spatialreference': srs,
                'threads': threads,
            },
            {
                'type': 'filters.overlay',
                'dimension': 'Classification',
                'datasource': clip_file,
                'Column': 'Pohjola'
            },
            {
                'type': 'filters.range',
                'limits': 'Classification!=900'
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
                'type': 'writers.las',
                'filename': out_path,
                'a_srs': srs}
        ]
    }

    return pipe


def query_from_list(bboxes, srs, outpath, tags, ept):
    '''queries all the boxes in the list
       TODO :Dask'''

    for i, bbox in enumerate(bboxes):
        ([minx, maxx], [miny, maxy]) = bbox

        # make a laz for the window from ept.
        ept_window_query(minx, maxx, miny, maxy,
                         ept, srs, outpath, tag=tags[i])


if __name__ == '__main__':
    '''Returns subsets of supplied files clipped to bbox supplied in command
    or multiple bboxs specified in file using --bbxf'''

    # parse args -------------------------------------------------------------
    parser = argparse.ArgumentParser()

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

    args = parser.parse_args()

    # make an 8 digit hash so that it won't overwrite existing point clouds
    # this is for the case where we run on multiple epts and some shapes
    # fall into more than one ept.subprocess
    hesher = abs(hash(args.ept)) % (10 ** 8)

    # find the srs of the ept
    srs = get_ept_srs(args.ept)

    vpath = os.path.dirname(args.vector)
    global vpath

    # make list off bboxes
    if os.path.isfile(args.vector):
        bbox, fname = bbox_from_vector(args.vector, srs, hesher)
        # put into the bboxes list
        bboxes = [bbox]
        fnames = [fname]

    elif os.path.isdir(args.vector):
        # empty list for boxes
        bboxes = []
        fnames = []

        # ls the dector_dir
        vectors = [os.path.join(args.vector, f)
                   for f in os.listdir(args.vector)
                   if f.endswith('.gpkg')  
                   or f.endswith('.shp') 
                   or f.endswith('.geojson')]

        # TODO: if this is slow rewrite to be dask-able
        for vector in vectors:
            bbox, fname = bbox_from_vector(vector, srs, hesher)
            bboxes.append(bbox)
            fnames.append(fname)

    else:
        print(
            '''MysteryError: a mysterious error has occured.  No doubt you find
            this infuriating'''
        )

    query_from_list(bboxes, srs, args.out, fnames, args.ept)
