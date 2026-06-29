# yt-dlp Extension for Firefox

A Firefox extension that adds a Download button directly to YouTube's video player interface. Pick a quality, click, and the video is saved to your Downloads folder.

Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [ffmpeg](https://ffmpeg.org/).

## Features

- Download button injected next to YouTube's native Share/Save buttons
- Quality selection: Best, 1080p, 720p, 480p, or Audio Only (MP3)
- Real-time download progress shown inline
- yt-dlp and ffmpeg are automatically downloaded on first use and kept up to date
- No Python or other dependencies required — the native host is a standalone executable

## Installation

### 1. Install the extension

Install from [Firefox Add-ons](https://addons.mozilla.org/) (link TBD), or load it manually:

1. Go to `about:debugging#/runtime/this-firefox`
2. Click **Load Temporary Add-on**
3. Select `extension/manifest.json`

### 2. Install the native host

The extension needs a small helper app to run yt-dlp on your computer. When you click Download for the first time, the extension will open a setup page with instructions.

**Windows:**

Download and run the installer from the [latest release](https://github.com/user/yt-dlp-extension/releases/latest), or run the PowerShell installer:

```powershell
.\install.ps1
```

**macOS / Linux:**

```bash
./install.sh
```

### 3. Restart Firefox

Close and reopen Firefox so it detects the native host.

## Building from source

### Extension

No build step needed — the `extension/` directory is the extension.

### Native host

The native host must be compiled into a standalone executable so users don't need Python installed.

```bash
pip install pyinstaller
python build.py
```

The output is `dist/host.exe` (Windows) or `dist/host` (macOS/Linux). PyInstaller does not cross-compile — you need to build on each target OS, or use CI.

## How it works

```
[YouTube page] → [Firefox extension] → [Native messaging] → [host.exe] → [yt-dlp]
```

The extension injects a Download button into YouTube's UI. When you pick a quality, it sends the video URL to the native messaging host via Firefox's [Native Messaging API](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging). The host runs yt-dlp, streams progress back to the extension, and saves the file to your Downloads folder.

On first use, the host automatically downloads the latest yt-dlp and ffmpeg binaries from their official GitHub releases into a local application data directory.

## Project structure

```
yt-dlp-extension/
├── extension/              # Firefox extension
│   ├── manifest.json
│   ├── background.js       # Bridges extension ↔ native host
│   ├── content.js          # Injects download button on YouTube
│   ├── content.css
│   ├── setup.html          # Setup page shown when host is missing
│   ├── setup.js
│   └── icons/
├── native-host/
│   ├── host.py             # Native messaging host (auto-fetches yt-dlp + ffmpeg)
│   ├── install.py          # Cross-platform installer (Python)
│   └── yt_dlp_host.json    # Host manifest template
├── install.ps1             # Windows installer script
├── install.sh              # macOS/Linux installer script
├── build.py                # PyInstaller build script
└── dist/
    └── host.exe            # Compiled native host (Windows)
```

## Legal

**The tool itself is legal.** In 2020, the RIAA attempted to take down youtube-dl (the project yt-dlp is forked from) via a DMCA claim. The [Electronic Frontier Foundation](https://www.eff.org/deeplinks/2020/11/github-reinstates-youtube-dl-after-riaas-abuse-dmca) successfully argued that the tool does not circumvent any digital protections. GitHub reinstated the project and established a $1M developer defense fund.

**It does violate YouTube's Terms of Service.** YouTube's ToS prohibit accessing content through means other than the video player or explicitly authorized methods like YouTube Premium. Violating ToS is a breach of contract, not a criminal offense. The realistic consequence is account termination, though enforcement against individual users is extremely rare.

**What you download matters.** Downloading copyrighted content without permission is copyright infringement regardless of the tool used. This extension is a neutral tool — how you use it is your responsibility.

## License

MIT
