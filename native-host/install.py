"""
Cross-platform installer for the yt-dlp extension native messaging host.
Run: python install.py [--uninstall]
"""
import json
import os
import platform
import shutil
import stat
import sys

APP_NAME = "yt-dlp-extension"
HOST_NAME = "yt_dlp_host"
EXTENSION_ID = "yt-dlp-dl@wakefield.fyi"

def get_install_dir():
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        return os.path.join(base, APP_NAME)
    elif system == "Darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", APP_NAME)
    else:
        return os.path.join(os.environ.get("XDG_DATA_HOME", os.path.join(os.path.expanduser("~"), ".local", "share")), APP_NAME)


def get_host_manifest_dir():
    system = platform.system()
    if system == "Windows":
        return None
    elif system == "Darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Mozilla", "NativeMessagingHosts")
    else:
        return os.path.join(os.path.expanduser("~"), ".mozilla", "native-messaging-hosts")


def get_host_exe_path(install_dir):
    if platform.system() == "Windows":
        return os.path.join(install_dir, "host.exe")
    return os.path.join(install_dir, "host")


def install():
    system = platform.system()
    install_dir = get_install_dir()
    os.makedirs(install_dir, exist_ok=True)

    host_exe = get_host_exe_path(install_dir)

    # Copy the frozen host executable
    src_dir = os.path.dirname(os.path.abspath(__file__))
    if system == "Windows":
        src_exe = os.path.join(src_dir, "host.exe")
    else:
        src_exe = os.path.join(src_dir, "host")

    if os.path.exists(src_exe):
        shutil.copy2(src_exe, host_exe)
        if system != "Windows":
            os.chmod(host_exe, os.stat(host_exe).st_mode | stat.S_IEXEC)
        print(f"Installed host to: {host_exe}")
    else:
        # Dev mode: copy the Python script and create a wrapper
        shutil.copy2(os.path.join(src_dir, "host.py"), os.path.join(install_dir, "host.py"))
        if system == "Windows":
            wrapper = os.path.join(install_dir, "host.bat")
            with open(wrapper, "w") as f:
                f.write(f'@echo off\npython "{os.path.join(install_dir, "host.py")}"\n')
            host_exe = wrapper
        else:
            wrapper = os.path.join(install_dir, "host.sh")
            with open(wrapper, "w") as f:
                f.write(f'#!/bin/sh\npython3 "{os.path.join(install_dir, "host.py")}"\n')
            os.chmod(wrapper, os.stat(wrapper).st_mode | stat.S_IEXEC)
            host_exe = wrapper
        print(f"Installed host (dev mode) to: {install_dir}")

    # Write native messaging host manifest
    manifest = {
        "name": HOST_NAME,
        "description": "Native messaging host for yt-dlp downloads",
        "path": host_exe,
        "type": "stdio",
        "allowed_extensions": [EXTENSION_ID],
    }

    if system == "Windows":
        manifest_path = os.path.join(install_dir, f"{HOST_NAME}.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        # Write registry key
        import winreg
        key_path = f"SOFTWARE\\Mozilla\\NativeMessagingHosts\\{HOST_NAME}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, manifest_path)
        print(f"Registry key set: HKCU\\{key_path}")
    else:
        manifest_dir = get_host_manifest_dir()
        os.makedirs(manifest_dir, exist_ok=True)
        manifest_path = os.path.join(manifest_dir, f"{HOST_NAME}.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"Host manifest written to: {manifest_path}")

    print("\nInstallation complete!")
    print("Restart Firefox for changes to take effect.")


def uninstall():
    system = platform.system()
    install_dir = get_install_dir()

    if system == "Windows":
        import winreg
        key_path = f"SOFTWARE\\Mozilla\\NativeMessagingHosts\\{HOST_NAME}"
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            print(f"Removed registry key: HKCU\\{key_path}")
        except FileNotFoundError:
            pass
    else:
        manifest_dir = get_host_manifest_dir()
        manifest_path = os.path.join(manifest_dir, f"{HOST_NAME}.json")
        if os.path.exists(manifest_path):
            os.remove(manifest_path)
            print(f"Removed host manifest: {manifest_path}")

    if os.path.exists(install_dir):
        shutil.rmtree(install_dir)
        print(f"Removed install directory: {install_dir}")

    print("\nUninstall complete.")


if __name__ == "__main__":
    if "--uninstall" in sys.argv:
        uninstall()
    else:
        install()
