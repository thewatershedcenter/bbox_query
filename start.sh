#!/bin/sh

while getopts ":h" option; do
   case $option in
      h) # display Help
        echo "SYNOPSIS:"  
        echo "     Uses PDAL to return a pointcloud for the interior of"
        echo "     given polygon(s)"
        echo "USAGE:"
        echo "     ./start.sh [ vector_path ] [ ept ] [ out_path ]"
        echo "      "
        echo "      vector_path - Path (url might work) to a vector file or a"
        echo "      directory of vector files."
        echo "      "
        echo "      ept - url or path to ept file."
        echo "      "
        echo "      out_path - path where output las files will be saved."
        exit;;
   esac
done

# TODO: add option to re-pull image

V=$1
EPT=$2
OUT=$3

#docker pull quay.io/kulpojke/bbox_query:latest && \
docker run --rm -it -v $PWD:/work  -v $OUT:/out -u $(id -u):$(id -g) -e HOME=/work -w /work quay.io/kulpojke/bbox_query:latest --ept=$EPT --vector=$V --out=/out