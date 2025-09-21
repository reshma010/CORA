#!/bin/bash

# Set up environment for the pose classification app with CSI CAMERA input
export LD_LIBRARY_PATH=/home/jetson/v1DeepStreamPose/libs:$LD_LIBRARY_PATH

# Change to the project directory
cd /home/jetson/v1DeepStreamPose

echo "Starting DeepStream Pose Classification Application (CSI CAMERA INPUT)..."
echo "Project Directory: $(pwd)"
echo "Library Path: $LD_LIBRARY_PATH"
echo "Input: CSI Camera sensor_id=0, 1920x1080@30fps"

# Run the pose classification app with CSI camera input
./app/deepstream-pose-classification-app \
    configs/deepstream_pose_classification_config_csi.yaml

echo "Application finished."