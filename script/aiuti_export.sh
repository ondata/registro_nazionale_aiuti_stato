#!/bin/bash

set -x
set -e
set -u
set -o pipefail

folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "${folder}"/tmp
mkdir -p "${folder}"/../data/aiuti/parquet

debug=false

if [ "$debug" = true ]; then
  find "${folder}"/../data/aiuti/parquet -name "*.parquet" -delete
fi

find ../data/aiuti/raw -name "*.zip" | while read zip_file; do
  name=$(basename "$zip_file" .zip)

  if [ -f "${folder}"/../data/aiuti/parquet/"${name}"_aiuti.parquet ]; then
    echo "già creato"
  else
    echo "lo creo"

    # estrai file xml
    unzip -p "$zip_file" | sed "s/\x02/ /g;s/\x10/ /g;s/\x1A/'/g" >"${folder}"/tmp/"$name".xml

    # fai il flattening dell'xml in aiuti, componenti e strumenti
    python3 flattening.py -i "${folder}"/tmp/"$name".xml -of "${folder}"/../data/aiuti/parquet

    # elimina file xml
    find "${folder}"/tmp/ -name "*.xml" -delete
  fi

done
