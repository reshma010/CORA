#!/bin/bash

# Set up environment for the pose classification app with FILE input
export LD_LIBRARY_PATH=/home/jetson/v1DeepStreamPose/libs:$LD_LIBRARY_PATH

# Change to the project directory
cd /home/jetson/v1DeepStreamPose

echo "Starting DeepStream Pose Classification Application (FILE INPUT)..."
echo "Project Directory: $(pwd)"
echo "Library Path: $LD_LIBRARY_PATH"
echo "Input: sample_walk.mov video file"

# Run the pose classification app with file input
./app/deepstream-pose-classification-app \
    configs/deepstream_pose_classification_config.yaml

echo "Application finished."