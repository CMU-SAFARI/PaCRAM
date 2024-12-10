import os
os.chdir("Ram_scripts")

import pandas as pd
from Ram_scripts.utils_runs import *

num_exp = len(SINGLECORE_TRACES) + len(MULTICORE_TRACES)
num_finished = 0
num_failed = 0
num_running = 0
for trace in SINGLECORE_TRACES:
    output_path = f"{RAM_SRC}/../../Ram_results/singlecore/nodefense/"
    result_filename = output_path + "/stats/" + trace + ".txt"
    if get_run_status(result_filename) == "finished":
        num_finished += 1
    elif get_run_status(result_filename) == "running":
        num_running += 1
    elif get_run_status(result_filename) == "error":
        num_failed += 1

for trace_name, trace_mix in MULTICORE_TRACES.items():
    output_path = f"{RAM_SRC}/../../Ram_results/multicore/nodefense/"
    checkpoint_filename = f"{RAM_SRC}/checkpoints/multicore/llcs/" + trace_name + ".llc.txt"
    result_filename = output_path + "/stats/" + trace_name + ".txt"
    if get_run_status(result_filename) == "finished":
        num_finished += 1
    elif get_run_status(result_filename) == "running":
        num_running += 1
    elif get_run_status(result_filename) == "error":
        num_failed += 1

not_found = num_exp - num_finished - num_failed - num_running
if num_exp == num_finished:
    print("[INFO] All nodefense runs are finished.")
elif num_failed > 0:
    print("[INFO] There are failed runs. Please rerun './run_ramulator_all.sh'")
else:
    print(f"[INFO] {num_running} runs are running. {not_found} runs are not found.")


num_exp = (len(SINGLECORE_TRACES) + len(MULTICORE_TRACES)) * len(MITIGATION_LIST) * len(NRH_VALUES)
num_finished = 0
num_failed = 0
num_running = 0
for trace_name in SINGLECORE_TRACES:
    for mitigation in MITIGATION_LIST: 
        for tRH in NRH_VALUES:
            output_path = f"{RAM_SRC}/../../Ram_results/singlecore/default/" + mitigation + "/" + str(tRH) + "/"
            result_filename = output_path + "/stats/" + trace_name + ".txt"
            if get_run_status(result_filename) == "finished":
                num_finished += 1
            elif get_run_status(result_filename) == "running":
                num_running += 1
            elif get_run_status(result_filename) == "error":
                num_failed += 1

for trace_name, trace_mix in MULTICORE_TRACES.items():
    for mitigation in MITIGATION_LIST: 
        for tRH in NRH_VALUES:
            output_path = f"{RAM_SRC}/../../Ram_results/multicore/default/" + mitigation + "/" + str(tRH) + "/"
            result_filename = output_path + "/stats/" + trace_name + ".txt"
            if get_run_status(result_filename) == "finished":
                num_finished += 1
            elif get_run_status(result_filename) == "running":
                num_running += 1
            elif get_run_status(result_filename) == "error":
                num_failed += 1

not_found = num_exp - num_finished - num_failed - num_running
if num_exp == num_finished:
    print("[INFO] All default runs are finished.")
elif num_failed > 0:
    print("[INFO] There are failed runs. Please rerun './run_ramulator_all.sh'")
else:
    print(f"[INFO] {num_running} runs are running. {not_found} runs are not found.")

num_exp = (len(SINGLECORE_TRACES) + len(MULTICORE_TRACES)) * len(MITIGATION_LIST) * len(NRH_VALUES) * sum(len(values) for values in MFR_DICT.values())
num_finished = 0
num_failed = 0
num_running = 0
for mfr in MFR_DICT.keys():
    mech_csv = f"{RAM_SRC}/PaCRAM_config_mfr{mfr[-1]}.csv"
    conf_df = pd.read_csv(mech_csv)
    conf_df = conf_df[conf_df["norm_tras"].isin(MFR_DICT[mfr])]
    latency_factor_list = conf_df["norm_tras"].tolist()
    nRH_factor_list = conf_df["n_nRH"].tolist()
    th_pcr_list = conf_df["th_pcr"].tolist()
    for latency_factor, nRH_factor, th_pcr in zip(latency_factor_list, nRH_factor_list, th_pcr_list):
        for trace_name in SINGLECORE_TRACES:
            for mitigation in MITIGATION_LIST: 
                for base_tRH in NRH_VALUES:
                    output_path = f"{RAM_SRC}/../../Ram_results/singlecore/PaCRAM-{mfr[-1]}/" + mitigation + "/" + str(base_tRH) + "/" + str(latency_factor).replace(".", "_") + "/"
                    result_filename = output_path + "/stats/" + trace_name + ".txt"
                    if get_run_status(result_filename) == "finished":
                        num_finished += 1
                    elif get_run_status(result_filename) == "running":
                        num_running += 1
                    elif get_run_status(result_filename) == "error":
                        num_failed += 1

for mfr in MFR_DICT.keys():
    mech_csv = f"{RAM_SRC}/PaCRAM_config_mfr{mfr[-1]}.csv"
    conf_df = pd.read_csv(mech_csv)
    conf_df = conf_df[conf_df["norm_tras"].isin(MFR_DICT[mfr])]
    latency_factor_list = conf_df["norm_tras"].tolist()
    nRH_factor_list = conf_df["n_nRH"].tolist()
    th_pcr_list = conf_df["th_pcr"].tolist()
    for latency_factor, nRH_factor, th_pcr in zip(latency_factor_list, nRH_factor_list, th_pcr_list):
        for trace_name, trace_mix in MULTICORE_TRACES.items():
            for mitigation in MITIGATION_LIST: 
                for base_tRH in NRH_VALUES:
                    output_path = f"{RAM_SRC}/../../Ram_results/multicore/PaCRAM-{mfr[-1]}/" + mitigation + "/" + str(base_tRH) + "/" + str(latency_factor).replace(".", "_") + "/"
                    result_filename = output_path + "/stats/" + trace_name + ".txt"
                    if get_run_status(result_filename) == "finished":
                        num_finished += 1
                    elif get_run_status(result_filename) == "running":
                        num_running += 1
                    elif get_run_status(result_filename) == "error":
                        num_failed += 1

not_found = num_exp - num_finished - num_failed - num_running
if num_exp == num_finished:
    print("[INFO] All mechanism runs are finished.")
elif num_failed > 0:
    print("[INFO] There are failed runs. Please rerun './run_ramulator_all.sh'")
else:
    print(f"[INFO] {num_running} runs are running. {not_found} runs are not found.")
    