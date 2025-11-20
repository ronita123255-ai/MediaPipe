# MediaPipe ARM Optimization Guide

This guide provides practical steps to optimize MediaPipe for ARM-based processors like Raspberry Pi and mobile devices.

---

## Table of Contents

1. [Installation for ARM Devices](#installation-for-arm-devices)
2. [Performance Optimization Tips](#performance-optimization-tips)
3. [Memory Optimization](#memory-optimization)
4. [Building from Source for ARM](#building-from-source-for-arm)
5. [Example Applications](#example-applications)
6. [Troubleshooting](#troubleshooting)

---

## Installation for ARM Devices

### Option 1: Easy Install (Recommended)

```bash
# For Raspberry Pi and Linux ARM devices
pip3 install --upgrade pip
pip3 install mediapipe

# Verify installation
python3 << EOF
import mediapipe as mp
print(f"MediaPipe version: {mp.__version__}")
print(f"MediaPipe installed successfully!")
EOF
```

### Option 2: Install with Specific Python Version

```bash
# For Python 3.9
python3.9 -m pip install mediapipe

# For Python 3.10
python3.10 -m pip install mediapipe

# For Python 3.11
python3.11 -m pip install mediapipe
```

### Option 3: Install from Source (Advanced)

```bash
# Prerequisites
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    python3-dev \
    python3-pip \
    protobuf-compiler \
    libopencv-dev

# Clone and build
git clone https://github.com/google/mediapipe.git
cd mediapipe
export MEDIAPIPE_DISABLE_GPU=1
python3 -m pip install -e .
```

---

## Performance Optimization Tips

### 1. Use Lightweight Models

MediaPipe provides multiple model variants. Choose based on your needs:

```python
from mediapipe.tasks import vision
from mediapipe.tasks.python.components.containers import rect

# Hand detection with lightweight model
def detect_hands_optimized(image_path):
    """Detect hands using optimized model"""
    # Use 'lite' variant for faster inference
    hand_detector = vision.HandLandmarker.create_from_options(
        vision.HandLandmarkerOptions(
            base_options=vision.HandLandmarkerOptions.BaseOptions(
                model_asset_path="hand_landmarker_lite.task"
            ),
            num_hands=1,  # Limit to 1 hand for speed
            running_mode=vision.RunningMode.IMAGE
        )
    )
    
    # ... process image
    return hand_detector
```

### 2. Reduce Input Resolution

Lower resolution = faster processing:

```python
import cv2
from mediapipe.tasks import vision

def process_with_lower_resolution(video_path, scale_factor=0.5):
    """Process video at lower resolution for speed"""
    cap = cv2.VideoCapture(video_path)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Scale down for faster processing
        height, width = frame.shape[:2]
        scaled_frame = cv2.resize(
            frame,
            (int(width * scale_factor), int(height * scale_factor))
        )
        
        # Process scaled frame
        # ... detection code ...
        
        # Scale results back up if needed
        # ...
    
    cap.release()
```

### 3. Batch Processing

Process multiple frames together:

```python
import numpy as np
from mediapipe.tasks import vision

def batch_process_frames(frames_list):
    """Process multiple frames efficiently"""
    
    # Batch processing can leverage SIMD better
    for batch in chunks(frames_list, batch_size=4):
        detections = []
        for frame in batch:
            # Process frame
            pass
        detections.append(detections)
    
    return detections

def chunks(lst, batch_size):
    """Yield successive chunks from list"""
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]
```

### 4. Enable Threading (Safe for ARM)

```python
from mediapipe.tasks import vision
from mediapipe.tasks.python.components.containers import rect
import threading

class AsyncDetector:
    """Async detection for non-blocking processing"""
    
    def __init__(self):
        self.detector = vision.ObjectDetector.create_from_options(
            vision.ObjectDetectorOptions(
                running_mode=vision.RunningMode.LIVE_STREAM,
                result_callback=self._handle_result
            )
        )
        self.results = None
        self.lock = threading.Lock()
    
    def _handle_result(self, result):
        with self.lock:
            self.results = result
    
    def get_results(self):
        with self.lock:
            return self.results
```

### 5. Cache Models

```python
from mediapipe.tasks import vision
from functools import lru_cache

@lru_cache(maxsize=1)
def get_hand_detector():
    """Cache detector instance"""
    return vision.HandLandmarker.create_from_options(
        vision.HandLandmarkerOptions(
            base_options=vision.HandLandmarkerOptions.BaseOptions(
                model_asset_path="hand_landmarker.task"
            )
        )
    )

# Use cached detector
detector = get_hand_detector()
```

---

## Memory Optimization

### 1. Release Resources

```python
import cv2
from mediapipe import solutions

def cleanup_detector(detector):
    """Properly release detector resources"""
    if detector is not None:
        # Close any open resources
        if hasattr(detector, 'close'):
            detector.close()

# Usage
try:
    detector = solutions.hands.Hands()
    # ... process ...
finally:
    cleanup_detector(detector)
```

### 2. Limit Active Instances

```python
from mediapipe.tasks import vision

class DetectorPool:
    """Reuse detector instances to save memory"""
    
    def __init__(self, max_detectors=1):
        self.detectors = []
        self.max_detectors = max_detectors
        self.index = 0
    
    def get_detector(self):
        if len(self.detectors) < self.max_detectors:
            detector = vision.FaceDetector.create_from_options(
                vision.FaceDetectorOptions()
            )
            self.detectors.append(detector)
        
        detector = self.detectors[self.index % len(self.detectors)]
        self.index += 1
        return detector

# Usage
pool = DetectorPool(max_detectors=2)
detector = pool.get_detector()
```

### 3. Use In-Memory Compression

```python
import cv2
import numpy as np

def compress_frame_for_processing(frame, quality=90):
    """Compress frame to reduce memory usage"""
    # Encode to JPEG in memory
    _, encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    # Decode back (reduces size due to compression)
    compressed = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    return compressed
```

### 4. Monitor Memory Usage

```python
import psutil
import os

def check_memory_usage():
    """Monitor memory on ARM device"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    print(f"RSS Memory: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS Memory: {memory_info.vms / 1024 / 1024:.2f} MB")
    
    # Get system memory
    vm = psutil.virtual_memory()
    print(f"Total System Memory: {vm.total / 1024 / 1024:.2f} MB")
    print(f"Available Memory: {vm.available / 1024 / 1024:.2f} MB")
    print(f"Memory Usage: {vm.percent}%")
    
    return vm.percent

# Usage
if check_memory_usage() > 80:
    print("WARNING: High memory usage!")
```

---

## Building from Source for ARM

### Method 1: Native Compilation on Raspberry Pi (Slow)

```bash
#!/bin/bash
# build_on_pi.sh - Build MediaPipe on Raspberry Pi

set -e

# Install dependencies
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    curl \
    git \
    python3-dev \
    python3-pip \
    protobuf-compiler

# Install Python dependencies
pip3 install --upgrade pip setuptools wheel
pip3 install numpy opencv-python protobuf

# Clone MediaPipe
git clone https://github.com/google/mediapipe.git
cd mediapipe

# Disable GPU (not available on Raspberry Pi)
export MEDIAPIPE_DISABLE_GPU=1

# Install with Python
python3 -m pip install -e . -v

echo "Build complete!"
```

### Method 2: Cross-Compilation (Fast - Recommended)

```bash
#!/bin/bash
# build_cross_compile.sh - Build for ARM on x86 desktop

set -e

# Build Docker image for ARM64 cross-compilation
make -C mediapipe/examples/coral PLATFORM=arm64 docker

# Inside the Docker environment, build for Raspberry Pi 4 (ARM64)
bazel build \
    --crosstool_top=@crosstool//:toolchains \
    --compiler=gcc \
    --cpu=aarch64 \
    --copt=-march=armv8-a \
    --define MEDIAPIPE_DISABLE_GPU=1 \
    //mediapipe/python:_framework_bindings

# For ARMv7 (32-bit):
bazel build \
    --crosstool_top=@crosstool//:toolchains \
    --compiler=gcc \
    --cpu=armv7a \
    --copt=-march=armv7-a \
    --copt=-mfpu=neon \
    --define MEDIAPIPE_DISABLE_GPU=1 \
    //mediapipe/python:_framework_bindings
```

### Method 3: Use Pre-built Wheels (Easiest)

```bash
# MediaPipe provides pre-built wheels for ARM
# Just install via pip (wheels are automatically selected)
pip3 install mediapipe

# Wheels available for:
# - Linux ARM64 (aarch64)
# - Linux ARMv7 (armv7l)
# - Android (via Google Play)
# - iOS (via Apple App Store)
```

---

## Example Applications

### Example 1: Real-Time Hand Detection on Raspberry Pi

```python
#!/usr/bin/env python3
"""Hand detection on Raspberry Pi camera"""

import cv2
import mediapipe as mp
from mediapipe.tasks import vision
from mediapipe.tasks.python.vision import HandLandmarkerOptions, HandLandmarker
import numpy as np

class HandDetectorPI:
    def __init__(self, model_path="hand_landmarker.task"):
        """Initialize hand detector"""
        options = HandLandmarkerOptions(
            base_options=vision.BaseOptions(model_asset_path=model_path),
            num_hands=2,
            min_hand_presence_confidence=0.5,
            min_hand_detection_confidence=0.5
        )
        self.detector = HandLandmarker.create_from_options(options)
        self.mp_drawing = mp.solutions.drawing_utils
    
    def process_frame(self, frame):
        """Process single frame"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Detect hands
        results = self.detector.detect(mp_image)
        
        # Draw annotations
        annotated_frame = frame.copy()
        for hand_landmarks in results.hand_landmarks:
            # Draw landmarks
            self.draw_landmarks(annotated_frame, hand_landmarks)
        
        return annotated_frame, results
    
    def draw_landmarks(self, frame, landmarks):
        """Draw hand landmarks on frame"""
        h, w, c = frame.shape
        for landmark in landmarks:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

def main():
    """Main function"""
    detector = HandDetectorPI()
    
    # Open camera (use 0 for default camera, or USB camera path)
    cap = cv2.VideoCapture(0)
    
    # Set lower resolution for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            result_frame, detections = detector.process_frame(frame)
            
            # Display
            cv2.imshow('Hand Detection', result_frame)
            
            # Exit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
```

### Example 2: Pose Estimation with Optimization

```python
#!/usr/bin/env python3
"""Optimized pose estimation"""

import cv2
import mediapipe as mp
from mediapipe.tasks import vision
import time

class OptimizedPoseDetector:
    def __init__(self):
        """Initialize with optimized settings"""
        options = vision.PoseLandmarkerOptions(
            base_options=vision.BaseOptions(
                model_asset_path="pose_landmarker_lite.task"  # Use lite model
            ),
            running_mode=vision.RunningMode.VIDEO,  # Video mode for efficiency
            output_segmentation_masks=False  # Disable segmentation for speed
        )
        self.detector = vision.PoseLandmarker.create_from_options(options)
        self.frame_count = 0
        self.fps = 0
        self.last_time = time.time()
    
    def process_video(self, video_path):
        """Process video with FPS tracking"""
        cap = cv2.VideoCapture(video_path)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Detect pose
            results = self.detector.detect_for_video(
                mp_image,
                int(time.time() * 1000)
            )
            
            # Draw results
            if results.pose_landmarks:
                self._draw_pose(frame, results.pose_landmarks)
            
            # Update FPS
            self.frame_count += 1
            current_time = time.time()
            if current_time - self.last_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_time = current_time
            
            # Display FPS
            cv2.putText(
                frame,
                f"FPS: {self.fps}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
            
            cv2.imshow('Pose Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
    
    def _draw_pose(self, frame, landmarks):
        """Draw pose landmarks"""
        h, w, c = frame.shape
        for landmark in landmarks:
            if landmark.visibility > 0.5:  # Only draw visible landmarks
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

# Usage
if __name__ == "__main__":
    detector = OptimizedPoseDetector()
    detector.process_video(0)  # 0 for webcam
```

---

## Troubleshooting

### Issue 1: "No module named 'mediapipe'"

```bash
# Solution: Ensure pip installed mediapipe
pip3 --version
pip3 list | grep mediapipe

# Reinstall if needed
pip3 install --upgrade --force-reinstall mediapipe
```

### Issue 2: "Segmentation fault" on ARM

```bash
# Solution: Ensure compatible Python version
python3 --version  # Should be 3.9+

# Install with verbose output to see errors
pip3 install -vv mediapipe

# Check for missing dependencies
ldd $(python3 -c "import mediapipe; print(mediapipe.__file__)")
```

### Issue 3: "Out of memory" on Raspberry Pi

```python
# Solution: Implement memory-efficient processing
import gc

def process_with_memory_management(video_path):
    cap = cv2.VideoCapture(video_path)
    
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        # ...
        
        # Periodic garbage collection
        frame_count += 1
        if frame_count % 30 == 0:
            gc.collect()
    
    cap.release()
```

### Issue 4: Slow inference

```bash
# Solution: Use lower resolution and lite models

# Check which model you're using:
grep -r "model_asset_path" your_code.py

# Switch to lite models:
# - hand_landmarker_lite.task (instead of full)
# - pose_landmarker_lite.task
# - face_detector_short_range.tflite

# Reduce input resolution in code:
# frame = cv2.resize(frame, (640, 480))
```

### Issue 5: Camera not working

```python
# Solution: Test camera availability
import cv2

def test_camera():
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Camera found at index {i}")
            ret, frame = cap.read()
            print(f"Frame captured: {ret}, Shape: {frame.shape if ret else 'N/A'}")
            cap.release()

test_camera()

# On Raspberry Pi, you might need:
# - Enable camera in raspi-config
# - Use libcamera instead of OpenCV:
# pip3 install picamera2
```

---

## Performance Benchmarking

```python
import time
import cv2
import mediapipe as mp

def benchmark_detector(detector, video_path, num_frames=100):
    """Benchmark detector performance"""
    cap = cv2.VideoCapture(video_path)
    
    times = []
    for i in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            break
        
        start = time.time()
        # Process frame
        results = detector.process_frame(frame)
        end = time.time()
        
        times.append(end - start)
    
    cap.release()
    
    # Print statistics
    print(f"Average inference time: {sum(times)/len(times)*1000:.2f} ms")
    print(f"Min: {min(times)*1000:.2f} ms")
    print(f"Max: {max(times)*1000:.2f} ms")
    print(f"FPS: {1/(sum(times)/len(times)):.2f}")

# Usage
# benchmark_detector(your_detector, "test_video.mp4")
```

---

## Conclusion

MediaPipe is production-ready for ARM-based devices. Follow these guidelines for optimal performance:

1. ✅ Use pre-built wheels (easiest and fastest)
2. ✅ Choose lightweight models (_lite variants)
3. ✅ Process at appropriate resolution
4. ✅ Cache detector instances
5. ✅ Monitor memory usage
6. ✅ Use GPU-disabled mode on Raspberry Pi
7. ✅ Consider cross-compilation for building from source

