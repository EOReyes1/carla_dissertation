#!/bin/bash

if [ -f "/mnt/parscratch/users/jap24omr/SAMOTA/implementation/runner/Results/finished.txt" ]; then
    cp "/mnt/parscratch/users/jap24omr/SAMOTA/implementation/runner/Results/finished.txt" ./
else
    echo "finished.txt not found in Results directory"
    exit 1
fi
