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
EPT=$2
BBOX=$3
SRS=$4

docker run --rm -it -v $PWD:/work  -v $OUTPATH:/out -v -u $(id -u):$(id -g) -e HOME=/work -w /work quay.io/kulpojke/bbox_query:ept-sha-45426f6 $BBOX $SRS $EPT

#./start.sh ~/Downloads /media/data/AOP data/chm.vrt data/dtm.vrt data/dsm.vrt entwine/ '([319864,319925],[4096389,4096442])' EPSG:26911