import os
import pandas as pd
from pandas.core.common import SettingWithCopyWarning
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)

PWD = os.getcwd()
CSV_DIR = f"{PWD}/../Ram_results/processed/"
PLOT_DIR = f"{PWD}/../Ram_plots/"
if not os.path.exists(PLOT_DIR):
    os.makedirs(PLOT_DIR)

num_mechs = 5
num_mixtypes= 2
fig, axarr = plt.subplots(num_mixtypes, num_mechs, figsize=(8, 2.1))
colors = sns.color_palette("plasma", 3)

for i, core in enumerate(["single", "multi"]):
    df = pd.read_csv(f"{CSV_DIR}{core}core_pacram_best.csv")
    df.drop(columns=set(df.columns) - set(['trace', 'mitigation', 'nRH', 'config', 'pref_cycles']), inplace=True)

    base_df = df[~((df.config.str.contains("Mfr. S") | df.config.str.contains("Mfr. H")))]
    base_df = base_df[base_df['nRH'] == 1024]
    df = pd.merge(df, base_df, on=["trace", "mitigation"], how="left", suffixes=("", "_base"))
    df.drop(columns=['config_base', 'nRH_base'], inplace=True)
    if core == "single":
        df[((df.config == "PaCRAM-S") & ((df.mitigation == "Hydra") | (df.mitigation == "Graphene")))]["pref_cycles"] = df[((df.config == "PaCRAM-S") & ((df.mitigation == "Hydra") | (df.mitigation == "Graphene")))]["pref_cycles_base"]
    else:
        df[((df.config == "PaCRAM-S") & ((df.mitigation == "Hydra") | (df.mitigation == "PARA") | (df.mitigation == "Graphene")))]["pref_cycles"] = df[((df.config == "PaCRAM-S") & ((df.mitigation == "Hydra") | (df.mitigation == "Graphene") | (df.mitigation == "PARA")))]["pref_cycles_base"]
    df['norm_pref'] = df['pref_cycles'] / df['pref_cycles_base']
    df = df[~df['norm_pref'].isna()]
    df = df[~df['norm_pref'].isin([np.inf, -np.inf])]

    df['mitigation'] = pd.Categorical(df['mitigation'], ["PARA", "RFM", "PRAC", "Hydra", "Graphene"])
    df.sort_values("mitigation", inplace=True)

    for mech_id, (mech, mech_df) in enumerate(df.groupby("mitigation")):
        plot_df = mech_df
        vrr_id = 0
        ax = axarr[i][mech_id]
        sns.boxplot(data=plot_df, x="nRH", y="norm_pref", hue='config', ax=ax, palette=colors, 
                    whis=[0, 90], showfliers=False, 
                    hue_order=["PaCRAM-S", "PaCRAM-H", "Default"], linewidth=0.5)

        ax.invert_xaxis()

        ax.set_yscale('log', base=10)

        ax.grid(which="major", axis="y", color="black", alpha=0.5, linestyle="dotted", linewidth=0.5, zorder=0)
        ax.grid(which="minor", axis="y", color="gray", alpha=0.2, linestyle="dotted", linewidth=0.5, zorder=0)
        ax.axhline(y=1, color="black", linestyle="dashed", linewidth=1, zorder=0)

        handles, labels = ax.get_legend_handles_labels()
        handles = handles[::-1]
        labels = labels[::-1]
        ax.legend(handles, labels, loc="upper left", ncols=1, fancybox=True, fontsize=5.8,
                    borderpad=0.2, labelspacing=0.2,  
                    columnspacing=0.5, handletextpad=0.3, handlelength=1,  bbox_transform=ax.transAxes)

        ax.set_ylabel("")
        ax.set_xlabel("")
        ax.set_title("")

        if i == 1:
            ax.set_xticklabels(["32", "64", "128", "256", "512", "1K"], rotation=90, fontsize=6.5)
        else:
            ax.set_xticklabels([])

        if i == 0:
            ax.set_title(mech, fontsize=7.5, pad=2)
        if mech_id == 0 or mech_id == 1:
            ax.set_ylim(0, 200)
            ax.set_yticks([1, 10, 100])
            ax.set_yticklabels(["1", "10", "100"], fontsize=6.5)
        else:
            ax.set_ylim(0, 80000)
            ax.set_yticks([1, 10, 100, 1000, 10000])
            ax.set_yticklabels(["1", "10", "100", "1K", "10K"], fontsize=6.5)
        ax.xaxis.set_tick_params(pad=0, length=2)
        ax.yaxis.set_tick_params(pad=0, length=2)
plt.subplots_adjust(hspace=0.04, wspace=0.24)
fig.supylabel('Time Spent on Preventive Refreshes\n(Norm. to RH Defenses at $N_{RH}=1K$)\n(Top: Singlecore, Bottom: Multicore)', 
                fontsize=6.5, va='center', ha='center', x=0.08, y=0.47)
fig.supxlabel('RowHammer Threshold ($N_{RH}$)', fontsize=7.5, x=0.5, y=-0.07)
fig.savefig(PLOT_DIR + "fig17_pref_time.png", bbox_inches='tight')
fig.savefig(PLOT_DIR + "fig17_pref_time.pdf", bbox_inches='tight')
