#!/bin/bash

# Combined script to run pose monitor and DeepStream pipeline with FILE input
# Starts monitor first, then pipeline

export LD_LIBRARY_PATH=/home/jetson/CORA/DeepStream/libs:$LD_LIBRARY_PATH
cd /home/jetson/CORA/DeepStream

echo "==============================================="
echo "DeepStream Pose Classification - COMPLETE PIPELINE"
echo "Input: FILE (sample_walk.mov)"
echo "==============================================="
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "Shutting down pipeline..."
    if [ ! -z "$MONITOR_PID" ]; then
        echo "Stopping pose monitor (PID: $MONITOR_PID)..."
        kill $MONITOR_PID 2>/dev/null
    fi
    if [ ! -z "$DEEPSTREAM_PID" ]; then
        echo "Stopping DeepStream app (PID: $DEEPSTREAM_PID)..."
        kill $DEEPSTREAM_PID 2>/dev/null
    fi
    echo "Pipeline stopped."
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "Step 1: Starting pose monitor with server communication..."
echo "Server: https://corabackend.onrender.com/api/detections"
echo "Unit ID: JETSON_FILE_01"
echo ""

# Start pose monitor in background
python3 scripts/pose_monitor.py \
    --server-url https://corabackend.onrender.com/api/detections \
    --unit-id JETSON_FILE_01 \
    --unit-name "Jetson File Input Unit" \
    --rtsp-uris "file:///opt/nvidia/deepstream/deepstream/samples/streams/sample_walk.mov" \
    --send-interval 2.0 \
    --batch-size 3 \
    --cooldown-walking 30.0 \
    --cooldown-sitting 90.0 \
    --cooldown-standing 90.0 &

MONITOR_PID=$!
echo "Pose monitor started (PID: $MONITOR_PID)"
echo ""

# Give monitor time to initialize
echo "Waiting 3 seconds for monitor to initialize..."
sleep 3

echo "Step 2: Starting DeepStream pose classification app..."
echo "Config: deepstream_pose_classification_config.yaml (FILE input)"
echo ""

# Start DeepStream app in background
./app/deepstream-pose-classification-app \
    configs/deepstream_pose_classification_config.yaml &

DEEPSTREAM_PID=$!
echo "DeepStream app started (PID: $DEEPSTREAM_PID)"
echo ""
echo "==============================================="
echo "PIPELINE RUNNING - Press Ctrl+C to stop both components"
echo "Monitor logs will show detection filtering and server communication"
echo "==============================================="

# Wait for both processes
wait $MONITOR_PID $DEEPSTREAM_PID

cleanup