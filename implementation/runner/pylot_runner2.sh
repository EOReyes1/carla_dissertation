#!/bin/bash

# Direct execution without SSH
apptainer exec instance://pylot bash -c '
    cd /home/erdos/workspace/pylot/
    export PYTHONPATH="$PYTHONPATH:$PYLOT_HOME/dependencies/lanenet/"
    python3 pylot.py --flagfile=configs/e2e.conf > /home/erdos/workspace/results/pylot_runner.log 2>&1
'
