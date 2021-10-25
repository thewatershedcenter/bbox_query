#!/bin/sh

while getopts ":h" option; do
   case $option in
      h) # display Help
        echo "SYNOPSIS"  
        echo "     has args"
        echo "DESCRIPTION"
        echo "     does things"
        exit;;
   esac
done

OUTPATH=$1
DATAPATH=$2
CHM=$3
DTM=$4
DSM=$5
EPT=$6
BBOX=$7
SRS=$8

docker build docker_rasterio -t rasterio_docker && \
docker run --rm -it -v $PWD:/work  -v $OUTPATH:/out -v $DATAPATH:/data -e USER=$USER -e HOME=/work -w /work rasterio_docker /data/$CHM /data/$DTM /data/$DSM $BBOX $SRS

#docker build docker_pdal -t pdal_docker && \
#docker run --rm -it -v $PWD:/work -v $OUTPATH:/out -v $DATAPATH:/data -e USER=$USER -e HOME=/work -w /work pdal_docker $BBOX $SRS /data/$EPT

#./start.sh /media/data/AOP/train /media/data/AOP data/chm.vrt data/dtm.vrt data/dsm.vrt entwine/ '([319864,319925],[4096389,4096442])' EPSG:26911