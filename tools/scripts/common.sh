#!/usr/bin/env bash
# Common functions and variables for all vorbit workflow commands

# Derive paths from script location - works wherever user installs this
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$TOOLS_DIR")"
VORBIT_DIR="${VORBIT_DIR:-$PROJECT_ROOT/.vorbit}"
FEATURES_DIR="$VORBIT_DIR/features"

# Convert string to slug (lowercase, spaces to hyphens, remove special chars)
slugify() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[[:space:]]/-/g' | sed 's/[^a-z0-9-]//g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//'
}

# Get feature directory path
# Usage: get_feature_dir "feature-slug"
get_feature_dir() {
    local feature_slug="$1"
    [[ -z "$feature_slug" ]] && { echo "ERROR: Feature slug required" >&2; return 1; }
    echo "$FEATURES_DIR/$feature_slug"
}

# Get workflow state for a specific feature
# Usage: get_feature_state "feature-slug"
get_feature_state() {
    local feature_slug="$1"
    local feature_dir="$FEATURES_DIR/$feature_slug"

    if [[ -f "$feature_dir/tasks.md" ]]; then echo "tasks"
    elif [[ -f "$feature_dir/epic.md" ]]; then echo "epic"
    elif [[ -f "$feature_dir/prd.md" ]]; then echo "prd"
    elif [[ -f "$feature_dir/explore.md" ]]; then echo "explore"
    else echo "none"
    fi
}

# Usage: eval $(get_feature_paths "feature-slug")
# Sets all paths for a specific feature
get_feature_paths() {
    local feature_slug="$1"
    [[ -z "$feature_slug" ]] && { echo "echo 'ERROR: Feature slug required'" >&2; return 1; }

    local feature_dir="$FEATURES_DIR/$feature_slug"

    cat <<EOF
CURRENT_DIR='$(pwd)'
PROJECT_ROOT='$PROJECT_ROOT'
VORBIT_DIR='$VORBIT_DIR'
FEATURES_DIR='$FEATURES_DIR'
FEATURE_SLUG='$feature_slug'
FEATURE_DIR='$feature_dir'
LOGS_DIR='$VORBIT_DIR/logs'
SCRIPTS_DIR='$SCRIPT_DIR'
TOOLS_DIR='$TOOLS_DIR'
TEMPLATES_DIR='$TOOLS_DIR/templates'
EXPLORE_FILE='$feature_dir/explore.md'
PRD_FILE='$feature_dir/prd.md'
EPIC_FILE='$feature_dir/epic.md'
TASKS_FILE='$feature_dir/tasks.md'
EOF
}

# List all features with their states
# Usage: list_features
list_features() {
    [[ ! -d "$FEATURES_DIR" ]] && { echo "No features found"; return 0; }

    local count=0
    echo "Active Features:"
    echo "================"

    for feature_dir in "$FEATURES_DIR"/*/; do
        [[ ! -d "$feature_dir" ]] && continue

        local slug=$(basename "$feature_dir")
        local state=$(get_feature_state "$slug")
        local task_progress=""

        if [[ -f "$feature_dir/tasks.md" ]]; then
            local total completed
            total=$(grep -c "^### T[0-9]" "$feature_dir/tasks.md" 2>/dev/null) || total=0
            completed=$(grep -c "^### ✓ T[0-9]" "$feature_dir/tasks.md" 2>/dev/null) || completed=0
            task_progress=" ($completed/$total tasks)"
        fi

        count=$((count + 1))
        echo "$count. $slug"
        echo "   State: $state$task_progress"
        echo "   Path: $feature_dir"
        echo ""
    done

    [[ $count -eq 0 ]] && echo "No features found"
    echo "Total: $count feature(s)"
}

# Validation functions
check_file() { [[ -f "$1" ]] && echo "  ✓ $2" || echo "  ✗ $2"; }
check_dir() { [[ -d "$1" && -n $(ls -A "$1" 2>/dev/null) ]] && echo "  ✓ $2" || echo "  ✗ $2"; }

# Setup functions
ensure_workflow_dirs() {
    mkdir -p "$VORBIT_DIR/logs"
    mkdir -p "$FEATURES_DIR"
    echo "Workflow directories ready: $VORBIT_DIR"
}

ensure_feature_dir() {
    local feature_slug="$1"
    [[ -z "$feature_slug" ]] && { echo "ERROR: Feature slug required" >&2; return 1; }
    mkdir -p "$FEATURES_DIR/$feature_slug"
    mkdir -p "$VORBIT_DIR/logs"
}

# Utility functions
die() {
    echo "ERROR: $1" >&2
    exit 1
}

# Format timestamp for display (cross-platform: macOS + Linux)
format_timestamp() {
    local ts="$1"
    date -r "$ts" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || \
    date -d "@$ts" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || \
    echo "$ts"
}
