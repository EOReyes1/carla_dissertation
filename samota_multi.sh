#!/bin/bash
#SBATCH --mail-user=ereyes1@sheffield.ac.uk
#SBATCH --mail-type=ALL
#SBATCH --job-name=samota-multi
#SBATCH --output=log/samota_%A_%a.out
#SBATCH --error=log/samota_%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=50G
#SBATCH --time=02:30:00
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --array=0-2

#---------------------------------

module load Anaconda3/2024.02-1

source activate samota_v3

SAMOTA_PATH="/mnt/parscratch/users/jap24omr/SAMOTA/implementation/runner"

cd "$SAMOTA_PATH"

python3 run_SAMOTA_multi.py
