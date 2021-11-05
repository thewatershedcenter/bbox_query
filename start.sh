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
        echo "      vector_path - Relative path from PWD to a vector file or a"
        echo "      directory of vector files (must be within PWD)."
        echo "      "
        echo "      ept - url to ept file."
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
docker run --rm -it -v $PWD:/work  -v $OUT:/out -u $(id -u):$(id -g) -e HOME=/work -w /work quay.io/kulpojke/bbox_query:ept-sha-93942e0 --ept=$EPT --vector=$V --out=/out

echo "Done !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"