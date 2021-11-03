import argparse
import os

# import pdal
import json
import subprocess
import requests
import geopandas as gpd
from shapely.geometry import Polygon
from osgeo import osr

# TODO:
#     Allow for passage of shp, gpgk, geojson, or tiff instead of bbox
#     find epsg from ept so it needn't be passed
#     Allow for reprojection
#     un-hardcode threads in make_pipe
#     un-hardcode resolution in make_pipe
#     make docstrings
#     update make_pipe docstring


def dog():
    print('snake')


def get_ept_srs(ept_url):
    x = requests.get(ept_url)
    ept_json = json.loads(x.text)
    srs = ept_json["srs"]["horizontal"]
    srs = f"EPSG:{srs}"
    return srs


def get_transform(vector, to_srs):
    '''
    vector - str - path to vector file
    to_srs - int - numeric part of epsg code
    '''

    # find srs of vector
    s = gpd.read_file(vector)
    v_srs = s.crs.to_epsg()

    # define transform from v_srs to to_srs
    old = osr.SpatialReference()
    old.ImportFromEPSG(v_srs)
    new = osr.SpatialReference()
    new.ImportFromEPSG(to_srs)
    transform = osr.CoordinateTransformation(old, new)

    return(transform)


def bbox_from_vector(f, layer=None):
    """Returns minx, maxx, miny, maxy of vector file or layer"""
    v = gpd.read_file(f, layer=layer)
    x, y = v.geometry.envelope.exterior.values[0].coords.xy
    return (min(x), max(x), min(y), max(y))


def read_and_transform_vector(vector, srs):
    # make init epsg string
    init_srs = {'init': srs}

    # read the vector file
    s = gpd.read_file(vector)

    # transform  s
    s = s.to_crs(init_srs)

    return(s)


def srs_bbox_from_vector(vector, layer, srs):
    # get just the number from the epsg string
    to_srs = int(srs.split(':')[-1])

    # get transform to transform vector coords to srs
    transform = get_transform(vector, to_srs)

    # get bbox values in vector's native coordinates
    minx, maxx, miny, maxy = bbox_from_vector(vector, layer=layer)

    # transform from vector coords to srs
    minx, miny, minz = transform.TransformPoint(miny, minx)
    maxx, maxy, maxz = transform.TransformPoint(maxy, maxx)

    return(minx, maxx, miny, maxy)


def ept_window_query(minx, maxx, miny, maxy, ept, srs, outpath, tag=None):
    """ """

    # make a tag for the output file
    loc = f"{int(minx)}_{int(maxx)}_{int(miny)}_{int(maxy)}"
    if tag:
        f = tag
    else:
        f = f"{loc}"
    of = os.path.join(outpath, f + ".las")

    # make pipeline
    bbox = ([minx, maxx], [miny, maxy])
    pipeline = make_pipe(ept, bbox, of, srs)
    json_file = os.path.join(outpath, f"{f}.json")
    with open(json_file, "w") as j:
        json.dump(pipeline, j)

    # make pdal comand
    cmd = f"pdal pipeline -i {json_file} --developer-debug"
    _ = subprocess.run(cmd, shell=True, capture_output=True)
    print(f"stdout:\n{_.stdout}\n\n\nerrors:\n{_.stderr}")


def make_pipe(ept, bbox, out_path, srs, threads=4, resolution=1):
    """Creates, validates and then returns the pdal pipeline

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
    """

    pipe = {
        "pipeline": [
            {
                "bounds": f"{bbox}",
                "filename": ept,
                "type": "readers.ept",
                "spatialreference": srs,
                "threads": threads,
            },
            {
                "type": "writers.las",
                "filename": out_path,
                "a_srs": srs}
        ]
    }
    return pipe

    # pipeline = pdal.Pipeline(pipe)
    # if pipeline.validate():
    # return(pipeline)
    # else:
    #    raise Exception('Bad pipeline (sorry to be so ambigous)!')


if __name__ == "__main__":
    """Returns subsets of supplied files clipped to bbox supplied in command
    or multiple bboxs specified in file using --bbxf"""

    # parse args -------------------------------------------------------------
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--bbox",
        type=str,
        required=False,
        help="""The extents of the resource to select in 2 dimensions,
        expressed as a string,
    in the format: '([minx, maxx], [miny, maxy])' """,
    )

    parser.add_argument(
        "--bbxf",
        type=str,
        required=False,
        help="""path to file with a bbox on each line""",
    )

    parser.add_argument(
        "--vector",
        type=str,
        required=False,
        help="""Path to vector file for which points will be returned.""",
    )

    parser.add_argument(
        "--vector_list",
        type=str,
        required=False,
        help="""Path to list of vector files for which points will be returned
        as seperate laz files""",
    )

    parser.add_argument("--ept", type=str, required=True, help="path to ept")

    parser.add_argument(
        "--out", type=str, required=True, help="path to output directory"
    )

    args = parser.parse_args()

    # find the srs of the ept
    srs = get_ept_srs(args.ept)

    # Complain if things are not as they should be
    if ((args.vector is not None) +
       (args.vector_list is not None) != 1):
        raise Exception(
            """One must specify exactly one of vector or vector_list.
            It appears you have done otherwise!"""
        )

    elif args.layer and not args.vector:
        print(
            f"""A layer has been specified, but a vector file has not.
            That is nonsense.
            Ignoring layer {args.layer}"""
        )

    # make list off bboxes 
    if args.vector:
        fname = os.path.basename(args.vector).split('.')[0]
        if args.layer:
            layer = args.layer
        else:
            layer = None

        # load and transform vector file
        s = read_and_transform_vector(args.vector, srs)

        # get the bbox from the vector
        x, y = s.geometry.envelope.exterior.values[0].coords.xy
        minx, maxx, miny, maxy = min(x), max(x), min(y), max(y)

        # pack up the bbox into the bboxes list
        bboxes = [([minx, maxx], [miny, maxy])]

    elif args.vector_list:
        bboxes = []
        fname = None
        with open(args.vector_list) as vectors:
            for line in vectors:
                minx, maxx, miny, maxy = bbox_from_vector(line)
                bboxes.append(([minx, maxx], [miny, maxy]))

    else:
        print(
            """MysteryError: a mysterious error has occured.  No doubt you find
            this infuriating"""
        )

    for bbox in bboxes:
        if args.bbox or args.bbxs:
            # unpack the bbox string
            minx, maxx, miny, maxy = (
                bbox.strip("()").replace("[", "").replace("]", "").split(",")
            )
            minx = float(minx)
            maxx = float(maxx)
            miny = float(miny)
            maxy = float(maxy)
        else:
            ([minx, maxx], [miny, maxy]) = bbox

        # make a laz for the window from ept.
        ept_window_query(minx, maxx, miny, maxy,
                         args.ept, srs, args.out, tag=fname)

# %%
