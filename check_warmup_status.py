import os
os.chdir("Ram_scripts")

from Ram_scripts.utils_runs import *

num_exp = len(SINGLECORE_TRACES) + len(MULTICORE_TRACES)
num_finished = 0
num_running = 0
num_failed = 0
for trace in SINGLECORE_TRACES:
    output_path = f"{RAM_SRC}/checkpoints/singlecore/"
    log_filename = output_path + "logs/" + trace + ".log"
    if get_run_status(log_filename) == "finished":
        num_finished += 1
    elif get_run_status(log_filename) == "running":
        num_running += 1
    elif get_run_status(log_filename) == "error":
        num_failed += 1

for trace_name, trace_mix in MULTICORE_TRACES.items():
    output_path = f"{RAM_SRC}/checkpoints/multicore/"
    log_filename = output_path + "logs/" + trace_name + ".log"
    if get_run_status(log_filename) == "finished":
        num_finished += 1
    elif get_run_status(log_filename) == "running":
        num_running += 1
    elif get_run_status(log_filename) == "error":
        num_failed += 1

not_found = num_exp - num_finished - num_failed - num_running
if num_exp == num_finished:
    print("[INFO] All warmup runs are finished.")
elif num_failed > 0:
    print("[INFO] There are failed runs. Please rerun './prepare_warmups.sh'")
else:
    print(f"[INFO] {num_running} runs are running. {not_found} runs are not found.")
