#! /bin/bash

echo "[INFO] Installing Python dependencies"
pip3 install -r requirements.txt

mkdir DB_results
if [ "$(ls -A DB_results/)" ]; then
    echo "[INFO] DB_results/ directory is not empty. Skipping download"
else
    echo "[INFO] DB_results/ directory is empty"
    echo "[INFO] Downloading the results into ./DB_results"
    wget https://zenodo.org/records/14343791/files/PaCRAM_DB.tar.gz
    echo "[INFO] Decompressing the results into ./DB_results"
    tar -xzf PaCRAM_DB.tar.gz -C DB_results --no-same-owner
fi

mkdir -p Ram_scripts/ramulator_pacram/cputraces/
if [ "$(ls -A Ram_scripts/ramulator_pacram/cputraces/)" ]; then
    echo "[INFO] cputraces/ directory is not empty. Skipping download"
else
    echo "[INFO] cputraces/ directory is empty"
    echo "[INFO] Downloading the traces into cputraces"
    wget https://zenodo.org/records/14345886/files/PaCRAM_Ram_traces.tar.gz
    echo "[INFO] Decompressing the traces into cputraces"
    tar -xzf PaCRAM_Ram_traces.tar.gz -C Ram_scripts/ramulator_pacram/cputraces --no-same-owner
fi

cd Ram_scripts/ramulator_pacram
echo "[INFO] Compiling Ramulator2"
cmake .
make -j
