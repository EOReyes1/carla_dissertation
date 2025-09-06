#!/bin/bash

set -x

export CARLA_HOME=/home/erdos/workspace/pylot/dependencies/CARLA_0.9.10.1
#export CARLA_HOME=/home/erdos/workspace/Carla_Versions/Carla_0.9.15

if [ -z "${CARLA_HOME}" ]; then
    echo "Please set \$CARLA_HOME before running this script"
    exit 1
fi

if [ -z "$1" ]; then
    PORT=2000
else
    PORT=$1
fi

echo "CARLA_HOME is set to: $CARLA_HOME"

${CARLA_HOME}/CarlaUE4.sh \
    -opengl \
    -windowed \
    -ResX=320 \
    -ResY=240 \
    -carla-server \
    -world-port=$PORT \
    -benchmark \
    -fps=10 \
    -quality-level=Low \
    -no-rendering-mode \
    -RenderOffScreen
