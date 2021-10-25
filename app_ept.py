import argparse
import os
#import pdal
from string import Template
import json
import subprocess
from pprint import pprint



def ept_window_query(xmin, xmax, ymin, ymax, ept, srs, outpath, tag=None):
    ''' '''

    # make a tag for the output file
    loc = f'{int(xmin)}_{int(xmax)}_{int(ymin)}_{int(ymax)}'
    if tag:
        f = f'{loc}_{tag}'
    else:
        f = f'{loc}'
    of = os.path.join(outpath, f + '.las')

    # make pipeline
    bbox = ([xmin, xmax], [ymin, ymax])
    pipeline = make_pipe(ept, bbox, of, srs)
    json_file = os.path.join(outpath, f'{f}.json')
    with open(json_file, 'w') as j:
        json.dump(pipeline, j)
    
    #make pdal comand
    cmd = f'pdal pipeline -i {json_file} --developer-debug'
    _ = subprocess.run(cmd, shell=True, capture_output=True)
    print(f'stdout:\n{_.stdout}\n\n\nerrors:\n{_.stderr}') 

def make_pipe(ept, bbox, out_path, srs, threads=4, resolution=1):
    '''Creates, validates and then returns the pdal pipeline
    
    Arguments:
    ept        -- String -Path to ept file.
    bbox       -- Tuple  - Bounding box in srs coordintes,
                  in the form: ([xmin, xmax], [ymin, ymax]).
    out_path   -- String - Path where the CHM shall be saved. Must include .tif exstension.
    srs        -- String - EPSG identifier for srs  being used. Defaults to EPSG:3857
                  because that is what ept files tend to use.
    threads    -- Int    - Number os threads to be used by the reader.ept. Defaults to 4.
    resolution -- Int or Float - resolution (m) used by writers.gdal
    '''

    pipe = {
        "pipeline": [
            {
            "bounds": f'{bbox}',
            "filename": ept,
            "type": "readers.ept",
            "tag": "readdata",
            "spatialreference": srs,
            "threads": threads
            },
            {
            "type":"filters.outlier",
            "method":"radius",
            "radius":1.0,
            "min_k":4
            },
            {
            "type":"filters.range",
            "limits":"returnnumber[1:1]"
            },
            {
            "type": "writers.las",
            "filename": out_path,
            "a_srs": srs
            }
        ]}
    return(pipe) 
    

    #pipeline = pdal.Pipeline(pipe)
    #if pipeline.validate():
    #return(pipeline)
    #else:
    #    raise Exception('Bad pipeline (sorry to be so ambigous)!')




if __name__ == '__main__':
    '''Returns subsets of supplied files clipped to bbox supplied in command or multiple bboxs specified in file using --bbxf '''

    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--bbox', type=str, required=False,
    help='''The extents of the resource to select in 2 dimensions, expressed as a string,
    in the format: '([xmin, xmax], [ymin, ymax])' ''')
    parser.add_argument('--bbxf', type=str, required=False, help='''path to file with a bbox on each line''') 
    parser.add_argument('--ept', type=str, required=True, help='path to ept')
    parser.add_argument('--srs', type=str, required=True, help='EPSG code of srs of files, all files must be in the same coordinate system')
    parser.add_argument('--out', type=str, required=True, help='path to output directory')
    args = parser.parse_args() 

    # make list off bboxes
    if args.bbox:
        bboxes = [args.bbox]
    elif args.bbxf:
        bboxes = []
        #try:
        with open(args.bbxf) as bxs:
            for line in bxs:
                bboxes.append(line)
    else:
        print('One must either specify --bbox or --bbxf')

    for bbox in bboxes:
        # unpack the bbox string
        xmin, xmax, ymin, ymax = bbox.strip('()').replace('[', '').replace(']','').split(',')
        xmin = float(xmin)
        xmax = float(xmax)
        ymin = float(ymin)
        ymax = float(ymax)

        #make a laz for the window from ept.
        ept_window_query(xmin, xmax, ymin, ymax, args.ept, args.srs, args.out, tag=None)