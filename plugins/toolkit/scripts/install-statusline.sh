#!/bin/bash
# ABOUTME: Installer for Claude Code status line showing model, context %, and short path
# ABOUTME: Creates statusline-pipe.sh and configures settings.json

set -euo pipefail

CLAUDE_DIR="${HOME}/.claude"
SCRIPT_PATH="${CLAUDE_DIR}/statusline-pipe.sh"
SETTINGS_PATH="${CLAUDE_DIR}/settings.json"

# Ensure ~/.claude exists
mkdir -p "$CLAUDE_DIR"

# Check for jq dependency
if ! command -v jq &>/dev/null; then
  echo "Error: jq is required. Install with: brew install jq"
  exit 1
fi

# Write the statusline script
cat > "$SCRIPT_PATH" << 'STATUSLINE'
#!/bin/bash

# ABOUTME: Clean pipe-separated statusline with model, color-coded percentage, and short path
# ABOUTME: Output format: opus | 67% | Github-Work/commander

# Read JSON input from stdin
input=$(cat)

# Extract model, workspace, and transcript info
model="$(echo "$input" | jq -r '.model.display_name' | tr '[:upper:]' '[:lower:]')"
workdir="$(echo "$input" | jq -r '.workspace.current_dir')"
transcript_path="$(echo "$input" | jq -r '.transcript_path // empty')"

# Read context window size from Claude Code input (default 200K)
context_size=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')

# Get last 2 path components for short display
parent=$(basename "$(dirname "$workdir")")
current=$(basename "$workdir")
short_path="${parent}/${current}"

# Calculate context usage percentage from transcript file
context_percent=0
if [ -f "$transcript_path" ]; then
  # Extract last assistant message and sum all token counts
  last_msg=$(tail -50 "$transcript_path" | grep '"type":"assistant"' | tail -1)
  if [ -n "$last_msg" ]; then
    input_tokens=$(echo "$last_msg" | jq -r '.message.usage.input_tokens // 0' 2>/dev/null || echo 0)
    cache_read=$(echo "$last_msg" | jq -r '.message.usage.cache_read_input_tokens // 0' 2>/dev/null || echo 0)
    cache_creation=$(echo "$last_msg" | jq -r '.message.usage.cache_creation_input_tokens // 0' 2>/dev/null || echo 0)

    output_tokens=$(echo "$last_msg" | jq -r '.message.usage.output_tokens // 0' 2>/dev/null || echo 0)

    # Calculate percentage of actual context window
    # Sum all token types (input, output, cached reads, and cache creation) for accurate total
    # Scale overhead proportionally (16% of window)
    overhead=$((context_size * 16 / 100))
    total_tokens=$((input_tokens + output_tokens + cache_read + cache_creation))
    context_percent=$((total_tokens * 100 / (context_size - overhead)))
    [ $context_percent -gt 100 ] && context_percent=100
  fi
fi

# Determine color based on context threshold (gray → green → yellow → red)
if [ $context_percent -ge 95 ]; then
  color="\033[1;91m"  # Bright red (bold)
elif [ $context_percent -ge 80 ]; then
  color="\033[91m"    # Red
elif [ $context_percent -ge 60 ]; then
  color="\033[33m"    # Yellow
elif [ $context_percent -ge 40 ]; then
  color="\033[32m"    # Green
else
  color="\033[90m"    # Dark gray
fi

# Color definitions
reset="\033[0m"
dim="\033[90m"
model_color="\033[1;38;5;208m"

# Output: model | percentage | path
printf "${model_color}%s${reset} ${dim}|${reset} ${color}%d%%${reset} ${dim}|${reset} ${dim}%s${reset}" \
  "$model" "$context_percent" "$short_path"
STATUSLINE

chmod +x "$SCRIPT_PATH"

# Configure settings.json
if [ -f "$SETTINGS_PATH" ]; then
  # Check if statusLine is already configured
  existing=$(jq -r '.statusLine.command // empty' "$SETTINGS_PATH" 2>/dev/null)
  if [ "$existing" = "$SCRIPT_PATH" ]; then
    echo "Status line already configured in settings.json"
  else
    # Add/update statusLine entry
    tmp=$(mktemp)
    jq --arg cmd "$SCRIPT_PATH" '.statusLine = {"type": "command", "command": $cmd}' "$SETTINGS_PATH" > "$tmp"
    mv "$tmp" "$SETTINGS_PATH"
    echo "Updated settings.json with statusLine config"
  fi
else
  # Create minimal settings.json
  cat > "$SETTINGS_PATH" << EOF
{
  "statusLine": {
    "type": "command",
    "command": "$SCRIPT_PATH"
  }
}
EOF
  echo "Created settings.json with statusLine config"
fi

echo "Installed: $SCRIPT_PATH"
echo "Status line will appear on next Claude Code session."
