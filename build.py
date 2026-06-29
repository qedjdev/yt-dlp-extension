"""Build the native host executable with PyInstaller."""
import subprocess
import sys
import os

HOST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "native-host")
DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

def build():
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--clean",
        "--name", "host",
        "--distpath", DIST_DIR,
        "--workpath", os.path.join(os.path.dirname(os.path.abspath(__file__)), "build"),
        "--specpath", os.path.join(os.path.dirname(os.path.abspath(__file__)), "build"),
        os.path.join(HOST_DIR, "host.py"),
    ]
    print("Building native host executable...")
    subprocess.check_call(cmd)
    print(f"\nBuild complete: {os.path.join(DIST_DIR, 'host.exe')}")

if __name__ == "__main__":
    build()
