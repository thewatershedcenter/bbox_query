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

docker run --rm -it -v $PWD:/work  -v $OUTPATH:/out -u $(id -u):$(id -g) -e HOME=/work -w /work quay.io/kulpojke/bbox_query:ept-sha-8167227 $BBOX $SRS $EPT

#./start.sh ~/Downloads https://storage.googleapis.com/monument_bucket/carr/entwine/ept.json 