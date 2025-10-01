#!/bin/bash

# Set ulimit to prevent GStreamer assertion failures
ulimit -Sn 4096

# Get the absolute path to the DeepStream directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEEPSTREAM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Set up environment for the pose classification app with FILE input
export LD_LIBRARY_PATH="$DEEPSTREAM_DIR/libs:/opt/nvidia/deepstream/deepstream/lib:/usr/local/lib:/usr/local/cuda/lib64:$LD_LIBRARY_PATH"

# Change to the project directory
cd "$DEEPSTREAM_DIR"

echo "Starting DeepStream Pose Classification Application (FILE INPUT)..."
echo "Project Directory: $(pwd)"
echo "Library Path: $LD_LIBRARY_PATH"
echo "Input: sample_walk.mov video file"

# Verify libraries exist before running
if [ ! -f "$DEEPSTREAM_DIR/libs/libshared_memory.so" ]; then
    echo "ERROR: libshared_memory.so not found at $DEEPSTREAM_DIR/libs/libshared_memory.so"
    exit 1
fi

if [ ! -f "$DEEPSTREAM_DIR/app/deepstream-pose-classification-app" ]; then
    echo "ERROR: Application binary not found at $DEEPSTREAM_DIR/app/deepstream-pose-classification-app"
    exit 1
fi

# Run the pose classification app with file input
"$DEEPSTREAM_DIR/app/deepstream-pose-classification-app" \
    "$DEEPSTREAM_DIR/configs/deepstream_pose_classification_config.yaml"

echo "Application finished."