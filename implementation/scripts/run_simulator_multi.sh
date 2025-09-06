#!/bin/bash

set -x

export CARLA_HOME=/home/erdos/workspace/pylot/dependencies/CARLA_0.9.10.1

if [ -z "${CARLA_HOME}" ]; then
    echo "Please set \$CARLA_HOME before running this script"
    exit 1
fi

if [ -z "$1" ]; then
    echo "ERROR: Must provide a port as the first argument."
    exit 2
else
    PORT=$1
fi

echo "CARLA_HOME is set to: $CARLA_HOME"
echo "Using CARLA world-port: $PORT"

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
