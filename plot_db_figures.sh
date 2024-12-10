#! /bin/bash

cd DB_scripts

echo "[INFO] Processing DB_results"
python3 process_NRH.py
python3 process_BER.py
python3 process_RPCR.py

echo "[INFO] Plotting DB_results"
python3 plot_fig6.py
python3 plot_fig9.py
python3 plot_fig11.py
