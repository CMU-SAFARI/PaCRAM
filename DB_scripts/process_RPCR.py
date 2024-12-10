import os
import pandas as pd
from plot_utils import *
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

results_dir = os.getcwd() + "/../DB_results/"
csv_dir = os.getcwd() + "/../DB_results/processed_rpcr"

restoration_latency_ns_list = [
    "33",
    "27",
    "21",
    "15",
    "12",
    "9",
    "6",
]

num_restoration_list = [
    "1",
    "2",
    "3",
    "4",
    "5",
]

module_list = ["H" + str(i) for i in range(9)] + ["M" + str(i) for i in range(7)] + ["S" + str(i) for i in range(14)]

if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)

main_df = pd.DataFrame()
for module in module_list:
    if os.path.exists(csv_dir + "/" + module + "_RPCR.csv"):
        csv_file = csv_dir + "/" + module  + "_RPCR.csv"
        df = pd.read_csv(csv_file)
        main_df = pd.concat([main_df, df], ignore_index=True)
    else:
        df = pd.DataFrame()
        for num_res in num_restoration_list:
            for res_lat_ns in restoration_latency_ns_list:
                out_dir = results_dir + module + "/"
                csv_file = out_dir + "tras_" + res_lat_ns + "-" + num_res + ".csv"

                if not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0:
                    continue

                t_df = pd.read_csv(csv_file)
                t_df = t_df.groupby(['PivotRow']).min().reset_index()
                t_df.drop_duplicates(inplace=True)
                t_df['module'] = module
                t_df['res_lat_ns'] = res_lat_ns
                t_df['num_res'] = num_res
                df = pd.concat([df, t_df], ignore_index=True)

        if df.empty or df[(df['res_lat_ns'] == "33") & (df['num_res'] == "1")].empty:
            continue

        df['id'] = df['res_lat_ns'] + "-" + df['num_res']

        id_list = df['id'].unique()
        df_pivot = df.pivot(index=['PivotRow', 'module'], columns='id', values='nRH').reset_index()

        baseline_id = "33-1"
        for id in set(id_list) - set([baseline_id]):
            df_pivot[id] = df_pivot[id] / df_pivot[baseline_id]

        df_pivot[baseline_id] = df_pivot[baseline_id] / df_pivot[baseline_id]
        df_pivot.dropna(axis=0, how='any', subset=[baseline_id], inplace=True)

        df = df_pivot.melt(id_vars=['PivotRow', 'module'], var_name='id', value_name='nRH')
        df['res_lat_ns'] = df['id'].apply(lambda x: int(x.split('-')[0]))
        df['norm_tras'] = df['res_lat_ns'].apply(lambda x: get_pcr_factor(x))
        df['num_res'] = df['id'].apply(lambda x: int(x.split('-')[1]))
        df.rename(columns={'nRH': 'norm_nRH'}, inplace=True)
        df.drop(['id'], axis=1, inplace=True)
        df['mfr'] = df['module'].apply(lambda x: get_mfr(x))

        df.to_csv(csv_dir + "/" + module + "_RPCR.csv", index=False)
        main_df = pd.concat([main_df, df], ignore_index=True)

main_df.to_csv(csv_dir + "/processed_RPCR.csv", index=False)
