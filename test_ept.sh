#!/bin/sh

V='/work/test/test_buff.shp'
EPT='https://storage.googleapis.com/monument_bucket/CarrHirzDelta_1/entwine/ept.json'

#docker pull quay.io/kulpojke/bbox_query:latest && \
docker run --rm -it -v $PWD:/work  -v /media/data/Downloads:/out -u $(id -u):$(id -g) -e HOME=/work -w /work quay.io/kulpojke/bbox_query:latest --ept=$EPT --vector=$V --out=/out
