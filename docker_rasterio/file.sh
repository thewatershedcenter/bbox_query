#!/bin/sh

CHM=$1
DTM=$2
DSM=$3
BBOX=$4
SRS=$5
echo "------------------------------------------------------------------------"
echo $BBOX

python app_vrt.py --bbox=$BBOX --chm=$CHM --dtm=$DTM --dsm=$DSM --srs=$SRS --out=/out