#!/bin/bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="${TARGET_DIR:-/usr/local/bin}"
TARGET_BIN="$TARGET_DIR/agent-viewer"

mkdir -p "$TARGET_DIR"
cat > "$TARGET_BIN" <<EOF
#!/bin/bash
REPO_DIR="$REPO_DIR"
exec node "\$REPO_DIR/bin/agent-viewer.js" "\$@"
EOF
chmod +x "$TARGET_BIN"

echo "Installed agent-viewer to $TARGET_BIN"
echo "Try: agent-viewer --help"
echo
echo "Tip: for open-source usage, prefer npm link during development or npm install -g after publishing."
