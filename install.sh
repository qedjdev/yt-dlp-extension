#!/bin/bash
set -e

APP_NAME="yt-dlp-extension"
HOST_NAME="yt_dlp_host"
EXTENSION_ID="yt-dlp-dl@wakefield.fyi"

case "$(uname -s)" in
    Darwin)
        INSTALL_DIR="$HOME/Library/Application Support/$APP_NAME"
        MANIFEST_DIR="$HOME/Library/Application Support/Mozilla/NativeMessagingHosts"
        ;;
    *)
        INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/$APP_NAME"
        MANIFEST_DIR="$HOME/.mozilla/native-messaging-hosts"
        ;;
esac

mkdir -p "$INSTALL_DIR"
mkdir -p "$MANIFEST_DIR"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Copy the frozen host executable
if [ -f "$SCRIPT_DIR/host" ]; then
    cp "$SCRIPT_DIR/host" "$INSTALL_DIR/host"
elif [ -f "$SCRIPT_DIR/dist/host" ]; then
    cp "$SCRIPT_DIR/dist/host" "$INSTALL_DIR/host"
else
    echo "Error: host executable not found. Build it first."
    exit 1
fi
chmod +x "$INSTALL_DIR/host"
echo "Installed host to: $INSTALL_DIR/host"

# Write native messaging host manifest
cat > "$MANIFEST_DIR/$HOST_NAME.json" <<EOF
{
  "name": "$HOST_NAME",
  "description": "Native messaging host for yt-dlp downloads",
  "path": "$INSTALL_DIR/host",
  "type": "stdio",
  "allowed_extensions": ["$EXTENSION_ID"]
}
EOF

echo "Wrote host manifest to: $MANIFEST_DIR/$HOST_NAME.json"
echo ""
echo "Installation complete! Restart Firefox for changes to take effect."
