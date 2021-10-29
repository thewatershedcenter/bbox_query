import argparse
import os

# import pdal
from string import Template
import json
import subprocess
import requests
from pprint import pprint
import geopandas as gpd
from shapely.geometry import Polygon

# TODO:
#     Allow for passage of shp, gpgk, geojson, or tiff instead of bbox
#     find epsg from ept so it needn't be passed
#     Allow for reprojection
#     un-hardcode threads in make_pipe
#     un-hardcode resolution in make_pipe
#     make docstrings


def get_ept_srs(ept_url):
    x = requests.get(ept_url)
    ept_json = json.loads(x.text)
    srs = ept_json["srs"]["horizontal"]
    srs = f"EPSG:{srs}"
    return srs


def bbox_from_vector(f, layer=None):
    """Returns minx, maxx, miny, maxy of vector file or layer"""
    v = gpd.read_file(f, layer=layer)
    x, y = v.geometry.envelope.exterior.values[0].coords.xy
    return (min(x), max(x), min(y), max(y))


def ept_window_query(minx, maxx, miny, maxy, ept, srs, outpath, tag=None):
    """ """

    # make a tag for the output file
    loc = f"{int(minx)}_{int(maxx)}_{int(miny)}_{int(maxy)}"
    if tag:
        f = f"{loc}_{tag}"
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
    vector     -- String - Path to vetcor file for which points will be returned.
    bbox       -- Tuple  - Bounding box in srs coordintes,
                  in the form: ([minx, maxx], [miny, maxy]).
    out_path   -- String - Path where the CHM shall be saved. Must include .tif exstension.
    srs        -- String - EPSG identifier for srs  being used. Defaults to EPSG:3857
                  because that is what ept files tend to use.
    threads    -- Int    - Number os threads to be used by the reader.ept. Defaults to 4.
    resolution -- Int or Float - resolution (srs units) used by writers.gdal
    """

    pipe = {
        "pipeline": [
            {
                "bounds": f"{bbox}",
                "filename": ept,
                "type": "readers.ept",
                "tag": "readdata",
                "spatialreference": srs,
                "threads": threads,
            },
            {"type": "filters.outlier", "method": "radius", "radius": 1.0, "min_k": 4},
            {"type": "filters.range", "limits": "returnnumber[1:1]"},
            {"type": "writers.las", "filename": out_path, "a_srs": srs},
        ]
    }
    return pipe

    # pipeline = pdal.Pipeline(pipe)
    # if pipeline.validate():
    # return(pipeline)
    # else:
    #    raise Exception('Bad pipeline (sorry to be so ambigous)!')


if __name__ == "__main__":
    """Returns subsets of supplied files clipped to bbox supplied in command or multiple bboxs specified in file using --bbxf"""

    # parse args -------------------------------------------------------------
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--bbox",
        type=str,
        required=False,
        help="""The extents of the resource to select in 2 dimensions, expressed as a string,
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
        help="""Path to list of vector files for which points will be returned as seperate laz files""",
    )

    parser.add_argument("--ept", type=str, required=True, help="path to ept")

    parser.add_argument(
        "--out", type=str, required=True, help="path to output directory"
    )

    args = parser.parse_args()

    # make list off bboxes ---------------------------------------------------
    if (args.bbox != None) + (args.bbxf != None) + (args.vector != None) + (
        args.vector_list != None
    ) != 1:
        print(
            "One must specify exactly one of bbox, bbxf, vector or vector_list. It appears you have done otherwise!"
        )
        # Use raise, not print
    elif args.layer and not args.vector:
        print(
            f"""A layer has been specified, but a vector file has not.
            That is nonsense.
            Ignoring layer {args.layer}"""
        )
    elif args.bbox:
        bboxes = [args.bbox]
    elif args.bbxf:
        bboxes = []

        with open(args.bbxf) as bxs:
            for line in bxs:
                bboxes.append(line)
    elif args.vector:
        if args.layer:
            layer = args.layer
        else:
            layer = None
        minx, maxx, miny, maxy = bbox_from_vector(args.vector, layer=layer)
        bboxes = [([minx, maxx], [miny, maxy])]
    elif args.vector_list:
        bboxes = []

        with open(args.vector_list) as vectors:
            for line in vectors:
                minx, maxx, miny, maxy = bbox_from_vector(line)
                bboxes.append(([minx, maxx], [miny, maxy]))

    else:
        print(
            "MysteryError: a mysterious error has occured.  No doubt you find this infuriating"
        )

    srs = get_ept_srs(args.ept)

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
        ept_window_query(minx, maxx, miny, maxy, args.ept, srs, args.out, tag=None)
