import os
import pandas as pd
from utils_runs import *
from utils_parser import *

PWD = os.getcwd()
CSV_DIR = f"{PWD}/../Ram_results/processed/"
if not os.path.exists(CSV_DIR):
    os.makedirs(CSV_DIR)


### Process nodefense runs
csv_filename = CSV_DIR + "singlecore_nodefense.csv"
if os.path.exists(csv_filename):
    os.remove(csv_filename)

metrics_per_core = ["core_0"] + ["inst_0"]
name_metrics_per_core =  ["cycles_recorded_core_", "insts_recorded_core_"]
metrics = ["total_energy"]
name_metrics = ["total_energy"]

df = pd.DataFrame(columns=["trace"] 
                + metrics_per_core
                + metrics)
for trace_name in SINGLECORE_TRACES:
    output_path = f"{RAM_SRC}/../../Ram_results/singlecore/nodefense/"
    result_filename = output_path + "stats/" + trace_name + ".txt"

    values = get_values_from_file(result_filename, 
                                name_metrics, 
                                name_metrics_per_core, 
                                1)

    cycles = values["cycles_recorded_core_"]
    insts = values["insts_recorded_core_"]
    slowest_core_inst = min(insts)
    total_energy = values["total_energy"] * 100000000 / slowest_core_inst

    df.loc[len(df)] = [trace_name] \
        + cycles + insts \
        + [total_energy]

df.to_csv(csv_filename, index=False)



### Process default runs
csv_filename = CSV_DIR + "singlecore_default.csv"
if os.path.exists(csv_filename):
    os.remove(csv_filename)

metrics_per_core = ["core_0"] + ["inst_0"]
name_metrics_per_core =  ["cycles_recorded_core_", "insts_recorded_core_"]
metrics = ["total_energy", "pref_cycles", "total_cycles"]

df = pd.DataFrame(columns=["trace", "mitigation", "nRH"] 
                + metrics_per_core
                + metrics)
for trace_name in SINGLECORE_TRACES:
    for mitigation in MITIGATION_LIST:
        for tRH in NRH_VALUES:
            pref_type = "rfm" if (mitigation == "RFM" or mitigation == "PRAC") else "vrr"
            name_metrics = ["total_energy","total_"+pref_type+"_cycles_rank0", "total_"+pref_type+"_cycles_rank1", "memory_system_cycles"]
            output_path = f"{RAM_SRC}/../../Ram_results/singlecore/default/" + mitigation + "/" + str(tRH) + "/"
            result_filename = output_path + "/stats/" + trace_name + ".txt"
            
            values = get_values_from_file(result_filename,
                                        name_metrics,
                                        name_metrics_per_core,
                                        1)
            cycles = values["cycles_recorded_core_"]
            insts = values["insts_recorded_core_"]
            slowest_core_inst = min(insts)
            total_energy = values["total_energy"] * 100000000 / slowest_core_inst
            if mitigation in ["PARA", "Hydra", "Graphene"]:
                total_dram_cycles = values["memory_system_cycles"] * 2 * 16 * 100000000 / slowest_core_inst
                total_pref_cycles = (values["total_"+pref_type+"_cycles_rank0"] + values["total_"+pref_type+"_cycles_rank1"]) * 100000000 / slowest_core_inst
            else:
                total_dram_cycles = values["memory_system_cycles"] * 2 * 16 * 100000000 / slowest_core_inst
                total_pref_cycles = 8*(values["total_"+pref_type+"_cycles_rank0"] + values["total_"+pref_type+"_cycles_rank1"]) * 100000000 / slowest_core_inst
            
            df.loc[len(df)] = [trace_name, mitigation, tRH] \
                + cycles + insts \
                + [total_energy, total_pref_cycles, total_dram_cycles]

df.to_csv(csv_filename, index=False)


### Process mechanism runs
csv_filename = CSV_DIR + "singlecore_mechanism.csv"

if os.path.exists(csv_filename):
    os.remove(csv_filename)

metrics_per_core = ["core_0"] + ["inst_0"]
name_metrics_per_core =  ["cycles_recorded_core_", "insts_recorded_core_"]
metrics = ["total_energy", "pref_cycles", "total_cycles"]

df = pd.DataFrame(columns=["trace", "mitigation", "nRH", "mfr", "latency_factor"] 
                + metrics_per_core
                + metrics)

for mfr in MFR_DICT.keys():
    for latency_factor in MFR_DICT[mfr]:
        for trace_name in SINGLECORE_TRACES:
            for mitigation in MITIGATION_LIST:
                for tRH in NRH_VALUES:
                    pref_type = "rfm" if (mitigation == "RFM" or mitigation == "PRAC") else "vrr"
                    name_metrics = ["total_energy", 
                                    "total_"+pref_type+"_cycles_rank0", "total_"+pref_type+"_cycles_rank1", "total_r"+pref_type+"_cycles_rank0", 
                                    "total_r"+pref_type+"_cycles_rank1", "memory_system_cycles"]
                    output_path = f"{RAM_SRC}/../../Ram_results/singlecore/PaCRAM-{mfr[-1]}/" + mitigation + "/" + str(tRH) + "/" + str(latency_factor).replace(".", "_") + "/"
                    result_filename = output_path + "/stats/" + trace_name + ".txt"
                    
                    values = get_values_from_file(result_filename,
                                                name_metrics,
                                                name_metrics_per_core,
                                                1)
                
                    cycles = values["cycles_recorded_core_"]
                    insts = values["insts_recorded_core_"]
                    slowest_core_inst = min(insts)
                    total_energy = values["total_energy"] * 100000000 / slowest_core_inst
                    if mitigation in ["PARA", "Hydra", "Graphene"]:
                        total_dram_cycles = values["memory_system_cycles"] * 2 * 16 * 100000000 / slowest_core_inst
                        total_pref_cycles = (values["total_"+pref_type+"_cycles_rank0"] + values["total_r"+pref_type+"_cycles_rank0"] + values["total_"+pref_type+"_cycles_rank1"] + values["total_r"+pref_type+"_cycles_rank1"]) * 100000000 / slowest_core_inst
                    else:
                        total_dram_cycles = values["memory_system_cycles"] * 2 * 16 * 100000000 / slowest_core_inst
                        total_pref_cycles = 8*(values["total_"+pref_type+"_cycles_rank0"] + values["total_r"+pref_type+"_cycles_rank0"] + values["total_"+pref_type+"_cycles_rank1"] + values["total_r"+pref_type+"_cycles_rank1"]) * 100000000 / slowest_core_inst
                    
                    df.loc[len(df)] = [trace_name, mitigation, tRH, mfr, latency_factor] \
                        + cycles + insts \
                        + [total_energy, total_pref_cycles, total_dram_cycles]

df.to_csv(csv_filename, index=False)