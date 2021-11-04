from app_ept import *
import pandas as pd

vector = '/test/test_buff.shp'

outpath = '.'
fname = 'GALNAKRAFTORNA'

usgs = pd.DataFrame({'x': [489000, 489000, 489749.99, 489749.99],
                     'y': [4514250, 4514999.99, 4514999.99, 4514250]})


def test_get_ept_srs():
    ept = 'https://storage.googleapis.com/monument_bucket/CarrHirzDelta_1/entwine/ept.json'
    assert get_ept_srs(ept) == 'EPSG:6339'
