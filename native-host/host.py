import json
import struct
import subprocess
import sys
import os
import platform
import urllib.request
import zipfile
import stat
import shutil

APP_NAME = "yt-dlp-extension"

def get_app_data_dir():
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        return os.path.join(base, APP_NAME)
    elif system == "Darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", APP_NAME)
    else:
        return os.path.join(os.environ.get("XDG_DATA_HOME", os.path.join(os.path.expanduser("~"), ".local", "share")), APP_NAME)

APP_DIR = get_app_data_dir()
BIN_DIR = os.path.join(APP_DIR, "bin")
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")

def get_ytdlp_path():
    name = "yt-dlp.exe" if platform.system() == "Windows" else "yt-dlp"
    return os.path.join(BIN_DIR, name)

def get_ffmpeg_path():
    name = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
    return os.path.join(BIN_DIR, name)

if sys.platform == "win32":
    import msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)


def read_message():
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) < 4:
        return None
    length = struct.unpack("<I", raw_length)[0]
    data = sys.stdin.buffer.read(length)
    return json.loads(data.decode("utf-8"))


def send_message(msg):
    encoded = json.dumps(msg).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("<I", len(encoded)))
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()


def ensure_dirs():
    os.makedirs(BIN_DIR, exist_ok=True)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_file(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "yt-dlp-extension/1.0"})
    with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
        shutil.copyfileobj(resp, f)


def fetch_ytdlp():
    path = get_ytdlp_path()
    if os.path.exists(path):
        return path

    send_message({"type": "progress", "data": "Downloading yt-dlp..."})
    ensure_dirs()

    system = platform.system()
    machine = platform.machine().lower()

    if system == "Windows":
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
        download_file(url, path)
    elif system == "Darwin":
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos"
        download_file(url, path)
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
    else:
        if "aarch64" in machine or "arm64" in machine:
            url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux_aarch64"
        else:
            url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux"
        download_file(url, path)
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

    return path


def fetch_ffmpeg():
    path = get_ffmpeg_path()
    if os.path.exists(path):
        return path

    send_message({"type": "progress", "data": "Downloading ffmpeg..."})
    ensure_dirs()

    system = platform.system()
    machine = platform.machine().lower()
    tmp_zip = os.path.join(APP_DIR, "ffmpeg_tmp.zip")

    try:
        if system == "Windows":
            url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            download_file(url, tmp_zip)
            with zipfile.ZipFile(tmp_zip) as zf:
                for member in zf.namelist():
                    basename = os.path.basename(member)
                    if basename in ("ffmpeg.exe", "ffprobe.exe"):
                        data = zf.read(member)
                        dest = os.path.join(BIN_DIR, basename)
                        with open(dest, "wb") as f:
                            f.write(data)
        elif system == "Darwin":
            url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-macosarm64-gpl.zip"
            if "x86_64" in machine:
                url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-macos64-gpl.zip"
            download_file(url, tmp_zip)
            with zipfile.ZipFile(tmp_zip) as zf:
                for member in zf.namelist():
                    basename = os.path.basename(member)
                    if basename in ("ffmpeg", "ffprobe"):
                        data = zf.read(member)
                        dest = os.path.join(BIN_DIR, basename)
                        with open(dest, "wb") as f:
                            f.write(data)
                        os.chmod(dest, os.stat(dest).st_mode | stat.S_IEXEC)
        else:
            if "aarch64" in machine or "arm64" in machine:
                url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linuxarm64-gpl.tar.xz"
            else:
                url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"
            tmp_tar = os.path.join(APP_DIR, "ffmpeg_tmp.tar.xz")
            download_file(url, tmp_tar)
            import tarfile
            with tarfile.open(tmp_tar) as tf:
                for member in tf.getmembers():
                    basename = os.path.basename(member.name)
                    if basename in ("ffmpeg", "ffprobe"):
                        member.name = basename
                        tf.extract(member, BIN_DIR)
                        dest = os.path.join(BIN_DIR, basename)
                        os.chmod(dest, os.stat(dest).st_mode | stat.S_IEXEC)
            os.remove(tmp_tar)
    finally:
        if os.path.exists(tmp_zip):
            os.remove(tmp_zip)

    return path


def ensure_tools():
    ytdlp = fetch_ytdlp()
    ffmpeg_dir = os.path.dirname(fetch_ffmpeg())
    return ytdlp, ffmpeg_dir


def update_tools():
    send_message({"type": "progress", "data": "Updating yt-dlp..."})
    ytdlp = get_ytdlp_path()
    ffmpeg = get_ffmpeg_path()
    if os.path.exists(ytdlp):
        os.remove(ytdlp)
    if os.path.exists(ffmpeg):
        os.remove(ffmpeg)
        ffprobe = os.path.join(BIN_DIR, "ffprobe.exe" if platform.system() == "Windows" else "ffprobe")
        if os.path.exists(ffprobe):
            os.remove(ffprobe)
    return ensure_tools()


def get_format_args(fmt):
    if fmt == "audio":
        return ["-x", "--audio-format", "mp3"]
    elif fmt == "best":
        return ["-f", "bestvideo+bestaudio/best"]
    elif fmt in ("1080", "720", "480"):
        return ["-f", f"bestvideo[height<={fmt}]+bestaudio/best[height<={fmt}]"]
    return ["-f", "best"]


def handle_download(url, fmt, ytdlp_path, ffmpeg_dir):
    format_args = get_format_args(fmt)

    cmd = [
        ytdlp_path,
        *format_args,
        "--ffmpeg-location", ffmpeg_dir,
        "--newline",
        "-o", os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        url,
    ]

    if fmt != "audio":
        cmd.insert(len(format_args) + 1, "--merge-output-format")
        cmd.insert(len(format_args) + 2, "mp4")

    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = subprocess.CREATE_NO_WINDOW

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=creation_flags,
        )

        filename = ""
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue

            if "[download]" in line and "Destination:" in line:
                filename = line.split("Destination:")[-1].strip()
                filename = os.path.basename(filename)

            if "[download]" in line and "%" in line:
                send_message({"type": "progress", "data": line})
            elif "[Merger]" in line or "[ExtractAudio]" in line:
                send_message({"type": "progress", "data": line})

        proc.wait()

        if proc.returncode == 0:
            send_message({
                "type": "complete",
                "filename": filename or "download complete",
            })
        else:
            send_message({"type": "error", "error": f"yt-dlp exited with code {proc.returncode}"})

    except FileNotFoundError:
        send_message({"type": "error", "error": f"yt-dlp not found at {ytdlp_path}"})
    except Exception as e:
        send_message({"type": "error", "error": str(e)})


def handle_status():
    ytdlp_ok = os.path.exists(get_ytdlp_path())
    ffmpeg_ok = os.path.exists(get_ffmpeg_path())
    send_message({
        "type": "status",
        "ready": ytdlp_ok and ffmpeg_ok,
        "ytdlp": ytdlp_ok,
        "ffmpeg": ffmpeg_ok,
        "app_dir": APP_DIR,
        "download_dir": DOWNLOAD_DIR,
    })


def main():
    ytdlp_path = None
    ffmpeg_dir = None

    while True:
        message = read_message()
        if message is None:
            break

        action = message.get("action", "")

        if action == "download":
            try:
                if not ytdlp_path:
                    ytdlp_path, ffmpeg_dir = ensure_tools()
                handle_download(message.get("url", ""), message.get("format", "best"), ytdlp_path, ffmpeg_dir)
            except Exception as e:
                send_message({"type": "error", "error": str(e)})

        elif action == "status":
            handle_status()

        elif action == "update":
            try:
                ytdlp_path, ffmpeg_dir = update_tools()
                send_message({"type": "complete", "filename": "Tools updated successfully"})
            except Exception as e:
                send_message({"type": "error", "error": str(e)})


HOST_NAME = "yt_dlp_host"
EXTENSION_ID = "yt-dlp-dl@wakefield.fyi"


def is_interactive():
    if sys.platform == "win32":
        return sys.stdin is None or not hasattr(sys.stdin, "buffer") or sys.stdin.isatty()
    return sys.stdin.isatty()


def install():
    system = platform.system()
    exe_path = os.path.abspath(sys.argv[0])
    install_dir = get_app_data_dir()
    os.makedirs(install_dir, exist_ok=True)

    if system == "Windows":
        dest = os.path.join(install_dir, "host.exe")
    else:
        dest = os.path.join(install_dir, "host")

    if os.path.abspath(exe_path) != os.path.abspath(dest):
        shutil.copy2(exe_path, dest)
        if system != "Windows":
            os.chmod(dest, os.stat(dest).st_mode | stat.S_IEXEC)

    manifest = {
        "name": HOST_NAME,
        "description": "Native messaging host for yt-dlp downloads",
        "path": dest,
        "type": "stdio",
        "allowed_extensions": [EXTENSION_ID],
    }

    if system == "Windows":
        manifest_path = os.path.join(install_dir, f"{HOST_NAME}.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        import winreg
        key_path = f"SOFTWARE\\Mozilla\\NativeMessagingHosts\\{HOST_NAME}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, manifest_path)

        print("yt-dlp Extension - Native Host Installer")
        print("=" * 40)
        print(f"Installed to: {dest}")
        print(f"Registry key: HKCU\\{key_path}")
        print()
        print("Installation complete!")
        print("Restart Firefox for changes to take effect.")
        print()
        input("Press Enter to close...")

    elif system == "Darwin":
        manifest_dir = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Mozilla", "NativeMessagingHosts")
        os.makedirs(manifest_dir, exist_ok=True)
        manifest_path = os.path.join(manifest_dir, f"{HOST_NAME}.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"Installed to: {dest}")
        print(f"Manifest: {manifest_path}")
        print("\nInstallation complete! Restart Firefox.")

    else:
        manifest_dir = os.path.join(os.path.expanduser("~"), ".mozilla", "native-messaging-hosts")
        os.makedirs(manifest_dir, exist_ok=True)
        manifest_path = os.path.join(manifest_dir, f"{HOST_NAME}.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"Installed to: {dest}")
        print(f"Manifest: {manifest_path}")
        print("\nInstallation complete! Restart Firefox.")


if __name__ == "__main__":
    if is_interactive():
        install()
    else:
        main()
