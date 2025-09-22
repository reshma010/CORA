#!/bin/bash

# Set up environment for the pose classification app
export LD_LIBRARY_PATH=/home/jetson/CORA/DeepStream/libs:$LD_LIBRARY_PATH

# Change to the project directory
cd /home/jetson/CORA/DeepStream

echo "Starting DeepStream Pose Classification Application..."
echo "Project Directory: $(pwd)"
echo "Library Path: $LD_LIBRARY_PATH"
echo ""
echo "Available input options:"
echo "  - For FILE input: ./scripts/run_pose_classification_file.sh"
echo "  - For CSI Camera: ./scripts/run_pose_classification_csi.sh"
echo ""
echo "Using DEFAULT FILE INPUT (sample_walk.mov)..."

# Run the pose classification app with file input (default)
./app/deepstream-pose-classification-app \
    configs/deepstream_pose_classification_config.yaml

echo "Application finished."