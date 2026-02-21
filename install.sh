#!/bin/bash

# ABOUTME: Toolkit Installation Script
# ABOUTME: Installs Toolkit plugin from GitHub repository to ~/.toolkit

set -e

# Repository configuration
REPO_URL="https://github.com/ruizrica/toolkit"
TOOLKIT_VERSION="1.0.2"

# Installation paths
BASE_DIR="$HOME/.toolkit"
SLASH_COMMANDS_DIR="$HOME/.claude/slash_commands"
CONFIG_FILE="$HOME/.toolkit-config.yml"
TEMP_DIR=$(mktemp -d)

# -----------------------------------------------------------------------------
# Color Definitions
# -----------------------------------------------------------------------------

RED='\033[38;2;255;32;86m'
GREEN='\033[38;2;0;234;179m'
YELLOW='\033[38;2;255;185;0m'
BLUE='\033[38;2;0;208;255m'
PURPLE='\033[38;2;142;81;255m'
NC='\033[0m' # No Color

# -----------------------------------------------------------------------------
# Output Functions
# -----------------------------------------------------------------------------

print_color() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

print_section() {
    echo ""
    if command -v gum &> /dev/null; then
        gum style --foreground 12 --border double --border-foreground 12 --align center --width 60 --padding "1 2" "$1" 2>/dev/null || print_color "$BLUE" "=== $1 ==="
    else
        print_color "$BLUE" "=== $1 ==="
    fi
    echo ""
}

print_status() {
    if command -v gum &> /dev/null; then
        gum style --foreground 12 "$1" 2>/dev/null || print_color "$BLUE" "$1"
    else
        print_color "$BLUE" "$1"
    fi
}

print_success() {
    if command -v gum &> /dev/null; then
        gum style --foreground 10 "✓ $1" 2>/dev/null || print_color "$GREEN" "✓ $1"
    else
        print_color "$GREEN" "✓ $1"
    fi
}

print_warning() {
    if command -v gum &> /dev/null; then
        gum style --foreground 11 "⚠️  $1" 2>/dev/null || print_color "$YELLOW" "⚠️  $1"
    else
        print_color "$YELLOW" "⚠️  $1"
    fi
}

print_error() {
    if command -v gum &> /dev/null; then
        gum style --foreground 9 "✗ $1" 2>/dev/null || print_color "$RED" "✗ $1"
    else
        print_color "$RED" "✗ $1"
    fi
}

print_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        if command -v gum &> /dev/null; then
            gum log --level debug "$1" 2>/dev/null || echo "[VERBOSE] $1" >&2
        else
            echo "[VERBOSE] $1" >&2
        fi
    fi
}

# Confirmation prompt with fallback
confirm_prompt() {
    local message="$1"
    local default="${2:-true}"

    if command -v gum &> /dev/null; then
        if [[ "$default" == "true" ]]; then
            gum confirm "$message" --selected.background="33" --selected.foreground="15" --default=true
        else
            gum confirm "$message" --selected.background="33" --selected.foreground="15" --default=false
        fi
        return $?
    else
        local prompt_text="$message"
        if [[ "$default" == "true" ]]; then
            prompt_text="$prompt_text [Y/n] "
        else
            prompt_text="$prompt_text [y/N] "
        fi

        read -r -p "$prompt_text" response
        case "${response}" in
            [yY][eE][sS]|[yY])
                return 0
                ;;
            [nN][oO]|[nN])
                return 1
                ;;
            "")
                [[ "$default" == "true" ]] && return 0 || return 1
                ;;
            *)
                [[ "$default" == "true" ]] && return 0 || return 1
                ;;
        esac
    fi
}

# -----------------------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------------------

cleanup() {
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
    tput cnorm 2>/dev/null || true
}
trap cleanup EXIT

# -----------------------------------------------------------------------------
# Prerequisite Checks
# -----------------------------------------------------------------------------

check_prerequisites() {
    local failed=0

    # Check for git
    if ! command -v git &> /dev/null; then
        print_error "git not found"
        ((failed++))
    fi

    # Check for Python 3.8+
    local python_ok=false
    for cmd in python3 python; do
        if command -v "$cmd" &> /dev/null; then
            local version=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "0.0")
            local major=$(echo "$version" | cut -d. -f1)
            local minor=$(echo "$version" | cut -d. -f2)
            if (( major >= 3 && minor >= 8 )); then
                python_ok=true
                break
            fi
        fi
    done
    if [[ "$python_ok" != "true" ]]; then
        print_error "Python 3.8+ not found"
        ((failed++))
    fi

    # Check for Claude Code CLI
    if ! command -v claude &> /dev/null; then
        print_error "Claude Code CLI not found (https://claude.ai/code)"
        ((failed++))
    fi

    if (( failed > 0 )); then
        exit 1
    fi
    echo "✓ Prerequisites: git, python, claude"
}

# -----------------------------------------------------------------------------
# Installation Functions
# -----------------------------------------------------------------------------

clone_repository() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "✓ Would clone to ~/.toolkit"
        return 0
    fi

    if [[ -d "$BASE_DIR/.git" ]]; then
        if ! (cd "$BASE_DIR" && git pull --ff-only 2>/dev/null); then
            echo "⚠ git pull failed in $BASE_DIR (may need manual update)"
        fi
    else
        rm -rf "$BASE_DIR" 2>/dev/null || true
        git clone --quiet "$REPO_URL" "$BASE_DIR" 2>/dev/null
    fi
    echo "✓ Cloned to ~/.toolkit"
}

register_plugin() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "✓ Would register plugin"
        return 0
    fi

    claude plugins remove toolkit 2>/dev/null || true
    local add_output
    if add_output=$(claude plugins add "$BASE_DIR/plugins/toolkit" 2>&1); then
        echo "✓ Plugin registered"
    else
        print_error "Plugin registration failed: $add_output"
        print_warning "Manual fix: claude plugins add ~/.toolkit/plugins/toolkit"
    fi
}

install_python_scripts() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "✓ Would install scripts"
        return 0
    fi

    mkdir -p "$SLASH_COMMANDS_DIR"
    cp "$BASE_DIR/plugins/toolkit/scripts/"*.py "$SLASH_COMMANDS_DIR/" 2>/dev/null || true
    echo "✓ Scripts installed"
}

# -----------------------------------------------------------------------------
# Required Tools
# -----------------------------------------------------------------------------

install_agent_browser() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "✓ Would install agent-browser"
        return 0
    fi

    if command -v agent-browser &> /dev/null; then
        echo "✓ agent-browser ready"
        return 0
    fi

    if command -v npm &> /dev/null; then
        npm install -g agent-browser 2>/dev/null && echo "✓ agent-browser installed" || print_warning "Run: npm install -g agent-browser"
    else
        print_warning "Run: npm install -g agent-browser"
    fi
}

install_just_bash() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "✓ Would install just-bash"
        return 0
    fi

    if command -v just-bash &> /dev/null; then
        echo "✓ just-bash ready"
        return 0
    fi

    if command -v npm &> /dev/null; then
        npm install -g just-bash 2>/dev/null && echo "✓ just-bash installed" || print_warning "Run: npm install -g just-bash"
    else
        print_warning "Run: npm install -g just-bash"
    fi
}

install_agent_memory() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "✓ Would install agent-memory"
        return 0
    fi

    if command -v pip3 &> /dev/null; then
        pip3 install --break-system-packages -e "$BASE_DIR/tools/agent-memory" 2>/dev/null && \
            echo "✓ agent-memory installed" || \
            print_warning "Run: pip3 install --break-system-packages -e ~/.toolkit/tools/agent-memory"
    else
        print_warning "pip3 not found. Run: pip3 install --break-system-packages -e ~/.toolkit/tools/agent-memory"
    fi
}

install_memory_dirs() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "✓ Would create memory directories"
        return 0
    fi

    mkdir -p "$HOME/.claude/agent-memory/daily-logs"
    mkdir -p "$HOME/.claude/agent-memory/sessions"
    mkdir -p "$HOME/.claude/agent-memory/procedures"
    echo "✓ Memory directories created"
}

install_skills() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "✓ Would install skill files"
        return 0
    fi

    local skills_src="$BASE_DIR/plugins/toolkit/skills"
    local skills_dst="$HOME/.claude/skills"

    if [[ -d "$skills_src" ]]; then
        mkdir -p "$skills_dst"
        cp "$skills_src/"*.md "$skills_dst/" 2>/dev/null || true
        echo "✓ Skills installed"
    fi
}

install_statusline() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "✓ Would install statusline"
        return 0
    fi

    bash "$BASE_DIR/plugins/toolkit/scripts/install-statusline.sh"
    echo "✓ Statusline installed"
}

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

install_env() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "✓ Would install .env file"
        return 0
    fi

    local env_src="$BASE_DIR/.env"
    local env_dst="$PWD/.env"

    if [[ -f "$env_src" ]]; then
        if [[ -f "$env_dst" ]]; then
            print_status "Appending .env template to existing local .env..."
            echo "" >> "$env_dst"
            echo "# Added by agent-toolkit installer" >> "$env_dst"
            cat "$env_src" >> "$env_dst"
            echo "✓ .env template appended"
        else
            print_status "Copying .env template..."
            cp "$env_src" "$env_dst"
            echo "✓ .env template copied"
        fi
    fi
}

install_claude_md() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "✓ Would install CLAUDE.md file"
        return 0
    fi

    local claude_src="$BASE_DIR/CLAUDE.md"
    local claude_dst="$PWD/CLAUDE.md"
    if [[ -f "$PWD/claude.md" ]]; then
        claude_dst="$PWD/claude.md"
    elif [[ -f "$PWD/Claude.md" ]]; then
        claude_dst="$PWD/Claude.md"
    fi

    if [[ -f "$claude_src" ]]; then
        if [[ -f "$claude_dst" ]]; then
            if ! grep -q "Toolkit Commands" "$claude_dst"; then
                print_status "Appending CLAUDE.md template to existing local file..."
                echo "" >> "$claude_dst"
                echo "" >> "$claude_dst"
                echo "---" >> "$claude_dst"
                echo "" >> "$claude_dst"
                echo "# Added by agent-toolkit installer" >> "$claude_dst"
                cat "$claude_src" >> "$claude_dst"
                echo "✓ CLAUDE.md template appended"
            fi
        else
            print_status "Copying CLAUDE.md template..."
            cp "$claude_src" "$claude_dst"
            echo "✓ CLAUDE.md template copied"
        fi
    fi
}

save_config() {
    if [[ "$DRY_RUN" == "true" ]]; then
        return 0
    fi

    cat > "$CONFIG_FILE" << EOF
# Toolkit configuration
version: "$TOOLKIT_VERSION"
install_path: "$BASE_DIR"
installed_at: "$(date '+%Y-%m-%d %H:%M:%S')"
EOF
}

# -----------------------------------------------------------------------------
# Uninstall
# -----------------------------------------------------------------------------

perform_uninstall() {
    print_section "Toolkit Uninstall"

    # Remove plugin registration
    print_status "Removing plugin registration..."
    claude plugins remove toolkit 2>/dev/null || true
    echo "✓ Plugin unregistered"
    echo ""

    # Remove Python scripts
    print_status "Removing Python scripts..."
    rm -f "$SLASH_COMMANDS_DIR/handbook.py" 2>/dev/null
    rm -f "$SLASH_COMMANDS_DIR/rlm_repl.py" 2>/dev/null
    echo "✓ Python scripts removed"
    echo ""

    # Remove statusline
    print_status "Removing statusline..."
    rm -f "$HOME/.claude/statusline-pipe.sh" 2>/dev/null
    if command -v jq &>/dev/null && [[ -f "$HOME/.claude/settings.json" ]]; then
        tmp=$(mktemp)
        jq 'del(.statusLine)' "$HOME/.claude/settings.json" > "$tmp" && mv "$tmp" "$HOME/.claude/settings.json"
    fi
    echo "✓ Statusline removed"
    echo ""

    # Remove skill files
    print_status "Removing skill files..."
    rm -f "$HOME/.claude/skills/just-bash.md" 2>/dev/null
    rm -f "$HOME/.claude/skills/agent-memory.md" 2>/dev/null
    echo "✓ Skill files removed"
    echo ""

    # Remove repository
    if [[ -d "$BASE_DIR" ]]; then
        if confirm_prompt "Remove repository at $BASE_DIR?" true; then
            rm -rf "$BASE_DIR"
            echo "✓ Repository removed"
        else
            echo "  Repository kept at $BASE_DIR"
        fi
    fi
    echo ""

    # Remove config
    rm -f "$CONFIG_FILE" 2>/dev/null

    print_success "Toolkit has been uninstalled"
}

# -----------------------------------------------------------------------------
# Main Execution
# -----------------------------------------------------------------------------

VERBOSE=false
DRY_RUN=false
UNINSTALL=false
REFRESH=false

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --uninstall)
                UNINSTALL=true
                shift
                ;;
            --refresh)
                REFRESH=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  -v, --verbose    Show verbose output"
                echo "  --dry-run        Preview without making changes"
                echo "  --uninstall      Remove Toolkit"
                echo "  --refresh        Re-register plugin and skills (after git pull)"
                echo "  -h, --help       Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use -h or --help for usage information"
                exit 1
                ;;
        esac
    done

    # Handle uninstall
    if [[ "$UNINSTALL" == "true" ]]; then
        perform_uninstall
        exit 0
    fi

    # Handle refresh
    if [[ "$REFRESH" == "true" ]]; then
        print_section "Refreshing Plugin"
        register_plugin
        install_skills
        print_success "Plugin refreshed!"
        exit 0
    fi

    # Clear screen and show header
    clear

    # Print logo (Dodger Blue 2)
    local LOGO_COLOR='\033[38;2;28;134;238m'
    echo ""
    print_color "$LOGO_COLOR" " ▄▄                   ▄▄▄▄   ▄▄       ██    ▄▄"
    print_color "$LOGO_COLOR" "▄██▄▄▄ ▄████▄  ▄████▄ ▀▀██   ██ ▄██  ▄▄▄   ▄██▄▄▄"
    print_color "$LOGO_COLOR" "▀██▀▀▀ ██  ██  ██  ██   ██   ████▀   ▀██   ▀██▀▀▀"
    print_color "$LOGO_COLOR" " ██▄▄▄ ██▄▄██  ██▄▄██ ▄▄██▄▄ ██▀██▄ ▄▄██▄▄  ██▄▄▄"
    print_color "$LOGO_COLOR" "  ▀▀▀▀  ▀▀▀▀    ▀▀▀▀  ▀▀▀▀▀▀ ▀▀  ▀▀ ▀▀▀▀▀▀   ▀▀▀▀"
    echo ""

    # Description
    echo "A Claude Code plugin with commands, agents, and scripts to optimize developer workflows."
    echo -e "${YELLOW}Commands:${NC} /team /review /haiku /handbook /gherkin /rlm"
    echo -e "${YELLOW}Agents:${NC} gemini, cursor, codex, qwen, opencode, groq, crush, droid"

    print_section "Installation"

    if [[ "$DRY_RUN" == "true" ]]; then
        print_warning "DRY RUN MODE - No changes will be made"
        echo ""
    fi

    # Check for curl
    if ! command -v curl &> /dev/null; then
        print_error "curl is required but not installed"
        exit 1
    fi

    check_prerequisites
    clone_repository
    register_plugin
    install_python_scripts
    install_statusline
    install_skills
    install_memory_dirs
    install_agent_browser
    install_just_bash
    install_agent_memory
    install_env
    install_claude_md
    save_config

    echo ""
    print_success "Toolkit installed!"
    echo -e "Run ${YELLOW}claude${NC} then try ${YELLOW}/team \"hello\"${NC}"
}

main "$@"
