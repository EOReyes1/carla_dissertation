#!/bin/bash


task_id="${1:-single}"

finished_file="/mnt/parscratch/users/jap24omr/SAMOTA/implementation/runner/Results_multi/finished_${task_id}.txt"

if [ -f "$finished_file" ]; then
    cp "$finished_file" ./
else
    echo "finished_${task_id}.txt not found in Results directory"
    exit 1
fi
