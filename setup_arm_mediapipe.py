#!/usr/bin/env python3
"""
MediaPipe ARM Setup Automation Script
Simplifies installation and configuration for ARM-based devices
Author: GitHub Copilot
"""

import os
import sys
import platform
import subprocess
import argparse
from pathlib import Path


class ARMMediaPipeSetup:
    """Handle MediaPipe setup for ARM devices"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.system_info = self._get_system_info()
    
    def _get_system_info(self):
        """Get system information"""
        info = {
            'system': platform.system(),
            'machine': platform.machine(),
            'python_version': platform.python_version(),
            'python_executable': sys.executable,
        }
        
        # Detect if ARM
        arm_indicators = ['arm', 'aarch64', 'armv7l', 'armv6l']
        info['is_arm'] = any(ind in info['machine'].lower() for ind in arm_indicators)
        
        # Detect device type
        if os.path.exists('/proc/device-tree/model'):
            with open('/proc/device-tree/model') as f:
                info['device'] = f.read().strip('\x00')
        else:
            info['device'] = 'Unknown ARM Device'
        
        return info
    
    def print_system_info(self):
        """Print detected system information"""
        print("\n" + "="*60)
        print("SYSTEM INFORMATION")
        print("="*60)
        print(f"System: {self.system_info['system']}")
        print(f"Machine: {self.system_info['machine']}")
        print(f"Device: {self.system_info.get('device', 'Unknown')}")
        print(f"Python Version: {self.system_info['python_version']}")
        print(f"Python Executable: {self.system_info['python_executable']}")
        print(f"Is ARM: {'YES' if self.system_info['is_arm'] else 'NO'}")
        print("="*60 + "\n")
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("Checking Python version...")
        version_info = sys.version_info
        
        if version_info.major != 3 or version_info.minor < 9:
            print(f"❌ Python {version_info.major}.{version_info.minor} is not supported")
            print("   MediaPipe requires Python 3.9 or later")
            return False
        
        print(f"✓ Python {version_info.major}.{version_info.minor} is compatible")
        return True
    
    def check_dependencies(self):
        """Check for required system dependencies"""
        print("\nChecking system dependencies...")
        
        dependencies = {
            'pip3': 'Python package manager',
            'python3-dev': 'Python development headers',
        }
        
        missing = []
        
        # Check pip
        try:
            subprocess.run(['pip3', '--version'], 
                          capture_output=True, check=True)
            print("✓ pip3 found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append('python3-pip')
        
        # Check python development
        if sys.platform.startswith('linux'):
            try:
                subprocess.run(['python3-config', '--includes'],
                              capture_output=True, check=True)
                print("✓ python3-dev found")
            except FileNotFoundError:
                missing.append('python3-dev')
        
        if missing:
            print(f"\n⚠ Missing dependencies: {', '.join(missing)}")
            print("\nTo install missing dependencies:")
            if sys.platform.startswith('linux'):
                print(f"  sudo apt-get install -y {' '.join(missing)}")
            return False
        
        return True
    
    def upgrade_pip(self):
        """Upgrade pip to latest version"""
        print("\nUpgrading pip...")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install',
                '--upgrade', 'pip', 'setuptools', 'wheel'
            ], check=True)
            print("✓ pip upgraded")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to upgrade pip: {e}")
            return False
    
    def install_mediapipe(self, upgrade=False):
        """Install MediaPipe package"""
        print("\nInstalling MediaPipe...")
        
        cmd = [sys.executable, '-m', 'pip', 'install']
        
        if upgrade:
            cmd.append('--upgrade')
        
        cmd.extend(['--prefer-binary', 'mediapipe'])
        
        try:
            subprocess.run(cmd, check=True)
            print("✓ MediaPipe installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install MediaPipe: {e}")
            return False
    
    def install_opencv(self):
        """Install OpenCV if not present"""
        print("\nChecking for OpenCV...")
        try:
            import cv2
            print(f"✓ OpenCV {cv2.__version__} already installed")
            return True
        except ImportError:
            print("Installing opencv-python...")
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install',
                    '--prefer-binary', 'opencv-python'
                ], check=True)
                print("✓ OpenCV installed")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install OpenCV: {e}")
                return False
    
    def verify_installation(self):
        """Verify MediaPipe installation"""
        print("\nVerifying MediaPipe installation...")
        
        try:
            import mediapipe as mp
            print(f"✓ MediaPipe {mp.__version__} installed")
            
            # Try to import common tasks
            try:
                from mediapipe.tasks import vision
                print("✓ MediaPipe vision tasks available")
            except ImportError:
                print("⚠ Vision tasks not available")
            
            return True
        except ImportError as e:
            print(f"❌ MediaPipe import failed: {e}")
            return False
    
    def create_test_script(self, output_path="test_mediapipe_arm.py"):
        """Create a test script for MediaPipe on ARM"""
        test_code = '''#!/usr/bin/env python3
"""Test MediaPipe installation on ARM device"""

import sys
import time

def test_imports():
    """Test basic imports"""
    print("Testing imports...")
    try:
        import mediapipe as mp
        print(f"✓ MediaPipe {mp.__version__}")
    except ImportError as e:
        print(f"✗ Failed to import MediaPipe: {e}")
        return False
    
    try:
        import cv2
        print(f"✓ OpenCV {cv2.__version__}")
    except ImportError as e:
        print(f"✗ Failed to import OpenCV: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✓ NumPy {np.__version__}")
    except ImportError as e:
        print(f"✗ Failed to import NumPy: {e}")
        return False
    
    return True


def test_face_detection():
    """Test face detection"""
    print("\\nTesting face detection...")
    try:
        import mediapipe as mp
        from mediapipe import solutions
        
        # Create face detection instance
        with solutions.face_detection.FaceDetection() as face_detection:
            print("✓ Face detection initialized")
        
        return True
    except Exception as e:
        print(f"✗ Face detection test failed: {e}")
        return False


def test_hands():
    """Test hand detection"""
    print("\\nTesting hand detection...")
    try:
        import mediapipe as mp
        from mediapipe import solutions
        
        # Create hands instance
        with solutions.hands.Hands() as hands:
            print("✓ Hands detection initialized")
        
        return True
    except Exception as e:
        print(f"✗ Hands detection test failed: {e}")
        return False


def test_pose():
    """Test pose detection"""
    print("\\nTesting pose estimation...")
    try:
        import mediapipe as mp
        from mediapipe import solutions
        
        # Create pose instance
        with solutions.pose.Pose() as pose:
            print("✓ Pose detection initialized")
        
        return True
    except Exception as e:
        print(f"✗ Pose detection test failed: {e}")
        return False


def benchmark_inference():
    """Simple inference benchmark"""
    print("\\nBenchmarking inference...")
    try:
        import cv2
        import numpy as np
        from mediapipe import solutions
        import time
        
        # Create test image
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Test with face detection (fast)
        with solutions.face_detection.FaceDetection() as face_detection:
            start = time.time()
            results = face_detection.process(cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB))
            elapsed = time.time() - start
            print(f"✓ Face detection inference: {elapsed*1000:.2f} ms")
        
        return True
    except Exception as e:
        print(f"✗ Benchmark failed: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("MediaPipe ARM Installation Test")
    print("="*60)
    
    tests = [
        ("Import Test", test_imports),
        ("Face Detection", test_face_detection),
        ("Hand Detection", test_hands),
        ("Pose Detection", test_pose),
        ("Inference Benchmark", benchmark_inference),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\\nTotal: {passed}/{total} tests passed")
    print("="*60)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
'''
        
        with open(output_path, 'w') as f:
            f.write(test_code)
        
        os.chmod(output_path, 0o755)
        print(f"\n✓ Test script created: {output_path}")
        print(f"  Run with: python3 {output_path}")
    
    def run_full_setup(self):
        """Run complete setup"""
        print("\n" + "="*60)
        print("MediaPipe ARM Setup")
        print("="*60)
        
        # Step 1: System info
        self.print_system_info()
        
        # Step 2: Check Python
        if not self.check_python_version():
            return False
        
        # Step 3: Check dependencies
        if not self.check_dependencies():
            print("\nContinuing without all dependencies...")
        
        # Step 4: Upgrade pip
        if not self.upgrade_pip():
            return False
        
        # Step 5: Install MediaPipe
        if not self.install_mediapipe(upgrade=True):
            return False
        
        # Step 6: Install OpenCV
        if not self.install_opencv():
            print("Continuing without OpenCV...")
        
        # Step 7: Verify
        if not self.verify_installation():
            return False
        
        # Step 8: Create test script
        self.create_test_script()
        
        print("\n" + "="*60)
        print("✓ Setup Complete!")
        print("="*60)
        print("\nNext steps:")
        print("1. Run the test script: python3 test_mediapipe_arm.py")
        print("2. Try a MediaPipe example")
        print("3. Check documentation: https://developers.google.com/mediapipe")
        print("="*60 + "\n")
        
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MediaPipe ARM Setup and Installation"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Verbose output"
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help="Only check system without installing"
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help="Only verify existing installation"
    )
    parser.add_argument(
        '--create-test',
        action='store_true',
        help="Only create test script"
    )
    
    args = parser.parse_args()
    
    setup = ARMMediaPipeSetup(verbose=args.verbose)
    
    if args.check_only:
        setup.print_system_info()
        setup.check_python_version()
        setup.check_dependencies()
        return 0
    
    if args.verify_only:
        setup.print_system_info()
        setup.verify_installation()
        return 0
    
    if args.create_test:
        setup.create_test_script()
        return 0
    
    # Run full setup
    success = setup.run_full_setup()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
