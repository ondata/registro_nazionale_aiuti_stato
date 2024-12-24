#!/bin/bash

set -x
set -e
set -u
set -o pipefail

folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "${folder}"/../data
mkdir -p "${folder}"/../data/misure/raw
mkdir -p "${folder}"/../data/aiuti
mkdir -p "${folder}"/../data/aiuti/raw

mkdir -p "${folder}"/tmp

# Misure

curl -kL "https://www.rna.gov.it/open-data/misure-agevolative" | scrape -be '//a[@data-nid]' | xq -c '.html.body.a[]' >"${folder}"/tmp/misure.jsonl

mlr -I --jsonl cut -x -f span then rename -r "@","" then rename -g -r "[-]","_" then filter '${data_file_ext}=="zip"' then uniq -a "${folder}"/tmp/misure.jsonl

cp "${folder}"/tmp/misure.jsonl "${folder}"/../data/misure/misure.jsonl

## estrai elenco URL

if [ -f "${folder}"/tmp/lista.jsonl ]; then
  rm "${folder}"/tmp/lista.jsonl
fi

while read -r line; do
  id=$(echo "$line" | jq -r '.data_nid')
  data_filename=$(echo "$line" | jq -r '.data_filename')
  curl 'https://www.rna.gov.it/opendata/misure-agevolative/download' \
    -H 'Accept: */*' \
    -H 'Content-Type: application/json' \
    -H 'Origin: https://www.rna.gov.it' \
    -H 'Referer: https://www.rna.gov.it/open-data/misure-agevolative' \
    --data-raw '{"nids":"'"$id"'","file_extension":"zip"}' |
    jq -c '. + {file: "'"$id"'", filename:"'"$data_filename"'"}' >>"${folder}"/tmp/lista.jsonl
done <"${folder}"/tmp/misure.jsonl

cp "${folder}"/tmp/lista.jsonl "${folder}"/../data/misure/lista.jsonl

## scarica dati grezzi

while read -r line; do
  path=$(echo "$line" | jq -r '.content')
  filename=$(echo "$line" | jq -r '.filename' | sed -r 's/\..+//')
  if [ -f "${folder}"/../data/misure/raw/${filename}.zip ]; then
    echo "esiste già"
  else
    curl -o "${folder}"/../data/misure/raw/${filename}.zip "https://www.rna.gov.it${path}"
  fi
done <"${folder}"/tmp/lista.jsonl

# Aiuti

curl -kL "https://www.rna.gov.it/open-data/aiuti" | scrape -be '//a[@data-nid]' | xq -c '.html.body.a[]' >"${folder}"/tmp/aiuti.jsonl

mlr -I --jsonl cut -x -f span then rename -r "@","" then rename -g -r "[-]","_" then filter '${data_file_ext}=="zip"' then uniq -a "${folder}"/tmp/aiuti.jsonl

cp "${folder}"/tmp/aiuti.jsonl "${folder}"/../data/misure/aiuti.jsonl

## estrai elenco URL

if [ -f "${folder}"/tmp/lista.jsonl ]; then
  rm "${folder}"/tmp/lista.jsonl
fi

while read -r line; do
  id=$(echo "$line" | jq -r '.data_nid')
  data_filename=$(echo "$line" | jq -r '.data_filename')
  curl 'https://www.rna.gov.it/opendata/misure-agevolative/download' \
    -H 'Accept: */*' \
    -H 'Content-Type: application/json' \
    -H 'Origin: https://www.rna.gov.it' \
    -H 'Referer: https://www.rna.gov.it/open-data/aiuti' \
    --data-raw '{"nids":"'"$id"'","file_extension":"zip"}' |
    jq -c '. + {file: "'"$id"'", filename:"'"$data_filename"'"}' >>"${folder}"/tmp/lista.jsonl
done <"${folder}"/tmp/aiuti.jsonl

cp "${folder}"/tmp/lista.jsonl "${folder}"/../data/aiuti/lista.jsonl

## scarica dati grezzi

while read -r line; do
  path=$(echo "$line" | jq -r '.content')
  filename=$(echo "$line" | jq -r '.filename' | sed -r 's/\..+//')
  if [ -f "${folder}"/../data/aiuti/raw/${filename}.zip ]; then
    echo "esiste già"
  else
    curl -o "${folder}"/../data/aiuti/raw/${filename}.zip "https://www.rna.gov.it${path}"
  fi
done <"${folder}"/tmp/lista.jsonl
