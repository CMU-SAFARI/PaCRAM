#! /bin/bash

cd Ram_scripts

echo "[INFO] Parsing singlecore results"
python3 parse_singlecore.py

echo "[INFO] Parsing multicore results"
python3 parse_multicore.py

echo "[INFO] Processing results"
python3 process_results.py

