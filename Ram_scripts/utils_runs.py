import os

RAM_SRC = os.getcwd() + "/ramulator_pacram/"

MITIGATION_LIST = ["PARA", "Graphene", "Hydra", "RFM", "PRAC"]

NRH_VALUES = [1024, 512, 256, 128, 64, 32]

MFR_DICT = {"Mfr. H" : [0.81, 0.64, 0.45, 0.36, 0.27], "Mfr. S" : [0.81, 0.64, 0.45, 0.36], "Mfr. M" : [0.81, 0.64, 0.45, 0.36, 0.27, 0.18]}

TRACE_PATH = f"{RAM_SRC}/cputraces/"
trace_combination_filename = RAM_SRC + "/../mixes_singlecore.txt"

SINGLECORE_TRACES = []
with open(trace_combination_filename, "r") as trace_combination_file:
    for line in trace_combination_file:
        line = line.strip()
        if(line == ""):
            continue
        SINGLECORE_TRACES.append(line)
SINGLECORE_TRACES = list(set(SINGLECORE_TRACES))

trace_combination_filename = RAM_SRC + "/../mixes_multicore.txt"

MULTICORE_TRACES = {}
with open(trace_combination_filename, "r") as trace_combination_file:
    for line in trace_combination_file:
        line = line.strip()
        if(line == ""):
            continue
        trace_name = line.split(",")[0]
        trace_list = line.split(",")[1:]
        MULTICORE_TRACES[trace_name] = trace_list

def get_run_status(result_filename):
    if not os.path.exists(result_filename) or os.path.getsize(result_filename) == 0:
        return "not started"
    file = open(result_filename, "r")
    lines = file.readlines()
    file.close()
    for line in lines:
        if ("error" in line.lower() and not "established stream" in line.lower() and not "received spurious message" in line.lower()) or ("forcing job termination" in line.lower()):
            return "error"
        if "controller_num_row_hits" in line:
            return "finished"
        if "revoked" in line.lower():
            return "error"
    return "running"
    