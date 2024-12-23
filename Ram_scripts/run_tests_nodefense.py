import os, yaml, copy, time, sys
from utils_runs import *
from utils_slurm import *

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
for trace in SINGLECORE_TRACES:
    output_path = f"{RAM_SRC}/../../Ram_results/singlecore/nodefense/"
    checkpoint_filename = f"{RAM_SRC}/checkpoints/singlecore/llcs/" + trace + ".llc.txt"
        
    for path in [output_path + "/stats", output_path + "/configs", output_path + "/cmd_count"]:
        if not os.path.exists(path):
            os.makedirs(path)

    result_filename = output_path + "/stats/" + trace + ".txt"
    if get_run_status(result_filename) == "running" or get_run_status(result_filename) == "finished":
        continue
    config_filename = output_path + "/configs/" + trace + ".yaml"
    cmd_count_filename = output_path + "/cmd_count/" + trace + ".cmd.count"
    config = copy.deepcopy(base_config)
    result_file = open(result_filename, "w")
    config_file = open(config_filename, "w")
    
    config['Frontend']['traces'] = [TRACE_PATH + trace]
    config['Frontend']['llc_deserialize'] = True
    config['Frontend']['llc_deserialization_filename'] = checkpoint_filename

    config['MemorySystem']['BHDRAMController']['plugins'][0]['ControllerPlugin']['path'] = cmd_count_filename

    if is_slurm:
        cmd = f"{SLURM_CMD} {RAM_SRC}/ramulator2 -c '{config}' > {result_filename} 2>&1 &"
    else:
        cmd = f"{RAM_SRC}/ramulator2 -c '{config}' > {result_filename} 2>&1"  

    yaml.dump(config, config_file, default_flow_style=False)
    config_file.close()
    result_file.write(cmd + "\n")
    result_file.close()
    
    if is_slurm:
        while check_running_jobs() >= MAX_SLURM_JOBS:
            print(f"[INFO] Maximum Slurm Job limit ({MAX_SLURM_JOBS}) reached. Retrying in {SLURM_RETRY_DELAY} seconds")
            time.sleep(SLURM_RETRY_DELAY)
    print("Running: trace = " + trace + ", mitigation = nodefense")
    os.system(cmd)

    time.sleep(0.1)


### Multicore runs
for trace_name, trace_mix in MULTICORE_TRACES.items():
    output_path = f"{RAM_SRC}/../../Ram_results/multicore/nodefense/"
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
    result_file = open(result_filename, "w")
    config_file = open(config_filename, "w")
    
    config['Frontend']['traces'] = [TRACE_PATH + trace for trace in trace_mix]
    config['Frontend']['llc_deserialize'] = True
    config['Frontend']['llc_deserialization_filename'] = checkpoint_filename

    config['MemorySystem']['BHDRAMController']['plugins'][0]['ControllerPlugin']['path'] = cmd_count_filename

    if is_slurm:
        cmd = f"{SLURM_CMD} {RAM_SRC}/ramulator2 -c '{config}' > {result_filename} 2>&1 &"
    else:
        cmd = f"{RAM_SRC}/ramulator2 -c '{config}' > {result_filename} 2>&1"  

    yaml.dump(config, config_file, default_flow_style=False)
    config_file.close()
    result_file.write(cmd + "\n")
    result_file.close()
    
    if is_slurm:
        while check_running_jobs() >= MAX_SLURM_JOBS:
            print(f"[INFO] Maximum Slurm Job limit ({MAX_SLURM_JOBS}) reached. Retrying in {SLURM_RETRY_DELAY} seconds")
            time.sleep(SLURM_RETRY_DELAY)
    print("Running: trace = " + trace_name + ", mitigation = nodefense")
    os.system(cmd)

    time.sleep(0.1)

print("[INFO] All no defense runs are started.")