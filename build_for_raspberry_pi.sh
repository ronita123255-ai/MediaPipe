#!/bin/bash
# build_for_raspberry_pi.sh
# Cross-compile MediaPipe for Raspberry Pi on x86_64 desktop
# Usage: ./build_for_raspberry_pi.sh [arm64|armv7]

set -e

TARGET_ARCH=${1:-arm64}  # Default to ARM64 (Pi 4/5)

echo "============================================"
echo "MediaPipe Build for Raspberry Pi"
echo "Target Architecture: $TARGET_ARCH"
echo "============================================"

# Check Bazel
if ! command -v bazel &> /dev/null; then
    echo "ERROR: Bazel not found. Install from https://bazel.build/install"
    exit 1
fi

# Build configuration based on architecture
if [ "$TARGET_ARCH" = "arm64" ]; then
    echo "Building for ARM64 (Raspberry Pi 4/5, 64-bit)..."
    
    bazel build -c opt \
        --crosstool_top=@crosstool//:toolchains \
        --compiler=gcc \
        --cpu=aarch64 \
        --copt=-march=armv8-a \
        --copt=-O3 \
        --define MEDIAPIPE_DISABLE_GPU=1 \
        //mediapipe/python:_framework_bindings
    
    OUTPUT_DIR="bazel-bin/mediapipe/python"
    
elif [ "$TARGET_ARCH" = "armv7" ]; then
    echo "Building for ARMv7 (Raspberry Pi 3, 32-bit)..."
    
    bazel build -c opt \
        --crosstool_top=@crosstool//:toolchains \
        --compiler=gcc \
        --cpu=armv7a \
        --copt=-march=armv7-a \
        --copt=-mfpu=neon \
        --copt=-O3 \
        --define MEDIAPIPE_DISABLE_GPU=1 \
        //mediapipe/python:_framework_bindings
    
    OUTPUT_DIR="bazel-bin/mediapipe/python"
    
else
    echo "ERROR: Unknown architecture. Use 'arm64' or 'armv7'"
    exit 1
fi

echo ""
echo "============================================"
echo "Build Complete!"
echo "Output directory: $OUTPUT_DIR"
echo "============================================"

# List outputs
if [ -d "$OUTPUT_DIR" ]; then
    echo "Build artifacts:"
    ls -lh "$OUTPUT_DIR"
else
    echo "WARNING: Output directory not found"
fi

echo ""
echo "Next steps:"
echo "1. Copy the compiled binaries to Raspberry Pi:"
echo "   scp -r $OUTPUT_DIR pi@raspberrypi.local:~/mediapipe_build/"
echo ""
echo "2. On Raspberry Pi, install:"
echo "   cd ~/mediapipe_build"
echo "   pip3 install -e ."
echo ""
