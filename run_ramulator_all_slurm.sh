#! /bin/bash

cd Ram_scripts

echo "[INFO] Running Ramulator nodefense runs"
python3 run_tests_nodefense.py slurm

echo "[INFO] Running Ramulator default runs"
python3 run_tests_default.py slurm

echo "[INFO] Running Ramulator mechanism runs"
python3 run_tests_mechanism.py slurm


