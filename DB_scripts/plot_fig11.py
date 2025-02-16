import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

csv_dir = os.getcwd() + "/../DB_results/processed_rpcr"
plots_dir = os.getcwd() + "/../DB_plots/"

if not os.path.exists(plots_dir):
    os.makedirs(plots_dir)
    
df = pd.read_csv(csv_dir + "/processed_RPCR.csv")
# df = df[df['mfr'] != "Mfr. M"]

hhh = plt.plot([],marker="", ls="")[0]

fig_width = 5
fig_height = fig_width * 0.32
fig, axarr = plt.subplots(1, 3, figsize=(fig_width, fig_height))

for i, (mfr, mfrdf) in enumerate(df.groupby("mfr")):
    ax = axarr.flatten()[i]
    
    sns.boxplot(
        data = mfrdf,
        x="norm_tras",
        y="norm_nRH",
        hue="num_res",
        ax=ax,
        palette="tab10",
        linewidth=0.5,
        fliersize=0,
        hue_order = [5,4,3,2,1],
    )
    ax.set_xlim(ax.get_xlim()[::-1])
    
    ax.set_axisbelow(True)
    ax.grid(which="major", axis="both", color="black", alpha=0.5, linestyle="dotted", linewidth=0.5, zorder=0)
    ax.grid(which="minor", axis="both", color="gray", alpha=0.2, linestyle="dotted", linewidth=0.5, zorder=0)
    ax.axhline(y=1, color="black", linestyle="dashed", linewidth=0.5, zorder=0)
    ax.axvline(x=6, color="black", linestyle="dashed", linewidth=0.5, zorder=0)
    ax.set_xlabel("")
    ax.set_ylabel("")
    if i ==0:
        ax.set_ylabel("RowHammer threshold ($N_{RH}$)\nnormalized to $N_{RH}$ @ $t_{RAS(Nom)}$", fontsize=8, x=0, y=0.5, labelpad=2)

    ax.set_ylim(0, 1.2)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2])
    if i == 0:
        ax.set_yticklabels(["0", "0.2", "0.4", "0.6", "0.8", "1.0", "1.2"], fontsize=8)
    else:
        ax.set_yticklabels(["", "", "", "", "", "", ""], fontsize=8)
    ax.text(0.105, 0.025, mfr, horizontalalignment='left', verticalalignment='bottom', transform=ax.transAxes, fontsize=8, bbox=dict(facecolor='white', alpha=0.5, boxstyle='round,pad=0.1'))

    ax.set_xticklabels(ax.get_xticklabels(), rotation=90, fontsize=8)
    ax.xaxis.set_tick_params(pad=1, length=2)
    ax.yaxis.set_tick_params(pad=1, length=2)

    h, l = ax.get_legend_handles_labels()
    h = [hhh] + h[::-1]
    l = ["Number of partial charge restorations:"] + l[::-1]
    ax.legend().remove()

fig.legend(h, l, loc="lower center", frameon=True, 
            handlelength=0.6, fontsize=7.8, title_fontsize=7.8,
            bbox_to_anchor=(0.505, 0.90),
            borderaxespad=0.15, handletextpad=0.15, columnspacing=0.3, ncols=6)
fig.supxlabel("Charge restoration latency ($t_{RAS(Red)}$)\nnormalized to the nominal charge restoration latency ($t_{RAS(Nom)}$)", fontsize=8, x=0.5, y=-0.3)

plt.subplots_adjust(hspace=0.25, wspace=0.05)
plt.savefig(plots_dir + "fig11_NRH_vs_RPCR.png", bbox_inches='tight', pad_inches=0.01)
plt.savefig(plots_dir + "fig11_NRH_vs_RPCR.pdf", bbox_inches='tight', pad_inches=0.01)
