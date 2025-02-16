import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

PWD = os.getcwd()
CSV_DIR = f"{PWD}/../Ram_results/processed/"
PLOT_DIR = f"{PWD}/../Ram_plots/"
if not os.path.exists(PLOT_DIR):
    os.makedirs(PLOT_DIR)
    
fig_width = 4
fig_height = fig_width * 0.37
colors = sns.color_palette("tab10", 5)
fig, axarr = plt.subplots(1, 2, figsize=(fig_width, fig_height))

for i, core in enumerate(["single", "multi"]):
    df = pd.read_csv(f"{CSV_DIR}{core}core_pacram_best.csv")

    if core == "single":
        df = df[~((df["config"] == "PaCRAM-S") & ((df["mitigation"] == "Graphene") | (df["mitigation"] == "Hydra")))]
        df.rename(columns={"n_ipc_over_nodefense": "norm_ipc"}, inplace=True)
    else:
        df = df[~((df["config"] == "PaCRAM-S") & ((df["mitigation"] == "Graphene") | (df["mitigation"] == "Hydra") | (df["mitigation"] == "PARA")))]
        df.rename(columns={"n_weighted_speedup_over_nodefense": "norm_ipc"}, inplace=True)
    # df = df.groupby(["mitigation", "nRH", "config"]).mean().reset_index()
    # df['mitigation'] = pd.Categorical(df['mitigation'], ["PARA", "RFM", "PRAC", "Hydra", "Graphene"])
    # df.sort_values("mitigation", inplace=True)

    ax = axarr[i]
    sns.lineplot(data=df, x="nRH", y="norm_ipc", hue="mitigation", style="config", ax=ax, markers=False, 
                    palette=colors, linewidth=1, alpha=1, err_style="band", errorbar=("ci", 100),
                    hue_order=["PARA", "RFM", "PRAC", "Hydra", "Graphene"],
                    style_order=["Default", "PaCRAM-H", "PaCRAM-M", "PaCRAM-S"])

    ax.invert_xaxis()
    ax.set_xscale('log', base=2)
    ax.set_xticks([1024, 512, 256, 128, 64, 32])
    xticklabels = []
    for x in [1024, 512, 256, 128, 64, 32]:
        xticklabels += [str(int(x/1024))+"K" if x >= 1024 else str(int(x))]
    ax.set_xticklabels(xticklabels, rotation=90, fontsize=8.5)
            
    ax.grid(which="major", axis="y", color="black", alpha=0.5, linestyle="dotted", linewidth=0.5, zorder=0)
    ax.grid(which="minor", axis="y", color="gray", alpha=0.2, linestyle="dotted", linewidth=0.5, zorder=0)
    ax.axhline(y=1, color="black", linestyle="dashed", linewidth=1, zorder=0)

    handles, labels = ax.get_legend_handles_labels()
    labels[-4:] = ["No PaCRAM", "PaCRAM-H", "PaCRAM-M", "PaCRAM-S"]
    handles = handles[1:6] + handles[-4:]
    labels = labels[1:6] + labels[-4:]
    for a in range(8):
        handles[a].set_linewidth(1.5)
        
    ax.legend().remove()
    ax.set_ylabel("")
    ax.set_xlabel("")
    ax.set_title("")

    ax.set_ylim(0.29, 1.0+0.01*0.7/0.4)
    ax.set_yticks([0.4, 0.6, 0.8, 1])
    if i == 0:
        ax.set_yticklabels(["0.4", "0.6", "0.8", "1.0"], fontsize=8.5)         
    else:
        ax.set_yticklabels(["", "", "", ""], fontsize=8.5)         
    ax.xaxis.set_tick_params(pad=0, length=2)
    ax.yaxis.set_tick_params(pad=0, length=2)
    test_type = "Single-core" if i == 0 else "Multi-core"
    ax.text(0.03, 0.03, test_type, horizontalalignment='left', verticalalignment='bottom', transform=ax.transAxes, 
            fontsize=8.5, bbox=dict(facecolor='white', alpha=0.5, boxstyle='round,pad=0.1'))
    if i == 0:
        ax.set_ylabel("System performance\n(normalized to no\nRowHammer mitigation)", fontsize=9, x=0, y=0.37, labelpad=2)

fig.legend(handles, labels, loc="center left", ncols=1, fancybox=True, fontsize=8.5,
            borderpad=0.2, labelspacing=0.2, bbox_to_anchor=(0.9, 0.42), 
            columnspacing=0.5, handletextpad=0.3, handlelength=1.5)

plt.subplots_adjust(hspace=0.04, wspace=0.05)
fig.supxlabel('RowHammer threshold ($N_{RH}$)', fontsize=9, x=0.5, y=-0.18)
fig.savefig(PLOT_DIR + "fig17_perf_imp.png", bbox_inches='tight', pad_inches=0.01)
fig.savefig(PLOT_DIR + "fig17_perf_imp.pdf", bbox_inches='tight', pad_inches=0.01)