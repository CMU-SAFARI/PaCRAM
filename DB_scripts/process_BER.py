import os
import pandas as pd
from plot_utils import *
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

results_dir = os.getcwd() + "/../DB_results/"
csv_dir = os.getcwd() + "/../DB_results/processed_ber/"

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
    if os.path.exists(csv_dir + "/" + module + "_BER.csv"):
        csv_file = csv_dir + "/" + module  + "_BER.csv"
        df_ber = pd.read_csv(csv_file)
        main_df = pd.concat([main_df, df_ber], ignore_index=True)
    else:
        df_ber = pd.DataFrame()
        for res_lat_ns in restoration_latency_ns_list:
            out_dir = results_dir + module + "/"
            ber_file = out_dir + "tras_" + res_lat_ns + "-1" + ".ber"

            if not os.path.exists(ber_file) or os.path.getsize(ber_file) == 0:
                continue

            t_df = pd.read_csv(ber_file)
            t_df.drop_duplicates(inplace=True)
            t_df['bfs'] = t_df.groupby(['PivotRow'])['BitLoc'].transform('count')
            t_df.drop(['BitLoc'], axis=1, inplace=True)
            t_df.drop_duplicates(inplace=True)
            t_df['module'] = module
            t_df['res_lat_ns'] = res_lat_ns
            df_ber = pd.concat([df_ber, t_df], axis=0)

        if df_ber.empty or not "33" in df_ber['res_lat_ns'].unique():
            continue

        id_list = df_ber['res_lat_ns'].unique()
        df_pivot = df_ber.pivot(index=['PivotRow', 'module'], columns='res_lat_ns', values='bfs').reset_index()

        baseline_id = "33"
        for id in set(id_list) - set([baseline_id]):
            df_pivot[id] = df_pivot[id] / df_pivot[baseline_id]

        df_pivot[baseline_id] = df_pivot[baseline_id] / df_pivot[baseline_id]
        df_pivot.dropna(axis=0, how='any', subset=[baseline_id], inplace=True)

        df_ber = df_pivot.melt(id_vars=['PivotRow', 'module'], var_name='res_lat_ns', value_name='bfs')
        df_ber['res_lat_ns'] = df_ber['res_lat_ns'].apply(lambda x: int(x))
        df_ber['norm_tras'] = df_ber['res_lat_ns'].apply(lambda x: get_pcr_factor(x))
        df_ber.rename(columns={'bfs': 'norm_bfs'}, inplace=True)
        df_ber['mfr'] = df_ber['module'].apply(lambda x: get_mfr(x))

        df_ber.to_csv(csv_dir + "/" + module + "_BER.csv", index=False)
        main_df = pd.concat([main_df, df_ber], ignore_index=True)

main_df.to_csv(csv_dir + "/processed_BER.csv", index=False)
