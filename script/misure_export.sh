#!/bin/bash

set -x
set -e
set -u
set -o pipefail

folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "${folder}"/tmp
mkdir -p "${folder}"/../data/misure/parquet

debug=false

if [ "$debug" = true ]; then
  find "${folder}"/../data/misure/parquet -name "*.parquet" -delete
fi

find ../data/misure/raw -name "*.zip" | while read zip_file; do
  name=$(basename "$zip_file" .zip)

  if [ -f "${folder}"/../data/misure/parquet/"${name}"_misure.parquet ]; then
    echo "già creato"
  else
    echo "lo creo"

    # estrai file xml
    unzip -p "$zip_file" | sed "s/\x02/ /g;s/\x10/ /g;s/\x1A/'/g" >"${folder}"/tmp/"$name".xml

    # fai il flattening dell'xml
    python3 misure_flattening.py -i "${folder}"/tmp/"$name".xml -of "${folder}"/../data/misure/parquet

    # elimina file xml
    find "${folder}"/tmp/ -name "*.xml" -delete
  fi

done

# crea array suffissi: strumenti,misure,settori,obiettivi,dotazioni,aree
suffissi=("strumenti" "misure" "settori" "obiettivi" "dotazioni" "aree")

for suffisso in "${suffissi[@]}"; do
  duckdb -c "COPY (select * from read_parquet('${folder}/../data/misure/parquet/*_${suffisso}*.parquet',union_by_name=True)) TO '${folder}/../data/misure/misure_${suffisso}.parquet' (FORMAT 'PARQUET',CODEC  'ZSTD')"
done
