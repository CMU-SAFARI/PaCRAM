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

csv_filename = CSV_DIR + "singlecore_pacram.csv"

sc_df = pd.read_csv(csv_filename)
sc_df.drop(columns=set(sc_df.columns) 
                - set(['trace', 'mitigation', 'nRH', 'n_ipc_over_default', 'config']), inplace=True)

sc_df = sc_df[(sc_df.config != "PARA") & (sc_df.config != "Graphene") & (sc_df.config != "Hydra") & (sc_df.config != "RFM") & (sc_df.config != "PRAC")]
sc_df.rename(columns={"n_ipc_over_default": "norm_ipc"}, inplace=True)

sc_df['latency_reduction'] = sc_df['config'].apply(lambda x: float(x.split("_")[2]))
sc_df['config'] = sc_df['config'].apply(lambda x: x.split("_")[1])
sc_df['config'] = sc_df['config'].apply(lambda x: "PaCRAM-S" if "Mfr. S" in x else "PaCRAM-H")

for config in sc_df.config.unique():
    for nRH in sc_df.nRH.unique():
        for mech in sc_df.mitigation.unique():
                for trace in sc_df.trace.unique():
                    sc_df = sc_df.append({'config': config, 'nRH': nRH, 'mitigation': mech, 'trace': trace, 'norm_ipc': 1.0, 'latency_reduction': 1.0}, ignore_index=True)

num_mechs = sc_df.mitigation.unique().shape[0]
num_modules = sc_df.config.unique().shape[0]

sc_df['mitigation'] = pd.Categorical(sc_df['mitigation'], ["PARA", "RFM", "PRAC", "Hydra", "Graphene"])
sc_df.sort_values("mitigation", inplace=True)


num_mechs = sc_df.mitigation.unique().shape[0]
num_modules = sc_df.config.unique().shape[0]
fig, axarr = plt.subplots(num_modules, num_mechs, figsize=(8, 2.1))
colors = sns.color_palette("plasma", 6)

for c_id, (config, configdf) in enumerate(sc_df.groupby("config")):
    mfr = "Mfr. " + config.split("-")[1]
    for m_id, (mech, mechdf) in enumerate(configdf.groupby("mitigation")):
        ax = axarr.flatten()[c_id*num_mechs + m_id]
        sns.lineplot(data=mechdf, x="latency_reduction", y="norm_ipc", hue="nRH", ax=ax, markers=True, 
                    dashes=False, palette=colors, marker="o", markersize=3, linewidth=1,
                    err_style="band", errorbar=("ci", 100))

        ax.invert_xaxis()
        ax.set_xticks([0.25, 0.50, 0.75, 1.0])
        if c_id == 1:
            ax.set_xticklabels(ax.get_xticklabels(), fontsize=6.5, rotation=90)            
        else:
            ax.set_xticklabels(["", "", "", ""], fontsize=6.5)            
        ax.grid(which="major", axis="y", color="black", alpha=0.5, linestyle="dotted", linewidth=0.5, zorder=0)
        ax.grid(which="minor", axis="y", color="gray", alpha=0.2, linestyle="dotted", linewidth=0.5, zorder=0)
        ax.axhline(y=1, color="black", linestyle="dashed", linewidth=0.5, zorder=0)
        handles, labels = ax.get_legend_handles_labels()
        labels = ["32", "64", "128", "256", "512", "1K"]

        if c_id == 0:
            ax.axvline(x=0.36, color="red", linestyle="dashed", linewidth=1, zorder=0)
        else:
            if m_id == 0 or m_id == 1 or m_id == 2:
                ax.axvline(x=0.45, color="red", linestyle="dashed", linewidth=1, zorder=0)
            else:
                ax.axvline(x=1, color="red", linestyle="dashed", linewidth=1, zorder=0)

        ax.set_ylabel("")
        ax.set_xlabel("")
        ax.set_title("")

        if c_id == 0:
            ax.set_title(mech, fontsize=7.5, pad=2)

        if mfr == "Mfr. H":
            ax.text(0.03, 0.97, "PaCRAM-H", horizontalalignment='left', verticalalignment='top', transform=ax.transAxes, 
                fontsize=7.5, bbox=dict(facecolor='white', alpha=0.5, boxstyle='round,pad=0.1'))
            
        if mfr == "Mfr. S":
            ax.text(0.03, 0.97, "PaCRAM-S", horizontalalignment='left', verticalalignment='top', transform=ax.transAxes, 
                fontsize=7.5, bbox=dict(facecolor='white', alpha=0.5, boxstyle='round,pad=0.1'))
            
        ax.set_axisbelow(True)
        ax.grid(color='gray', linestyle='dashed')

        if m_id == 0 or m_id == 1:
            ax.set_ylim(0.75, 1.25)
            ax.set_yticks([0.8, 0.9, 1.0, 1.1, 1.2])
            ax.set_yticklabels([0.8, 0.9, 1.0, 1.1, 1.2], fontsize=6.5)            
        else:
            ax.set_ylim(0.93, 1.07)
            ax.set_yticks([0.95, 1.0, 1.05])
            ax.set_yticklabels([0.95, "1.00", 1.05], fontsize=6.5)
        ax.xaxis.set_tick_params(pad=0, length=2)
        ax.yaxis.set_tick_params(pad=0, length=2)
        ax.legend(handles, labels, loc="lower left", ncols=2, fancybox=True, fontsize=5.8,
                    borderpad=0.2, labelspacing=0.2,  
                    columnspacing=0.5, handletextpad=0.3, handlelength=1,  bbox_transform=ax.transAxes)

plt.subplots_adjust(hspace=0.04, wspace=0.24)
fig.supylabel('Instruction-per-cycle (IPC)\n(normalized to baseline IPC @ $t_{RAS(Nom)}$)', 
                fontsize=7.5, va="center", ha="center", x=0.08, y=0.42)
fig.supxlabel('Charge restoration latency ($t_{RAS(Red)}$), normalized to the nominal charge restoration latency ($t_{RAS(Nom)}$)', 
                fontsize=7.5, x=0.5, y=-0.08)
fig.savefig(PLOT_DIR + "fig16_latency_reduction_sens.png", bbox_inches='tight', pad_inches=0.01)
fig.savefig(PLOT_DIR + "fig16_latency_reduction_sens.pdf", bbox_inches='tight', pad_inches=0.01)
