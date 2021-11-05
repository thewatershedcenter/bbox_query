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


V=$1
EPT=$2

#docker pull quay.io/kulpojke/bbox_query:latest && \
docker run --rm -it -v $PWD:/work  -v /media/data/Downloads:/out -u $(id -u):$(id -g) -e HOME=/work -w /work quay.io/kulpojke/bbox_query:latest --ept=$EPT --vector=$V --out=/out