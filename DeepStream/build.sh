#!/bin/bash

# Top-level build script for DeepStream Pose Classification
# This script builds all components and places them in the correct locations

# Check if CUDA_VER is set
if [ -z "$CUDA_VER" ]; then
    echo "CUDA_VER environment variable is not set. Setting to 12.6"
    export CUDA_VER=12.6
fi

echo "Building DeepStream Pose Classification with CUDA $CUDA_VER..."

# Create output directories
echo "Creating output directories..."
mkdir -p libs app

# Build shared memory library first
echo "Building shared memory library..."
cd src/shared_memory
make clean && make && make install
if [ $? -ne 0 ]; then
    echo "Failed to build shared memory library"
    exit 1
fi
cd ../..

# Build all other components
echo "Building pose classification parsers..."
cd src/parsers
make clean && make
cd ../..

echo "Building preprocessors..."
cd src/preprocessors
make clean && make
cd ../..

echo "Building body pose implementation..."
cd src/bodypose_impl  
make clean && make
cd ../..

# Build main application (this also builds its subdirectories)
echo "Building main application..."
cd src/main
make clean && make
if [ $? -ne 0 ]; then
    echo "Failed to build main application"
    exit 1
fi
cd ../..

echo "Build complete!"
echo "Executable: app/deepstream-pose-classification-app"
echo "Libraries: libs/"

# Set library path for runtime
echo "Setting up library paths..."
export LD_LIBRARY_PATH=$PWD/libs:$LD_LIBRARY_PATH

echo "All components built successfully!"
echo "To run: ./app/deepstream-pose-classification-app --config configs/deepstream_pose_classification_config.yaml"