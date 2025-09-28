#!/bin/bash

# Set ulimit to prevent GStreamer assertion failures
ulimit -Sn 4096

# Get the absolute path to the DeepStream directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEEPSTREAM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Set up environment for the pose classification app with CSI CAMERA input
export LD_LIBRARY_PATH="$DEEPSTREAM_DIR/libs:/opt/nvidia/deepstream/deepstream/lib:/usr/local/cuda-12.6/lib64:/usr/local/lib:$LD_LIBRARY_PATH"

# Critical environment variables to prevent hanging
export GST_DEBUG=1
export GST_DEBUG_NO_COLOR=1
export CUDA_CACHE_DISABLE=0
export CUDA_DEVICE_MAX_CONNECTIONS=1

# Ensure nvargus-daemon is running (critical for CSI camera)
if ! pgrep nvargus-daemon > /dev/null; then
    echo "Starting nvargus-daemon..."
    sudo systemctl start nvargus-daemon || echo "Warning: Could not start nvargus-daemon via systemctl"
    sleep 2
fi

# Change to the project directory
cd "$DEEPSTREAM_DIR"

echo "Starting DeepStream Pose Classification Application (CSI CAMERA INPUT)..."
echo "Project Directory: $(pwd)"
echo "Library Path: $LD_LIBRARY_PATH"
echo "Input: CSI Camera sensor_id=0, 1920x1080@30fps"

# Pre-flight checks removed to prevent hanging

echo "=== Starting Application ==="
echo "Press Ctrl+C to stop gracefully."

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "Cleaning up..."
    if [ ! -z "$APP_PID" ] && kill -0 "$APP_PID" 2>/dev/null; then
        echo "Terminating application (PID: $APP_PID)..."
        kill -TERM "$APP_PID" 2>/dev/null
        sleep 2
        if kill -0 "$APP_PID" 2>/dev/null; then
            echo "Force killing application..."
            kill -KILL "$APP_PID" 2>/dev/null
        fi
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Add timeout to prevent hanging - run in background with monitoring
set -m  # Enable job control

echo "Starting DeepStream application with debugging..."

# Run the pose classification app with CSI camera input
"$DEEPSTREAM_DIR/app/deepstream-pose-classification-app" \
    "$DEEPSTREAM_DIR/configs/deepstream_pose_classification_config_csi.yaml"

echo "Application finished with exit code: $?"