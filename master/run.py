#!/usr/bin/env python3
"""
Master Server Runner
Starts both backend and frontend services simultaneously
"""

import subprocess
import sys
import signal
import os
from pathlib import Path

# Get project root
project_root = Path(__file__).parent
backend_dir = project_root / "backend"
frontend_dir = project_root / "frontend"

processes = []


def cleanup():
    """Terminate all subprocesses"""
    print("\n🛑 Shutting down services...")
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        except Exception as e:
            print(f"Error terminating process: {e}")
    print("✅ All services stopped")


def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    cleanup()
    sys.exit(0)


def check_and_install_dependencies():
    """Check and install dependencies if needed"""
    # Check frontend dependencies
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        subprocess.run(
            ["npm", "install"],
            cwd=frontend_dir,
            check=True
        )
    
    # Check backend dependencies (basic check)
    try:
        import fastapi
    except ImportError:
        print("📦 Installing backend dependencies...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            cwd=backend_dir,
            check=True
        )


def main():
    """Start backend and frontend services"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("🚀 Starting Master services...")
    print("   Backend: http://localhost:8000")
    print("   Frontend: http://localhost:3000")
    print("   (Press Ctrl+C to stop)\n")

    # Check and install dependencies
    check_and_install_dependencies()

    # Start backend
    print("📦 Starting backend server...")
    backend_process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=backend_dir,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    processes.append(backend_process)

    # Wait a moment for backend to start
    import time
    time.sleep(2)

    # Start frontend
    print("📦 Starting frontend dev server...")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    processes.append(frontend_process)

    # Wait for all processes
    try:
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    main()

