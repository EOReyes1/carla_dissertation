#!/bin/bash
#SBATCH --mail-user=ereyes1@sheffield.ac.uk    # Provides information about the job through an email sent here
#SBATCH --mail-type=ALL                        # Information provided includes whether job has failed, been cancelled, has started or finished
#SBATCH --job-name=samota                      # Name of the job seen on the scheduler
#SBATCH --output=log/samota_%j.out             # Any outputs provided are sent to this file
#SBATCH --error=log/samota_%j.err              # Similar to above but for errors
#SBATCH --nodes=1                              # Requests job to be allocated to one compute node
#SBATCH --ntasks-per-node=1                    # Specifies that only one task should run on each allocated node
#SBATCH --cpus-per-task=4                      # Requests for four CPU cores for each task
#SBATCH --mem=50G                              # Requests for 50GB of memory for the job. Critically as this determines wait time before job starts
#SBATCH --time=02:30:00                        # Maximum wall clock time for the job
#SBATCH --partition=gpu                        # Submit the job to the GPU, specifically the A100 GPUs
#SBATCH --gres=gpu:1                           # Requests for one GPU card for the job

#---------------------------------

# Loads Anaconda, an open source distribution of Python
# and activates a virtual environment containing all dependencies required for SAMOTA

module load Anaconda3/2024.02-1

source activate samota_v3

#---------------------------------

# Moves to required directory to begin running SAMOTA and runs run_SAMOTA.py

SAMOTA_PATH="/mnt/parscratch/users/jap24omr/SAMOTA/implementation/runner"

cd "$SAMOTA_PATH"

python3 run_SAMOTA.py


