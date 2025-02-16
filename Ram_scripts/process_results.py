import os
import pandas as pd
from utils_runs import *
from utils_parser import *

PWD = os.getcwd()
CSV_DIR = f"{PWD}/../Ram_results/processed/"
if not os.path.exists(CSV_DIR):
    os.makedirs(CSV_DIR)


### process singlecore results
csv_filename = CSV_DIR + "singlecore_nodefense.csv"
sc_nd_df = pd.read_csv(csv_filename)

sc_nd_df["ipc"] = sc_nd_df['inst_0'] / sc_nd_df["core_0"]
sc_nd_df.drop(columns=["core_0"], inplace=True)

csv_filename = CSV_DIR + "singlecore_default.csv"
sc_de_df = pd.read_csv(csv_filename)

sc_de_df["ipc"] = sc_de_df['inst_0'] / sc_de_df["core_0"]
sc_de_df['config'] = sc_de_df['mitigation']
sc_de_df.drop(columns=["core_0"], inplace=True)

sc_de_df = sc_de_df.merge(sc_nd_df, on=["trace"], how="left", suffixes=("_default", "_nodefense"))

csv_filename = CSV_DIR + "singlecore_mechanism.csv"
sc_me_df = pd.read_csv(csv_filename)

sc_me_df["ipc"] = sc_me_df['inst_0'] / sc_me_df["core_0"]
sc_me_df['config'] = sc_me_df['mitigation'] + "_" + sc_me_df['mfr'] + "_" + sc_me_df['latency_factor'].astype(str)
sc_me_df.drop(columns=["core_0", "mfr", "latency_factor"], inplace=True)

sc_me_df = sc_me_df.merge(sc_de_df, on=["trace", "mitigation", "nRH"], how="left", suffixes=("", "_default"))
sc_me_df.drop(columns=["config_default"], inplace=True)

sc_de_df['ipc'] = sc_de_df['ipc_default']
sc_de_df['total_energy'] = sc_de_df['total_energy_default']
sc_de_df['pref_cycles_default'] = sc_de_df['pref_cycles']

sc_df = pd.concat([sc_me_df, sc_de_df], ignore_index=True)
sc_df.fillna(0, inplace=True)

sc_df['n_ipc_over_nodefense'] = sc_df['ipc'] / sc_df['ipc_nodefense']
sc_df['n_ipc_over_default'] = sc_df['ipc'] / sc_df['ipc_default']

sc_df['n_total_energy_over_nodefense'] = sc_df['total_energy'] / sc_df['total_energy_nodefense']
sc_df['n_total_energy_over_default'] = sc_df['total_energy'] / sc_df['total_energy_default']
sc_df['n_pref_cycles_over_default'] = sc_df['pref_cycles'] / sc_df['pref_cycles_default']

sc_df.fillna(1, inplace=True)

csv_filename = CSV_DIR + "singlecore_pacram.csv"
if os.path.exists(csv_filename):
    os.remove(csv_filename)
sc_df.to_csv(csv_filename, index=False)

sc_df.loc[sc_df.config.str.contains("Mfr. S_0.45"), "config"] = "PaCRAM-S"
sc_df = sc_df[~(sc_df.config.str.contains("Mfr. S"))]
sc_df.loc[sc_df.config.str.contains("Mfr. H_0.36"), "config"] = "PaCRAM-H"
sc_df = sc_df[~(sc_df.config.str.contains("Mfr. H"))]
sc_df.loc[sc_df.config.str.contains("Mfr. M_0.18"), "config"] = "PaCRAM-M"
sc_df = sc_df[~(sc_df.config.str.contains("Mfr. M"))]
sc_df.loc[((sc_df.config != "PaCRAM-H") & (sc_df.config != "PaCRAM-S") & (sc_df.config != "PaCRAM-M")), "config"] = "Default"

t_df = sc_df[(sc_df.config == "PaCRAM-S") & ((sc_df.mitigation == "Hydra") | (sc_df.mitigation == "Graphene"))]
sc_df = sc_df[~((sc_df.config == "PaCRAM-S") & ((sc_df.mitigation == "Hydra") | (sc_df.mitigation == "Graphene")))]
t_df["n_ipc_over_nodefense"] = t_df["ipc_default"] / t_df["ipc_nodefense"]

sc_df = pd.concat([sc_df, t_df], ignore_index=True)
csv_filename = CSV_DIR + "singlecore_pacram_best.csv"
if os.path.exists(csv_filename):
    os.remove(csv_filename)
sc_df.to_csv(csv_filename, index=False)


### process multicore results
csv_filename = CSV_DIR + "singlecore_nodefense.csv"
sc_df = pd.read_csv(csv_filename)
sc_df.drop(columns=list(set(sc_df.columns) - set(["trace", "core_0", "inst_0"])), inplace=True)

sc_df["alone_ipc"] = sc_df['inst_0'] / sc_df["core_0"]
sc_df["workload"] = sc_df["trace"]
sc_df = sc_df[["workload", "alone_ipc"]]

csv_filename = CSV_DIR + "multicore_nodefense.csv"
mc_nd_df = pd.read_csv(csv_filename)

mc_nd_df = calc_mc_metrics(mc_nd_df, sc_df, MULTICORE_TRACES)

csv_filename = CSV_DIR + "multicore_default.csv"
mc_de_df = pd.read_csv(csv_filename)

mc_de_df['config'] = mc_de_df['mitigation']
mc_de_df = calc_mc_metrics(mc_de_df, sc_df, MULTICORE_TRACES)

mc_de_df = mc_de_df.merge(mc_nd_df, on=["trace"], how="left", suffixes=("_default", "_nodefense"))

csv_filename = CSV_DIR + "multicore_mechanism.csv"
mc_me_df = pd.read_csv(csv_filename)

mc_me_df['config'] = mc_me_df['mitigation'] + "_" + mc_me_df['mfr'] + "_" + mc_me_df['latency_factor'].astype(str)
mc_me_df.drop(columns=["mfr", "latency_factor"], inplace=True)
mc_me_df = calc_mc_metrics(mc_me_df, sc_df, MULTICORE_TRACES)

mc_me_df = mc_me_df.merge(mc_de_df, on=["trace", "mitigation", "nRH"], how="left", suffixes=("", "_default"))
mc_me_df.drop(columns=["config_default"], inplace=True)

mc_de_df['weighted_speedup'] = mc_de_df['weighted_speedup_default']
mc_de_df['total_energy'] = mc_de_df['total_energy_default']
mc_de_df['pref_cycles_default'] = mc_de_df['pref_cycles']

mc_df = pd.concat([mc_me_df, mc_de_df], ignore_index=True)
mc_df.fillna(0, inplace=True)

mc_df['n_weighted_speedup_over_nodefense'] = mc_df['weighted_speedup'] / mc_df['weighted_speedup_nodefense']
mc_df['n_weighted_speedup_over_default'] = mc_df['weighted_speedup'] / mc_df['weighted_speedup_default']

mc_df['n_total_energy_over_nodefense'] = mc_df['total_energy'] / mc_df['total_energy_nodefense']
mc_df['n_total_energy_over_default'] = mc_df['total_energy'] / mc_df['total_energy_default']
mc_df['n_pref_cycles_over_default'] = mc_df['pref_cycles'] / mc_df['pref_cycles_default']

mc_df.fillna(1, inplace=True)

csv_filename = CSV_DIR + "multicore_pacram.csv"
mc_df.to_csv(csv_filename, index=False)

mc_df.loc[mc_df.config.str.contains("Mfr. S_0.45"), "config"] = "PaCRAM-S"
mc_df = mc_df[~(mc_df.config.str.contains("Mfr. S"))]
mc_df.loc[mc_df.config.str.contains("Mfr. H_0.36"), "config"] = "PaCRAM-H"
mc_df = mc_df[~(mc_df.config.str.contains("Mfr. H"))]
mc_df.loc[mc_df.config.str.contains("Mfr. M_0.18"), "config"] = "PaCRAM-M"
mc_df = mc_df[~(mc_df.config.str.contains("Mfr. M"))]
mc_df.loc[((mc_df.config != "PaCRAM-H") & (mc_df.config != "PaCRAM-S") & (mc_df.config != "PaCRAM-M")), "config"] = "Default"

t_df = mc_df[(mc_df.config == "PaCRAM-S") & ((mc_df.mitigation == "Hydra") | (mc_df.mitigation == "Graphene") | (mc_df.mitigation == "PARA"))]
mc_df = mc_df[~((mc_df.config == "PaCRAM-S") & ((mc_df.mitigation == "Hydra") | (mc_df.mitigation == "Graphene") | (mc_df.mitigation == "PARA")))]
t_df["n_weighted_speedup_over_nodefense"] = t_df["weighted_speedup_default"] / t_df["weighted_speedup_nodefense"]

mc_df = pd.concat([mc_df, t_df], ignore_index=True)
csv_filename = CSV_DIR + "multicore_pacram_best.csv"
if os.path.exists(csv_filename):
    os.remove(csv_filename)
mc_df.to_csv(csv_filename, index=False)
