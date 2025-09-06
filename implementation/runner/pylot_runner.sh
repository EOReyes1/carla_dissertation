#!/bin/bash

# Absolute paths on the host
RESULTS_DIR="/mnt/parscratch/users/jap24omr/SAMOTA/implementation/runner/Results"
PYLOT_DIR="/mnt/parscratch/users/jap24omr/SAMOTA/implementation/pylot"
SCRIPTS_DIR="/mnt/parscratch/users/jap24omr/SAMOTA/implementation/scripts"
CONFIG_FILE="/mnt/parscratch/users/jap24omr/SAMOTA/implementation/runner/e2e.conf"
EGG_CACHE_DIR="/mnt/parscratch/users/jap24omr/SAMOTA/tmp/python-eggs"
mkdir -p "$EGG_CACHE_DIR"

apptainer exec --nv --containall \
    --bind "$RESULTS_DIR:/home/erdos/workspace/results:rw" \
    --bind "$PYLOT_DIR:/home/erdos/workspace/pylot/pylot:rw" \
    --bind "$SCRIPTS_DIR:/home/erdos/workspace/pylot/scripts:rw" \
    --bind "$CONFIG_FILE:/home/erdos/workspace/pylot/configs/e2e.conf:rw" \
    --bind "$EGG_CACHE_DIR:/tmp/python-eggs:rw" \
    /mnt/parscratch/users/jap24omr/SAMOTA/pylot_improvedv2.sif \
    /bin/bash -c "
        cd /home/erdos/workspace/pylot && \
        mkdir -p /tmp/python-eggs && \
        export PYTHON_EGG_CACHE=/tmp/python-eggs && \
        export PYTHONPATH="\$PYTHONPATH:\$PYLOT_HOME/dependencies/lanenet/" && \
        python3 pylot.py --flagfile=configs/e2e.conf > /home/erdos/workspace/results/pylot_runner.log 2>&1     
    "

