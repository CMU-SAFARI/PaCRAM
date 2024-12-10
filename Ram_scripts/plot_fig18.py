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
fig_height = fig_width * 0.35
colors = sns.color_palette("plasma", 5)
attack = "False"
fig, axarr = plt.subplots(1, 2, figsize=(fig_width, fig_height))
for i, core in enumerate(["single", "multi"]):
    df = pd.read_csv(f"{CSV_DIR}{core}core_pacram_best.csv")
    if core == "single":
        df.drop(columns=set(df.columns) - set(['trace', 'mitigation', 'nRH', 'n_total_energy_over_default', 'config']), inplace=True)
        df.rename(columns={"n_total_energy_over_default": "norm_energy"}, inplace=True)
        df.loc[((df.config == "PaCRAM-S") & ((df.mitigation == "Hydra") | (df.mitigation == "Graphene"))), "norm_energy"] = 1
    else:
        df.drop(columns=set(df.columns) - set(['trace', 'mitigation', 'nRH', 'n_total_energy_over_default', 'config']), inplace=True)
        df.rename(columns={"n_total_energy_over_default": "norm_energy"}, inplace=True)
        df.loc[((df.config == "PaCRAM-S") & ((df.mitigation == "Hydra") | (df.mitigation == "PARA") | (df.mitigation == "Graphene"))), "norm_energy"] = 1

    df = df[(df['config'].str.contains("PaCRAM-H"))]
    df['mitigation'] = pd.Categorical(df['mitigation'], ["PARA", "RFM", "PRAC", "Hydra", "Graphene"])
    df.sort_values("mitigation", inplace=True)

    plot_df = df
    ax = axarr[i]
    sns.lineplot(data=plot_df, x="nRH", y="norm_energy", hue="mitigation", ax=ax, markers=True, dashes=False, palette=colors, marker="o", linewidth=1, markersize=4, 
            hue_order=["PARA", "RFM", "PRAC", "Hydra", "Graphene"])

    ax.invert_xaxis()
    ax.set_xscale('log', base=2)
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

    ax.set_ylim(0.79, 1.01)
    ax.set_yticks([0.80, 0.85, 0.90, 0.95, 1])
    if i == 0:
        ax.set_yticklabels(["0.80", "0.85", "0.90", "0.95", "1.00"], fontsize=8.5)
    else:
        ax.set_yticklabels(["", "", "", "", ""], fontsize=8.5)
    handles, labels = ax.get_legend_handles_labels()
    if i == 0:
        ax.set_ylabel("Energy Cons. (Norm.\nto RH Defenses)", fontsize=10, x=0, y=0.4, labelpad=2)

    test_type = "Singlecore" if i == 0 else "Multicore"
    ax.text(0.03, 0.03, test_type, horizontalalignment='left', verticalalignment='bottom', transform=ax.transAxes, 
            fontsize=8.5, bbox=dict(facecolor='white', alpha=0.5, boxstyle='round,pad=0.1'))


fig.legend(handles, labels, loc="center left", frameon=True, handlelength=0.8, fontsize=8.5, 
            bbox_to_anchor=(0.9, 0.5), labelspacing=0.2,
            borderaxespad=0.15, handletextpad=0.15, columnspacing=0.4, ncols=1)

plt.subplots_adjust(hspace=0.1, wspace=0.05)
fig.supxlabel('RowHammer Threshold ($N_{RH}$)', fontsize=10, x=0.5, y=-0.26)
fig.savefig(PLOT_DIR + "fig18_energy.png", bbox_inches='tight')
fig.savefig(PLOT_DIR + "fig18_energy.pdf", bbox_inches='tight')
