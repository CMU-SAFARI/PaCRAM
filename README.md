## PaCRAM: Understanding RowHammer Under Reduced Refresh Latency: Experimental Analysis of Real DRAM Chips and Implications on Future Solutions
PaCRAM is a technique that reduces the performance overhead of RowHammer mitigation mechanisms by carefully reducing the preventive refresh latency that are issued by RowHammer mitigations without compromising system security.

## Repository File Structure 

```
.
+-- DB_scripts/                           # Scripts to parse and plot DRAM Bender Results
+-- Ram_scripts/                          # Scripts to parse and plot Ramulator2 results
│   +-- ramulator_pacram/src              # Ramulator2 source code
│   │   +-- dram/impl
│   │   │   +-- DDR5-RVRR.cpp     # DDR5 implementation that supports partial charge restoration
│   │   +-- dram_controller
│   │   │   +-- impl/plugin
│   │   │   │   │   +-- pacram.h      # Ramulator2 plugin that implements PaCRAM
│   │   ...
...
+-- README.md                             # This file                        
```

## Installation Guide:

### Prerequisites:
- Git
- g++ with c++20 capabilities (g++-10 or above recommended)
- Python3 (3.10 or above recommended)
 
### Installation steps:
1. Clone the repository `git clone https://github.com/yct000/PaCRAM`
2. Install python dependencies, build Ramulator2, and download DRAM Bender results and traces with `./setup_all.sh`


## Example Use
1. Parse and plot DRAM Bender results `./plot_db_figures.sh`
2. Prepare Ramulator2 warmup checkpoints `./prepare_warmups.sh` or `./prepare_warmups_slurm.sh`.
3. Wait for the warmup runs to finish. You can use `python3 check_warmup_status.py` to track warmup status. If it reports any failed or not found runs, you can rerun step 2. 
2. Run Ramulator2 simulations `./run_ramulator_all.sh` or `./run_ramulator_all_slurm.sh`.
3. Wait for the runs to finish. You can use `python3 check_run_status.py` to track run status. If it reports any failed or not found runs, you can rerun step 4. 
4. Parse simulation results and process them with `./parse_ram_results.sh`
5. Generate figures with `./plot_ram_figures.sh`

## Simulation Configuration Parameters
Execution of Ramulator2 simulations can be configured with the following configuration parameters. These parameters reside in `Ram_scripts/utils_runs.py` unless the parameter description below states a different path.

`MITIGATION_LIST`: The list of tested RowHammer mitigations

`NRH_VALUES`: The list of tested RowHammer threshold values

`MFR_DICT`: The dictionary of charge restoration amounts for different manufacturers

## Contacts:
Yahya Can Tuğrul (yahyacantugrul [at] gmail [dot] com)  
