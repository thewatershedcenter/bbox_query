#%%
from importlib import reload
import app_ept
from app_ept import *
reload(app_ept)
from app_ept import *

vector = '/media/data/WRTC/bbox_query/test/test_buff.shp'
ept = 'https://storage.googleapis.com/monument_bucket/CarrHirzDelta_1/entwine/ept.json'
outpath = '/media/data/Downloads'
fname = 'GALNAKRAFTORNA'

def xy_test(to_srs, vector=vector, layer=None):
    '''
    Tests to see if points are within bounds of
    the tile which containe the test polygon.
    '''

    transform = get_transform(vector, to_srs)
    minx, maxx, miny, maxy = bbox_from_vector(vector, layer=layer)

    minx, miny, minz = transform.TransformPoint(miny, minx)
    maxx, maxy, maxz = transform.TransformPoint(maxy, maxx)

    ref = {
        "maxx": 489749.99,
        "maxy": 4514999.99,
        "maxz": 954.45,
        "minx": 489000,
        "miny": 4514250,
        "minz": 245.61
    }

    test = {
        "maxx": maxx < ref['maxx'],
        "maxy": maxy < ref['maxy'],
        "minx": minx > ref['minx'],
        "miny": miny > ref['miny']
    }

    return test


xy_test(6339)


# %%
import pandas as pd
import matplotlib.pyplot as plt

usgs = pd.DataFrame({'x': [489000, 489000, 489749.99, 489749.99],
                     'y': [4514250, 4514999.99, 4514999.99, 4514250]})

geometry = gpd.points_from_xy(usgs['x'], usgs['y'])

usgs = gpd.GeoDataFrame(usgs, geometry=geometry, crs=6339)

s = transform_vector(vector, srs)

# create the plot
fig, ax = plt.subplots(figsize=(12, 8))
usgs.plot(ax=ax)
s.plot(ax=ax)

# %%
# get the bbox from the vector
x, y = s.geometry.envelope.exterior.values[0].coords.xy
minx, maxx, miny, maxy = min(x), max(x), min(y), max(y)

# pack up the bbox into the bboxes list
bboxes = [([minx, maxx], [miny, maxy])]

query_from_list(bboxes, srs, outpath, fname, ept)
# %%
