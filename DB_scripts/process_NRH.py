import os
import pandas as pd
from plot_utils import *
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

results_dir = os.getcwd() + "/../DB_results/"
csv_dir = os.getcwd() + "/../DB_results/processed_nrh"

restoration_latency_ns_list = [
    "33",
    "27",
    "21",
    "15",
    "12",
    "9",
    "6",
]

module_list = ["H" + str(i) for i in range(9)] + ["M" + str(i) for i in range(7)] + ["S" + str(i) for i in range(14)]

if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)

main_df = pd.DataFrame()
for module in module_list:
    if os.path.exists(csv_dir + "/" + module + "_NRH.csv"):
        csv_file = csv_dir + "/" + module  + "_NRH.csv"
        df = pd.read_csv(csv_file)
        main_df = pd.concat([main_df, df], ignore_index=True)
    else:
        df = pd.DataFrame()
        for res_lat_ns in restoration_latency_ns_list:
            out_dir = results_dir + module + "/"
            csv_file = out_dir + "tras_" + res_lat_ns + "-1" + ".csv"

            if not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0:
                continue

            t_df = pd.read_csv(csv_file)
            t_df = t_df.groupby(['PivotRow']).min().reset_index()
            t_df.drop_duplicates(inplace=True)
            t_df['module'] = module
            t_df['res_lat_ns'] = res_lat_ns
            df = pd.concat([df, t_df], ignore_index=True)

        if df.empty or not "33" in df['res_lat_ns'].unique():
            continue

        id_list = df['res_lat_ns'].unique()
        df_pivot = df.pivot(index=['PivotRow', 'module'], columns='res_lat_ns', values='nRH').reset_index()
        baseline_id = "33"

        for id in set(id_list) - set([baseline_id]):
            df_pivot[id] = df_pivot[id] / df_pivot[baseline_id]

        df_pivot["base_nRH"] = df_pivot[baseline_id]
        df_pivot[baseline_id] = df_pivot[baseline_id] / df_pivot[baseline_id]
        df_pivot.dropna(axis=0, how='any', subset=[baseline_id], inplace=True)

        df = df_pivot.melt(id_vars=['PivotRow', 'module', 'base_nRH'], var_name='res_lat_ns', value_name='nRH')
        df['res_lat_ns'] = df['res_lat_ns'].apply(lambda x: int(x))
        df['norm_tras'] = df['res_lat_ns'].apply(lambda x: get_pcr_factor(x))
        df.rename(columns={'nRH': 'norm_nRH'}, inplace=True)    
        df['mfr'] = df['module'].apply(lambda x: get_mfr(x))

        df.to_csv(csv_dir + "/" + module + "_NRH.csv", index=False)
        main_df = pd.concat([main_df, df], ignore_index=True)

main_df.to_csv(csv_dir + "/processed_NRH.csv", index=False)
