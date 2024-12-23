import os

AE_SLURM_PART_NAME="cpu_part"

# Slurm username
SLURM_USERNAME = "$USER" 

# Maximum Slurm jobs
MAX_SLURM_JOBS = 500 

# Delay between retrying Slurm job submission (when job limit is reached)
SLURM_RETRY_DELAY = 5 

SLURM_CMD = f"srun --cpus-per-task=1 --nodes=1 --ntasks=1 --partition={AE_SLURM_PART_NAME} --job-name='ramulator2_ae'"

def check_running_jobs():
    return int(os.popen(f"squeue -u {SLURM_USERNAME} -h | wc -l").read())
