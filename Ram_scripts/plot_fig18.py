import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

PWD = os.getcwd()
CSV_DIR = f"{PWD}/../Ram_results/processed/"
PLOT_DIR = f"{PWD}/../Ram_plots/"
if not os.path.exists(PLOT_DIR):
    os.makedirs(PLOT_DIR)

fig_width = 4
fig_height = fig_width * 0.38
colors = sns.color_palette("tab10", 5)
attack = "False"
fig, axarr = plt.subplots(1, 2, figsize=(fig_width, fig_height))
for i, core in enumerate(["single", "multi"]):
    df = pd.read_csv(f"{CSV_DIR}{core}core_pacram_best.csv")
    if core == "single":
        df = df[~((df["config"] == "PaCRAM-S") & ((df["mitigation"] == "Graphene") | (df["mitigation"] == "Hydra")))]
        df.drop(columns=set(df.columns) - set(['trace', 'mitigation', 'nRH', 'n_total_energy_over_nodefense', 'config']), inplace=True)
        df.rename(columns={"n_total_energy_over_nodefense": "norm_energy"}, inplace=True)
    else:
        df = df[~((df["config"] == "PaCRAM-S") & ((df["mitigation"] == "Graphene") | (df["mitigation"] == "Hydra") | (df["mitigation"] == "PARA")))]
        df.drop(columns=set(df.columns) - set(['trace', 'mitigation', 'nRH', 'n_total_energy_over_nodefense', 'config']), inplace=True)
        df.rename(columns={"n_total_energy_over_nodefense": "norm_energy"}, inplace=True)

    df['mitigation'] = pd.Categorical(df['mitigation'], ["PARA", "RFM", "PRAC", "Hydra", "Graphene"])
    df.sort_values("mitigation", inplace=True)

    plot_df = df
    ax = axarr[i]
    sns.lineplot(data=plot_df, x="nRH", y="norm_energy", hue="mitigation", style="config", ax=ax, markers=False, palette=colors, linewidth=1, 
            hue_order=["PARA", "RFM", "PRAC", "Hydra", "Graphene"], alpha=1, err_style="band", errorbar=("ci", 100),
            style_order=["Default", "PaCRAM-H", "PaCRAM-S"])

    ax.invert_xaxis()
    ax.set_xscale('log', base=2)
    # ax.set_yscale('log', base=2)
    ax.set_xticks([1024, 512, 256, 128, 64, 32])
    xticklabels = []
    for x in [1024, 512, 256, 128, 64, 32]:
        xticklabels += [str(int(x/1024))+"K" if x >= 1024 else str(int(x))]
    ax.set_xticklabels(xticklabels, rotation=90, fontsize=8.5)

    ax.grid(which="major", axis="y", color="black", alpha=0.5, linestyle="dotted", linewidth=0.5, zorder=0)
    ax.grid(which="minor", axis="y", color="gray", alpha=0.2, linestyle="dotted", linewidth=0.5, zorder=0)
    ax.axhline(y=1, color="black", linestyle="dashed", linewidth=0.5, zorder=0)

    ax.legend().remove()
    ax.xaxis.set_tick_params(pad=0, length=2)
    ax.yaxis.set_tick_params(pad=0, length=2)

    ax.set_ylabel("")
    ax.set_xlabel("")
    ax.set_title("")

    ax.set_ylim(0.95, 5.05)
    ax.set_yticks([1, 2, 3, 4, 5])
    if i == 0:
        ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=8.5)
    else:
        ax.set_yticklabels(["", "", "", "", ""], fontsize=8.5)
    handles, labels = ax.get_legend_handles_labels()
    if i == 0:
        ax.set_ylabel("Energy consumption\n(normalized to no \nRowHammer mitigation)", fontsize=9, x=0, y=0.4, labelpad=2)

    test_type = "Single-core" if i == 0 else "Multi-core"
    ax.text(0.03, 0.97, test_type, horizontalalignment='left', verticalalignment='top', transform=ax.transAxes, 
            fontsize=8.5, bbox=dict(facecolor='white', alpha=0.5, boxstyle='round,pad=0.1'))

    handles, labels = ax.get_legend_handles_labels()
    labels[-3:] = ["No PaCRAM", "PaCRAM-H", "PaCRAM-S"]
    handles = handles[1:6] + handles[-3:]
    labels = labels[1:6] + labels[-3:]
    for a in range(8):
        handles[a].set_linewidth(1.5)

fig.legend(handles, labels, loc="center left", frameon=True, handlelength=1.5, fontsize=8.5, 
            bbox_to_anchor=(0.9, 0.5), labelspacing=0.2,
            borderaxespad=0.15, handletextpad=0.15, columnspacing=0.4, ncols=1)

plt.subplots_adjust(hspace=0.1, wspace=0.05)
fig.supxlabel('RowHammer threshold ($N_{RH}$)', fontsize=9, x=0.5, y=-0.18)
fig.savefig(PLOT_DIR + "fig18_energy.png", bbox_inches='tight', pad_inches=0.01)
fig.savefig(PLOT_DIR + "fig18_energy.pdf", bbox_inches='tight', pad_inches=0.01)
