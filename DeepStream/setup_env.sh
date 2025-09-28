#!/bin/bash

# DeepStream Pose Classification Environment Setup
# Run this script to permanently set up the environment for the current terminal session

# Get the absolute path to the DeepStream directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEEPSTREAM_DIR="$SCRIPT_DIR"

# Set up library paths
export LD_LIBRARY_PATH="$DEEPSTREAM_DIR/libs:/opt/nvidia/deepstream/deepstream/lib:/usr/local/lib:/usr/local/cuda/lib64:$LD_LIBRARY_PATH"

# Set ulimit to prevent GStreamer issues
ulimit -Sn 4096

# Add DeepStream app to PATH for convenience
export PATH="$DEEPSTREAM_DIR/app:$PATH"

echo "DeepStream Environment Setup Complete!"
echo "DeepStream Directory: $DEEPSTREAM_DIR"
echo "Library Path: $LD_LIBRARY_PATH"
echo ""
echo "You can now run:"
echo "  ./scripts/run_pose_classification_csi.sh    - For CSI camera input"
echo "  ./scripts/run_pose_classification_file.sh   - For file input"
echo "  deepstream-pose-classification-app <config> - Direct application execution"
echo ""
echo "To make this permanent for all terminal sessions, add to ~/.bashrc:"
echo "source $DEEPSTREAM_DIR/setup_env.sh"