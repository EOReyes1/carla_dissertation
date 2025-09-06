#!/bin/bash

PORT=$1

if [[ -z "$PORT" ]]; then
    echo "ERROR: Must provide a port as the first argument."
    exit 2
fi

# Direct execution without SSH
apptainer exec instance://pylot_${SLURM_ARRAY_TASK_ID:-single} bash -c '
    cd /home/erdos/workspace/pylot/
    export PYTHONPATH="$PYTHONPATH:$PYLOT_HOME/dependencies/lanenet/"
    python3 pylot.py --flagfile=configs/e2e.conf --simulator_port='"$PORT"' > /home/erdos/workspace/results/pylot_runner_${SLURM_ARRAY_TASK_ID}.log 2>&1
'
