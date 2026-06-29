"""Build the native host executable with PyInstaller. Accepts an optional name argument for CI."""
import subprocess
import sys
import os

HOST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "native-host")
DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

def build(name):
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--clean",
        "--name", name,
        "--distpath", DIST_DIR,
        "--workpath", os.path.join(os.path.dirname(os.path.abspath(__file__)), "build"),
        "--specpath", os.path.join(os.path.dirname(os.path.abspath(__file__)), "build"),
        os.path.join(HOST_DIR, "host.py"),
    ]
    print(f"Building {name}...")
    subprocess.check_call(cmd)
    print(f"\nBuild complete: {os.path.join(DIST_DIR, name)}")

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "yt-dlp-host-windows"
    build(name)
