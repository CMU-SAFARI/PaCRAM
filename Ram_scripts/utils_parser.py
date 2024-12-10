def get_value(metric, line):
    if metric in line:
        return float(line.split(":")[1].strip())
    return 0

def get_values_from_file(filename, metrics, metrics_per_core, num_cores):
    result_file = open(filename, "r")
    lines = result_file.readlines()
    result_file.close()

    values = {}
    for metric in metrics_per_core:
        values[metric] = [0] * num_cores

    for line in lines:
        found = False
        for metric in metrics:
            if metric == line.split(":")[0].strip():
                values[metric] = get_value(metric, line)
                found = True
        for metric in metrics_per_core:
            if metric in line and "memory" not in line:
                core_id = int(line.split(":")[0].split("_")[-1])
                if core_id >= num_cores:
                    continue
                values[metric][core_id] = get_value(metric, line)
    for metric in metrics:
        if metric not in values:
            values[metric] = 0
    for metric in metrics_per_core:
        if metric not in values:
            values[metric] = [0] * num_cores
    return values

def merge_alone_IPCs(row, sc_df, mc_traces):
    if row["trace"] in mc_traces:
        workload_mix = mc_traces[row["trace"]]
        for core, workload in enumerate(workload_mix):
            row["aipc_"+str(int(core))] = sc_df[sc_df.workload == workload]["alone_ipc"].values[0]
        return row

def calc_mc_metrics(mc_df, sc_df, mc_traces):
    mc_df = mc_df.apply(lambda row : merge_alone_IPCs(row, sc_df, mc_traces), axis=1)

    for col in [c for c in mc_df.columns if "core_" in c]:
        co = col.split("_")[1]
        mc_df["sipc_"+str(int(co))] = mc_df['inst_'+str(int(co))] / mc_df[col]
        mc_df["soa_"+str(int(co))] = mc_df["sipc_"+str(int(co))] / mc_df["aipc_"+str(int(co))]
        mc_df["aos_"+str(int(co))] = mc_df["aipc_"+str(int(co))] / mc_df["sipc_"+str(int(co))]

    mc_df["weighted_speedup"] = 0
    for c in range(4):
        mc_df["weighted_speedup"] += mc_df["soa_"+str(c)]
    
    mc_df.drop([c for c in mc_df.columns if "aipc_" in c], axis=1, inplace=True)
    mc_df.drop([c for c in mc_df.columns if "sipc_" in c], axis=1, inplace=True)
    mc_df.drop([c for c in mc_df.columns if "soa_" in c], axis=1, inplace=True)
    mc_df.drop([c for c in mc_df.columns if "aos_" in c], axis=1, inplace=True)
    mc_df.drop([c for c in mc_df.columns if "core_" in c], axis=1, inplace=True)
    return mc_df
