import os, yaml, copy, time, sys
from utils_runs import *
from utils_slurm import *

is_slurm = (sys.argv[1] == "slurm")

base_config_file = RAM_SRC + "base_checkpoint_config.yaml"
    
base_config = None
with open(base_config_file, 'r') as stream:
    try:
        base_config = yaml.safe_load(stream)
    except yaml.YamlError as exc:
        print(exc)
if(base_config == None):
    print("Error: base config is None")
    exit(1)


### Singlecore checkpoints
for trace in SINGLECORE_TRACES:
    output_path = f"{RAM_SRC}/checkpoints/singlecore/"

    for path in [output_path + "/llcs", output_path + "/configs", output_path + "/logs"]:
        if not os.path.exists(path):
            os.makedirs(path)

    llc_filename = output_path + "llcs/" + trace + ".llc.txt"
    config_filename = output_path + "configs/" + trace + ".yaml"
    log_filename = output_path + "logs/" + trace + ".log"
    if get_run_status(log_filename) == "running" or get_run_status(log_filename) == "finished":
            continue
    config = copy.deepcopy(base_config)
    config_file = open(config_filename, "w")
    
    config['Frontend']['traces'] = [TRACE_PATH + trace]
    config['Frontend']['llc_serialization_filename'] = llc_filename
    config['Frontend']['llc_serialize'] = True

    if is_slurm:
        cmd = f"{SLURM_CMD} {RAM_SRC}/ramulator2 -c '{config}' > {log_filename} 2>&1 &"
    else:
        cmd = f"{RAM_SRC}/ramulator2 -c '{config}' > {log_filename} 2>&1"

    yaml.dump(config, config_file, default_flow_style=False)
    config_file.close()
    
    if is_slurm:
        while check_running_jobs() >= MAX_SLURM_JOBS:
            print(f"[INFO] Maximum Slurm Job limit ({MAX_SLURM_JOBS}) reached. Retrying in {SLURM_RETRY_DELAY} seconds")
            time.sleep(SLURM_RETRY_DELAY)
    print("Running: checkpoint for trace = " + trace)
    os.system(cmd)

    time.sleep(0.1)


### Multicore checkpoints
for trace_name, trace_mix in MULTICORE_TRACES.items():
    output_path = f"{RAM_SRC}/checkpoints/multicore/"
        
    for path in [output_path + "/llcs", output_path + "/configs", output_path + "/logs"]:
        if not os.path.exists(path):
            os.makedirs(path)

    llc_filename = output_path + "llcs/" + trace_name + ".llc.txt"
    config_filename = output_path + "configs/" + trace_name + ".yaml"
    log_filename = output_path + "logs/" + trace_name + ".log"
    if get_run_status(log_filename) == "running" or get_run_status(log_filename) == "finished":
            continue
    config = copy.deepcopy(base_config)
    config_file = open(config_filename, "w")
    
    config['Frontend']['traces'] = [TRACE_PATH + trace for trace in trace_mix]
    config['Frontend']['llc_serialization_filename'] = llc_filename
    config['Frontend']['llc_serialize'] = True

    if is_slurm:
        cmd = f"{SLURM_CMD} {RAM_SRC}/ramulator2 -c '{config}' > {log_filename} 2>&1 &"
    else:
        cmd = f"{RAM_SRC}/ramulator2 -c '{config}' > {log_filename} 2>&1"

    yaml.dump(config, config_file, default_flow_style=False)
    config_file.close()
    
    if is_slurm:
        while check_running_jobs() >= MAX_SLURM_JOBS:
            print(f"[INFO] Maximum Slurm Job limit ({MAX_SLURM_JOBS}) reached. Retrying in {SLURM_RETRY_DELAY} seconds")
            time.sleep(SLURM_RETRY_DELAY)
    print("Running: checkpoint for trace = " + trace_name)
    os.system(cmd)

    time.sleep(0.1)

print("[INFO] All checkpoint runs are started")