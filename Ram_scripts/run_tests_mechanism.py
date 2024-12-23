import os, yaml, copy, time, sys
import pandas as pd
from calc_rh_parameters import *
from utils_runs import *
from utils_slurm import *
from math import log2

is_slurm = (sys.argv[1] == "slurm")

base_config_file = RAM_SRC + "base_config.yaml"
    
base_config = None
with open(base_config_file, 'r') as stream:
    try:
        base_config = yaml.safe_load(stream)
    except yaml.YamlError as exc:
        print(exc)
if(base_config == None):
    print("Error: base config is None")
    exit(1)

TREFWMS = 32

### Singlecore runs
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
                    checkpoint_filename = f"{RAM_SRC}/checkpoints/singlecore/llcs/" + trace_name + ".llc.txt"

                    for path in [output_path + "/stats", output_path + "/configs", output_path + "/cmd_count"]:
                        if not os.path.exists(path):
                            os.makedirs(path)

                    tRH = int(base_tRH * nRH_factor)
                    result_filename = output_path + "/stats/" + trace_name + ".txt"
                    if get_run_status(result_filename) == "running" or get_run_status(result_filename) == "finished":
                        continue
                    config_filename = output_path + "/configs/" + trace_name + ".yaml"
                    cmd_count_filename = output_path + "/cmd_count/" + trace_name + ".cmd.count"
                    config = copy.deepcopy(base_config)
                    config_file = open(config_filename, "w")
                    
                    config['Frontend']['traces'] = [TRACE_PATH + trace_name]
                    config['Frontend']['llc_deserialize'] = True
                    config['Frontend']['llc_deserialization_filename'] = checkpoint_filename

                    config['MemorySystem']['BHDRAMController']['plugins'][0]['ControllerPlugin']['path'] = cmd_count_filename
                    config['MemorySystem']['DRAM']['latency_factor_vrr'] = latency_factor
                    config['MemorySystem']['DRAM']['latency_factor_rfc'] = 1.0

                    pacram_th_pcr = int(th_pcr)
                    if(mitigation == "PARA"):
                        threshold = get_para_parameters(tRH)
                        num_act_for_refresh = log2(1 - 0.8) / log2(1-threshold)
                        pacram_set_period_ns = int((th_pcr) * (num_act_for_refresh * 45 + 240 * latency_factor))
                        if(pacram_set_period_ns >= TREFWMS*1000*1000):
                            pacram_set_period_ns = 0
                        config['MemorySystem']['BHDRAMController']['plugins'].append({'ControllerPlugin' : {'impl': 'PARA', 'threshold': threshold, 'pacram': True, 'pacram_set_period_ns': pacram_set_period_ns}})
                    elif(mitigation == "Graphene"):
                        num_table_entries, activation_threshold, reset_period_ns = get_graphene_parameters(tRH, TREFWMS)
                        pacram_set_period_ns = int((th_pcr) * (activation_threshold * 45 + 240 * latency_factor))
                        if(pacram_set_period_ns >= TREFWMS*1000*1000):
                            pacram_set_period_ns = 0
                        config['MemorySystem']['BHDRAMController']['plugins'].append({'ControllerPlugin' : {'impl': 'Graphene', 'num_table_entries': num_table_entries, 'activation_threshold': activation_threshold, 'reset_period_ns': reset_period_ns, 'pacram': True, 'pacram_set_period_ns': pacram_set_period_ns}})
                    elif(mitigation == "Hydra"):
                        hydra_tracking_threshold, hydra_group_threshold, hydra_row_group_size, hydra_reset_period_ns, hydra_rcc_num_per_rank, hydra_rcc_policy = get_hydra_parameters(tRH, TREFWMS)
                        pacram_set_period_ns = int((th_pcr) * (hydra_tracking_threshold * 45 + 240 * latency_factor))
                        if(pacram_set_period_ns >= TREFWMS*1000*1000):
                            pacram_set_period_ns = 0
                        config['MemorySystem']['BHDRAMController']['plugins'].append({'ControllerPlugin' : {'impl': 'Hydra', 'hydra_tracking_threshold': hydra_tracking_threshold, 'hydra_group_threshold': hydra_group_threshold, 'hydra_row_group_size': hydra_row_group_size, 'hydra_reset_period_ns': hydra_reset_period_ns, 'hydra_rcc_num_per_rank': hydra_rcc_num_per_rank, 'hydra_rcc_policy': hydra_rcc_policy, 'pacram': True, 'pacram_set_period_ns': pacram_set_period_ns}})
                    elif(mitigation == "RFM"):
                        rfm_threshold = get_rfm_parameters(tRH)
                        pacram_set_period_ns = int((th_pcr) * (rfm_threshold * 46 + 260 * latency_factor))
                        if(pacram_set_period_ns >= TREFWMS*1000*1000):
                            pacram_set_period_ns = 0
                        config['MemorySystem']['BHDRAMController']['plugins'].append({'ControllerPlugin' : {'impl': 'RFMManager', 'rfm_threshold': rfm_threshold, 'pacram': True, 'pacram_set_period_ns': pacram_set_period_ns}})
                    elif(mitigation == "PRAC"):
                        abo_threshold = get_prac_parameters(tRH, ABO_refs=4)
                        pacram_set_period_ns = int((th_pcr) * (abo_threshold * 46 + 260 * latency_factor))
                        if(pacram_set_period_ns >= TREFWMS*1000*1000):
                            pacram_set_period_ns = 0
                        config["MemorySystem"]["DRAM"]["PRAC"] = True
                        config["MemorySystem"]["BHDRAMController"]["impl"] = "PRACDRAMController"
                        config["MemorySystem"]["BHDRAMController"]["BHScheduler"]["impl"] = "PRACScheduler"
                        config["MemorySystem"]["BHDRAMController"]["plugins"].append({"ControllerPlugin" : {"impl": "PRAC", "abo_threshold": abo_threshold, "abo_delay_acts": 4, "abo_recovery_refs": 4, 'pacram': True, 'pacram_set_period_ns': pacram_set_period_ns}})
        
                    if is_slurm:
                        cmd = f"{SLURM_CMD} {RAM_SRC}/ramulator2 -c '{config}' > {result_filename} 2>&1 &"
                    else:
                        cmd = f"{RAM_SRC}/ramulator2 -c '{config}' > {result_filename} 2>&1"  
                    
                    yaml.dump(config, config_file, default_flow_style=False)
                    config_file.close()
                    
                    if is_slurm:
                        while check_running_jobs() >= MAX_SLURM_JOBS:
                            print(f"[INFO] Maximum Slurm Job limit ({MAX_SLURM_JOBS}) reached. Retrying in {SLURM_RETRY_DELAY} seconds")
                            time.sleep(SLURM_RETRY_DELAY)
                    print("Running: mfr = " + mfr + ", trace = " + trace_name + ", mitigation = " + mitigation + ", tRH = " + str(base_tRH) + ", latency_factor = " + str(latency_factor))
                    os.system(cmd)

                    time.sleep(0.1)

### Multicore runs
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
                    checkpoint_filename = f"{RAM_SRC}/checkpoints/multicore/llcs/" + trace_name + ".llc.txt"

                    for path in [output_path + "/stats", output_path + "/configs", output_path + "/cmd_count"]:
                        if not os.path.exists(path):
                            os.makedirs(path)

                    tRH = int(base_tRH * nRH_factor)
                    result_filename = output_path + "/stats/" + trace_name + ".txt"
                    if get_run_status(result_filename) == "running" or get_run_status(result_filename) == "finished":
                        continue
                    config_filename = output_path + "/configs/" + trace_name + ".yaml"
                    cmd_count_filename = output_path + "/cmd_count/" + trace_name + ".cmd.count"
                    config = copy.deepcopy(base_config)
                    config_file = open(config_filename, "w")
                    
                    config['Frontend']['traces'] = [TRACE_PATH + trace for trace in trace_mix]
                    config['Frontend']['llc_deserialize'] = True
                    config['Frontend']['llc_deserialization_filename'] = checkpoint_filename

                    config['MemorySystem']['BHDRAMController']['plugins'][0]['ControllerPlugin']['path'] = cmd_count_filename
                    config['MemorySystem']['DRAM']['latency_factor_vrr'] = latency_factor
                    config['MemorySystem']['DRAM']['latency_factor_rfc'] = 1.0

                    pacram_th_pcr = int(th_pcr)
                    if(mitigation == "PARA"):
                        threshold = get_para_parameters(tRH)
                        num_act_for_refresh = log2(1 - 0.8) / log2(1-threshold)
                        pacram_set_period_ns = int((th_pcr) * (num_act_for_refresh * 46 + 240 * latency_factor))
                        if(pacram_set_period_ns >= TREFWMS*1000*1000):
                            pacram_set_period_ns = 0
                        config['MemorySystem']['BHDRAMController']['plugins'].append({'ControllerPlugin' : {'impl': 'PARA', 'threshold': threshold, 'pacram': True, 'pacram_set_period_ns': pacram_set_period_ns}})
                    elif(mitigation == "Graphene"):
                        num_table_entries, activation_threshold, reset_period_ns = get_graphene_parameters(tRH, TREFWMS)
                        pacram_set_period_ns = int((th_pcr) * (activation_threshold * 46 + 240 * latency_factor))
                        if(pacram_set_period_ns >= TREFWMS*1000*1000):
                            pacram_set_period_ns = 0
                        config['MemorySystem']['BHDRAMController']['plugins'].append({'ControllerPlugin' : {'impl': 'Graphene', 'num_table_entries': num_table_entries, 'activation_threshold': activation_threshold, 'reset_period_ns': reset_period_ns, 'pacram': True, 'pacram_set_period_ns': pacram_set_period_ns}})
                    elif(mitigation == "Hydra"):
                        hydra_tracking_threshold, hydra_group_threshold, hydra_row_group_size, hydra_reset_period_ns, hydra_rcc_num_per_rank, hydra_rcc_policy = get_hydra_parameters(tRH, TREFWMS)
                        pacram_set_period_ns = int((th_pcr) * (hydra_tracking_threshold * 46 + 240 * latency_factor))
                        if(pacram_set_period_ns >= TREFWMS*1000*1000):
                            pacram_set_period_ns = 0
                        config['MemorySystem']['BHDRAMController']['plugins'].append({'ControllerPlugin' : {'impl': 'Hydra', 'hydra_tracking_threshold': hydra_tracking_threshold, 'hydra_group_threshold': hydra_group_threshold, 'hydra_row_group_size': hydra_row_group_size, 'hydra_reset_period_ns': hydra_reset_period_ns, 'hydra_rcc_num_per_rank': hydra_rcc_num_per_rank, 'hydra_rcc_policy': hydra_rcc_policy, 'pacram': True, 'pacram_set_period_ns': pacram_set_period_ns}})
                    elif(mitigation == "RFM"):
                        rfm_threshold = get_rfm_parameters(tRH)
                        pacram_set_period_ns = int((th_pcr) * (rfm_threshold * 46 + 260 * latency_factor))
                        if(pacram_set_period_ns >= TREFWMS*1000*1000):
                            pacram_set_period_ns = 0
                        config['MemorySystem']['BHDRAMController']['plugins'].append({'ControllerPlugin' : {'impl': 'RFMManager', 'rfm_threshold': rfm_threshold, 'pacram': True, 'pacram_set_period_ns': pacram_set_period_ns}})
                    elif(mitigation == "PRAC"):
                        abo_threshold = get_prac_parameters(tRH, ABO_refs=4)
                        pacram_set_period_ns = int((th_pcr) * (abo_threshold * 46 + 260 * latency_factor))
                        if(pacram_set_period_ns >= TREFWMS*1000*1000):
                            pacram_set_period_ns = 0
                        config["MemorySystem"]["DRAM"]["PRAC"] = True
                        config["MemorySystem"]["BHDRAMController"]["impl"] = "PRACDRAMController"
                        config["MemorySystem"]["BHDRAMController"]["BHScheduler"]["impl"] = "PRACScheduler"
                        config["MemorySystem"]["BHDRAMController"]["plugins"].append({"ControllerPlugin" : {"impl": "PRAC", "abo_threshold": abo_threshold, "abo_delay_acts": 4, "abo_recovery_refs": 4, 'pacram': True, 'pacram_set_period_ns': pacram_set_period_ns}})
        
                    if is_slurm:
                        cmd = f"{SLURM_CMD} {RAM_SRC}/ramulator2 -c '{config}' > {result_filename} 2>&1 &"
                    else:
                        cmd = f"{RAM_SRC}/ramulator2 -c '{config}' > {result_filename} 2>&1"  
                    
                    yaml.dump(config, config_file, default_flow_style=False)
                    config_file.close()
                    
                    if is_slurm:
                        while check_running_jobs() >= MAX_SLURM_JOBS:
                            print(f"[INFO] Maximum Slurm Job limit ({MAX_SLURM_JOBS}) reached. Retrying in {SLURM_RETRY_DELAY} seconds")
                            time.sleep(SLURM_RETRY_DELAY)
                    print("Running: mfr = " + mfr + ", trace = " + trace_name + ", mitigation = " + mitigation + ", tRH = " + str(base_tRH) + ", latency_factor = " + str(latency_factor))
                    os.system(cmd)

                    time.sleep(0.1)

print("[INFO] All PaCRAM runs are started.")
