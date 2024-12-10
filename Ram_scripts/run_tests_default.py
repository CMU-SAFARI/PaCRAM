import os, yaml, copy, time, sys
from utils_runs import *
from calc_rh_parameters import *

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

### Singlecore runs
for trace_name in SINGLECORE_TRACES:
    for mitigation in MITIGATION_LIST: 
        for tRH in NRH_VALUES:
            output_path = f"{RAM_SRC}/../../Ram_results/singlecore/default/" + mitigation + "/" + str(tRH) + "/"
            checkpoint_filename = f"{RAM_SRC}/checkpoints/singlecore/llcs/" + trace_name + ".llc.txt"

            for path in [output_path + "/stats", output_path + "/configs", output_path + "/cmd_count"]:
                if not os.path.exists(path):
                    os.makedirs(path)

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
            
            if(mitigation == "PARA"):
                threshold = get_para_parameters(tRH)
                config['MemorySystem']['BHDRAMController']['plugins'].append({'ControllerPlugin' : {'impl': 'PARA', 'threshold': threshold}})
            elif(mitigation == "Graphene"):
                num_table_entries, activation_threshold, reset_period_ns = get_graphene_parameters(tRH, 32)
                config['MemorySystem']['BHDRAMController']['plugins'].append({'ControllerPlugin' : {'impl': 'Graphene', 'num_table_entries': num_table_entries, 'activation_threshold': activation_threshold, 'reset_period_ns': reset_period_ns}})
            elif(mitigation == "Hydra"):
                hydra_tracking_threshold, hydra_group_threshold, hydra_row_group_size, hydra_reset_period_ns, hydra_rcc_num_per_rank, hydra_rcc_policy = get_hydra_parameters(tRH, 32)
                config['MemorySystem']['BHDRAMController']['plugins'].append({'ControllerPlugin' : {'impl': 'Hydra', 'hydra_tracking_threshold': hydra_tracking_threshold, 'hydra_group_threshold': hydra_group_threshold, 'hydra_row_group_size': hydra_row_group_size, 'hydra_reset_period_ns': hydra_reset_period_ns, 'hydra_rcc_num_per_rank': hydra_rcc_num_per_rank, 'hydra_rcc_policy': hydra_rcc_policy}})
            elif(mitigation == "RFM"):
                rfm_threshold = get_rfm_parameters(tRH)
                config['MemorySystem']['BHDRAMController']['plugins'].append({'ControllerPlugin' : {'impl': 'RFMManager', 'rfm_threshold': rfm_threshold}})
            elif(mitigation == "PRAC"):
                abo_threshold = get_prac_parameters(tRH, ABO_refs=4)
                config["MemorySystem"]["DRAM"]["PRAC"] = True
                config["MemorySystem"]["BHDRAMController"]["impl"] = "PRACDRAMController"
                config["MemorySystem"]["BHDRAMController"]["BHScheduler"]["impl"] = "PRACScheduler"
                config["MemorySystem"]["BHDRAMController"]["plugins"].append({"ControllerPlugin" : {"impl": "PRAC", "abo_threshold": abo_threshold, "abo_delay_acts": 4, "abo_recovery_refs": 4}})

            if is_slurm:
                cmd = f"srun {RAM_SRC}/ramulator2 -c '{config}' > {result_filename} 2>&1 &"
            else:
                cmd = f"{RAM_SRC}/ramulator2 -c '{config}' > {result_filename} 2>&1"

            yaml.dump(config, config_file, default_flow_style=False)
            config_file.close()
            print("Running: trace = " + trace_name + ", mitigation = " + mitigation + ", tRH = " + str(tRH))
            os.system(cmd)

            time.sleep(0.03)

### Multicore runs
for trace_name, trace_mix in MULTICORE_TRACES.items():
    for mitigation in MITIGATION_LIST: 
        for tRH in NRH_VALUES:
            output_path = f"{RAM_SRC}/../../Ram_results/multicore/default/" + mitigation + "/" + str(tRH) + "/"
            checkpoint_filename = f"{RAM_SRC}/checkpoints/multicore/llcs/" + trace_name + ".llc.txt"

            for path in [output_path + "/stats", output_path + "/configs", output_path + "/cmd_count"]:
                if not os.path.exists(path):
                    os.makedirs(path)

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
            
            if(mitigation == "PARA"):
                threshold = get_para_parameters(tRH)
                config['MemorySystem']['BHDRAMController']['plugins'].append({'ControllerPlugin' : {'impl': 'PARA', 'threshold': threshold}})
            elif(mitigation == "Graphene"):
                num_table_entries, activation_threshold, reset_period_ns = get_graphene_parameters(tRH, 32)
                config['MemorySystem']['BHDRAMController']['plugins'].append({'ControllerPlugin' : {'impl': 'Graphene', 'num_table_entries': num_table_entries, 'activation_threshold': activation_threshold, 'reset_period_ns': reset_period_ns}})
            elif(mitigation == "Hydra"):
                hydra_tracking_threshold, hydra_group_threshold, hydra_row_group_size, hydra_reset_period_ns, hydra_rcc_num_per_rank, hydra_rcc_policy = get_hydra_parameters(tRH, 32)
                config['MemorySystem']['BHDRAMController']['plugins'].append({'ControllerPlugin' : {'impl': 'Hydra', 'hydra_tracking_threshold': hydra_tracking_threshold, 'hydra_group_threshold': hydra_group_threshold, 'hydra_row_group_size': hydra_row_group_size, 'hydra_reset_period_ns': hydra_reset_period_ns, 'hydra_rcc_num_per_rank': hydra_rcc_num_per_rank, 'hydra_rcc_policy': hydra_rcc_policy}})
            elif(mitigation == "RFM"):
                rfm_threshold = get_rfm_parameters(tRH)
                config['MemorySystem']['BHDRAMController']['plugins'].append({'ControllerPlugin' : {'impl': 'RFMManager', 'rfm_threshold': rfm_threshold}})
            elif(mitigation == "PRAC"):
                abo_threshold = get_prac_parameters(tRH, ABO_refs=4)
                config["MemorySystem"]["DRAM"]["PRAC"] = True
                config["MemorySystem"]["BHDRAMController"]["impl"] = "PRACDRAMController"
                config["MemorySystem"]["BHDRAMController"]["BHScheduler"]["impl"] = "PRACScheduler"
                config["MemorySystem"]["BHDRAMController"]["plugins"].append({"ControllerPlugin" : {"impl": "PRAC", "abo_threshold": abo_threshold, "abo_delay_acts": 4, "abo_recovery_refs": 4}})
            
            if is_slurm:
                cmd = f"srun {RAM_SRC}/ramulator2 -c '{config}' > {result_filename} 2>&1 &"
            else:
                cmd = f"{RAM_SRC}/ramulator2 -c '{config}' > {result_filename} 2>&1"

            yaml.dump(config, config_file, default_flow_style=False)
            config_file.close()
            print("Running: trace = " + trace_name + ", mitigation = " + mitigation + ", tRH = " + str(tRH))
            os.system(cmd)

            time.sleep(0.03)

print("[INFO] All default mitigation runs are started.")
