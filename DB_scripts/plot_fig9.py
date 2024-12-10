import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

csv_dir = os.getcwd() + "/../DB_results/processed_ber"
plots_dir = os.getcwd() + "/../DB_plots/"

if not os.path.exists(plots_dir):
    os.makedirs(plots_dir)

df = pd.read_csv(csv_dir + "/processed_BER.csv")

fig_width = 4
fig_height = fig_width * 0.3
fig, axarr = plt.subplots(1, 3, figsize=(fig_width, fig_height))

for i, (mfr, mfrdf) in enumerate(df.groupby("mfr")):
    ax = axarr.flatten()[i]
    sns.boxplot(
        data = mfrdf,
        x="norm_tras",
        y="norm_bfs",
        ax=ax,
        palette="tab10",
        linewidth=0.5,
        fliersize=0,
    )
    ax.set_xlim(ax.get_xlim()[::-1])
    
    ax.set_axisbelow(True)
    ax.grid(which="major", axis="both", color="black", alpha=0.5, linestyle="dotted", linewidth=0.5, zorder=0)
    ax.grid(which="minor", axis="both", color="gray", alpha=0.2, linestyle="dotted", linewidth=0.5, zorder=0)
    ax.axhline(y=1, color="black", linestyle="dashed", linewidth=0.5, zorder=0)
    ax.axvline(x=6, color="black", linestyle="dashed", linewidth=0.5, zorder=0)
    ax.set_xlabel("")
    ax.set_ylabel("")

    ax.set_yscale("log", base=2)
    ax.set_ylim(0.25, 64)
    ax.set_yticks([0.25, 0.5, 1, 2, 4, 8, 16, 32, 64])
    if i == 0:
        ax.set_yticklabels(["1/4", "", "1", "", "4", "", "16", "", "64"], fontsize=8.5)
    else:
        ax.set_yticklabels(["", "", "", "", "", "", "", "", ""], fontsize=8.5)

    ax.set_xticklabels(ax.get_xticklabels(), rotation=90, fontsize=8.5)
    ax.xaxis.set_tick_params(pad=1, length=2)
    ax.yaxis.set_tick_params(pad=1, length=2)

    ax.set_xlabel("")
    ax.set_ylabel("")
    if i ==0:
        ax.set_ylabel("RowHammer $BER$\nNorm. to $BER$ @ $t_{RAS(Nom)}$", fontsize=8.5, x=0, y=0.25, labelpad=2)

    ax.text(0.105, 0.025, mfr, horizontalalignment='left', verticalalignment='bottom', transform=ax.transAxes, fontsize=8.5, bbox=dict(facecolor='white', alpha=0.5, boxstyle='round,pad=0.1'))

fig.supxlabel("Charge restoration latency ($t_{RAS(Red)}$)\nNorm. to the nominal charge restoration latency ($t_{RAS(Nom)}$)", fontsize=8.5, x=0.5, y=-0.46)

plt.subplots_adjust(hspace=0.25, wspace=0.08)
plt.savefig(plots_dir + "fig9_BER_vs_PCR.png", bbox_inches='tight')
plt.savefig(plots_dir + "fig9_BER_vs_PCR.pdf", bbox_inches='tight')
