#!/bin/sh

BBOX=$1
SRS=$2
EPT=$3
echo "------------------------------------------------------------------------"

python app_ept.py --bbox=$BBOX --srs=$SRS --ept=$EPT --out=/out