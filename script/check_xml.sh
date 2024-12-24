#!/bin/bash

set -x
set -e
set -u
set -o pipefail

folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

LOG_FILE="caratteri_invalidi.log"
TEMP_DIR="/tmp/check_xml_temp"

> "$LOG_FILE"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

find ../data/aiuti/raw -name "*.zip" | while read zip_file; do
    echo "Verifica: $zip_file"
    unzip -q "$zip_file" -d "$TEMP_DIR"

    find "$TEMP_DIR" -name "*.xml" | while read xml_file; do
        filename=$(basename "$xml_file")

        # Verifica caratteri invalidi e log
        if grep -q $'\x02' "$xml_file"; then
            echo "$filename,\\x02" >> "$LOG_FILE"
        fi
        if grep -q $'\x10' "$xml_file"; then
            echo "$filename,\\x10" >> "$LOG_FILE"
        fi
        if grep -q $'\x1a' "$xml_file"; then
            echo "$filename,\\x1A" >> "$LOG_FILE"
        fi

        # Validazione XML con sostituzione caratteri invalidi
        cat "$xml_file" | sed "s/\x02/ /g;s/\x10/ /g;s/\x1A/'/g" | xmlstarlet val -e -
    done

    rm -rf "$TEMP_DIR"/*
done

rm -rf "$TEMP_DIR"
