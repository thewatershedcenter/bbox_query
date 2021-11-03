#!/bin/sh

EPT=''
vector_dir=''

print_usage() {
  printf "Usage: Is this worth it since it runs in a container?"
}

while getopts 'e:dv' flag; do
  case "${flag}" in
    e) EPT="${OPTARG}" ;;
    d) vector="--vector_dir ${OPTARG}" ;;
    v) vector="--vector ${OPTARG}" ;;
    *) print_usage
       exit 1 ;;
  esac
done


python app_ept.py  --ept=$EPT --out=/out $vector
