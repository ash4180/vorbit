#!/usr/bin/env bash
# Unified task management - generate, progress, lifecycle

set -euo pipefail

# Source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# =============================================================================
# TASK GENERATION 
# =============================================================================

substitute_placeholder() {
    local content="$1"
    local placeholder="$2"
    local value="$3"
    echo "${content//\[$placeholder\]/$value}"
}

# Read task format from template 
get_task_format() {
    local template_file="$TOOLS_DIR/templates/tasks-template.md"
    sed -n '/^### \[TASK_ID\]/,/^\*\*Test\*\*:/p' "$template_file" | head -7
}

generate_task_entry() {
    local task_id="$1"
    local task_name="$2"
    local parallel_marker="$3"
    local story_id="$4"
    local file_path="$5"
    local task_type="$6"
    local dependencies="$7"
    local task_desc="$8"
    local task_test="$9"

    # Read format from template
    local format
    format=$(get_task_format)

    # Substitute all placeholders
    format=$(substitute_placeholder "$format" "TASK_ID" "$task_id")
    format=$(substitute_placeholder "$format" "PARALLEL" "$parallel_marker")
    format=$(substitute_placeholder "$format" "TASK_NAME" "$task_name")
    format=$(substitute_placeholder "$format" "STORY_ID" "$story_id")
    format=$(substitute_placeholder "$format" "FILE_PATH" "$file_path")
    format=$(substitute_placeholder "$format" "TASK_TYPE" "$task_type")
    format=$(substitute_placeholder "$format" "DEPENDENCIES" "$dependencies")
    format=$(substitute_placeholder "$format" "TASK_DESC" "$task_desc")
    format=$(substitute_placeholder "$format" "TASK_TEST" "$task_test")

    # Leading newline becomes separator; trailing stripped by $() anyway
    echo ""
    echo "$format"
}

# Detect project type from config files
# Returns: jest|vitest|mocha|pytest|go|cargo|unknown
detect_project_type() {
    local search_dir="${1:-.}"

    # JavaScript/TypeScript
    if [[ -f "$search_dir/package.json" ]]; then
        local pkg_content=$(cat "$search_dir/package.json" 2>/dev/null)
        if echo "$pkg_content" | grep -q '"vitest"'; then
            echo "vitest"; return
        elif echo "$pkg_content" | grep -q '"jest"'; then
            echo "jest"; return
        elif echo "$pkg_content" | grep -q '"mocha"'; then
            echo "mocha"; return
        fi
        echo "jest"  # Default for JS projects
        return
    fi

    # Python
    if [[ -f "$search_dir/pytest.ini" ]] || [[ -f "$search_dir/pyproject.toml" ]] || [[ -f "$search_dir/setup.py" ]]; then
        echo "pytest"; return
    fi

    # Go
    if [[ -f "$search_dir/go.mod" ]]; then
        echo "go"; return
    fi

    # Rust
    if [[ -f "$search_dir/Cargo.toml" ]]; then
        echo "cargo"; return
    fi

    echo "unknown"
}

# Generate test scaffold file for a task
# Usage: generate_test_scaffold <project_type> <output_dir> <task_id> <story_name> <acceptance_criteria>
generate_test_scaffold() {
    local project_type="$1"
    local output_dir="$2"
    local task_id="$3"
    local story_name="$4"
    local acceptance="${5:-Verify functionality works}"

    local test_dir="$output_dir/tests"
    mkdir -p "$test_dir"

    local test_file=""
    local test_content=""

    case "$project_type" in
        jest|vitest)
            test_file="$test_dir/${task_id}.test.ts"
            test_content="// Test: $story_name

describe('$story_name', () => {
  it.todo('$acceptance');
});
"
            ;;
        mocha)
            test_file="$test_dir/${task_id}.test.js"
            test_content="// Test: $story_name

describe('$story_name', () => {
  it.skip('$acceptance', () => {
    // Implement: $acceptance
  });
});
"
            ;;
        pytest)
            test_file="$test_dir/test_${task_id}.py"
            test_content="\"\"\"Test: $story_name\"\"\"
import pytest

@pytest.mark.skip(reason='Not implemented: $acceptance')
def test_${task_id}_acceptance():
    \"\"\"$acceptance\"\"\"
    pass
"
            ;;
        go)
            test_file="$test_dir/${task_id}_test.go"
            test_content="package tests

import \"testing\"

// Test: $story_name
func Test${task_id}Acceptance(t *testing.T) {
	t.Skip(\"Not implemented: $acceptance\")
}
"
            ;;
        cargo)
            test_file="$test_dir/${task_id}_test.rs"
            test_content="// Test: $story_name

#[cfg(test)]
mod tests {
    #[test]
    #[ignore = \"Not implemented: $acceptance\"]
    fn test_${task_id}_acceptance() {
    }
}
"
            ;;
        *)
            test_file="$test_dir/${task_id}_test.sh"
            test_content="#!/usr/bin/env bash
# Test: $story_name
# Acceptance: $acceptance
set -e

echo \"SKIP: $task_id - Not implemented\"
echo \"Expected: $acceptance\"
exit 0
"
            ;;
    esac

    # Only create if doesn't exist
    if [[ ! -f "$test_file" ]]; then
        echo "$test_content" > "$test_file"
        echo "$test_file"
    fi
}

# Generate tasks.md from epic.md
# Usage: cmd_generate <epic_file> [output_dir]
cmd_generate() {
    local epic_file="$1"
    local output_dir="${2:-}"

    [[ ! -f "$epic_file" ]] && die "Epic file not found: $epic_file"

    # If no output_dir, use epic file's directory
    [[ -z "$output_dir" ]] && output_dir=$(dirname "$epic_file")
    mkdir -p "$output_dir"

    # Extract epic name
    local epic_name=$(grep "^# EPIC:" "$epic_file" | sed 's/^# EPIC: //' | head -1)
    [[ -z "$epic_name" ]] && die "No epic name found in $epic_file"

    local output_file="$output_dir/tasks.md"
    local template_file="$TOOLS_DIR/templates/tasks-template.md"

    [[ ! -f "$template_file" ]] && die "Template not found: $template_file"

    # Detect project type for test scaffolds
    local project_type=$(detect_project_type "$PROJECT_ROOT")

    echo "Parsing epic: $epic_name"
    echo "Project type: $project_type"
    echo "Generating TDD task pairs from User Stories..."

    # Read template sections
    local header=$(sed -n '1,/^## Task Format$/p' "$template_file" | sed '$d')
    local footer=$(sed -n '/^## Progress Tracking/,$p' "$template_file")

    local task_count=0
    local test_tasks=0
    local impl_tasks=0
    local tasks_content=""

    # Parse User Stories (format: ### S-001: Story Name)
    local story_num=0
    while IFS= read -r line; do
        if [[ "$line" =~ ^###[[:space:]]S-([0-9]+):[[:space:]]*(.*) ]]; then
            story_num=$((story_num + 1))
            local story_id="S-${BASH_REMATCH[1]}"
            local story_name="${BASH_REMATCH[2]}"
            local task_num=$(printf "%03d" $story_num)

            # Extract acceptance criteria
            local story_line=$(grep -n "^### $story_id:" "$epic_file" | cut -d: -f1)
            local acceptance=""
            if [[ -n "$story_line" ]]; then
                acceptance=$(sed -n "${story_line},/^###/p" "$epic_file" | grep -A1 "Acceptance Criteria" | tail -1 | sed 's/^[0-9]*\. //')
            fi
            [[ -z "$acceptance" ]] && acceptance="Verify $story_name works correctly"

            # Generate test task (T001a)
            local test_file=$(generate_test_scaffold "$project_type" "$output_dir" "T${task_num}a" "$story_name" "$acceptance")
            local test_path="tests/"
            [[ -n "$test_file" ]] && test_path=$(basename "$test_file")

            tasks_content+=$(generate_task_entry "T${task_num}a" "Write tests for $story_name" "[P] " "$story_id" "$test_path" "Test" "None" "Write unit tests for $story_name" "$acceptance")$'\n'
            test_tasks=$((test_tasks + 1))
            task_count=$((task_count + 1))

            # Generate implementation task (T001b)
            tasks_content+=$(generate_task_entry "T${task_num}b" "Implement $story_name" "" "$story_id" "src/" "Implementation" "T${task_num}a" "Implement functionality for $story_name" "All T${task_num}a tests pass")$'\n'
            impl_tasks=$((impl_tasks + 1))
            task_count=$((task_count + 1))
        fi
    done < "$epic_file"

    [[ $story_num -eq 0 ]] && die "No User Stories found in $epic_file (expected format: ### S-001: Story Name)"

    # Substitute header placeholders
    header=$(substitute_placeholder "$header" "FEATURE_NAME" "$epic_name")
    header=$(substitute_placeholder "$header" "DATE" "$(date +%Y-%m-%d)")
    header=$(substitute_placeholder "$header" "EPIC_FILE" "$epic_file")
    header=$(substitute_placeholder "$header" "EPIC_TYPE" "TDD Implementation")
    header=$(substitute_placeholder "$header" "DESCRIPTION" "Test-first task pairs generated from User Stories")

    # Substitute footer placeholders
    footer=$(substitute_placeholder "$footer" "SETUP_COUNT" "0")
    footer=$(substitute_placeholder "$footer" "IMPL_COUNT" "$impl_tasks")
    footer=$(substitute_placeholder "$footer" "TEST_COUNT" "$test_tasks")
    footer=$(substitute_placeholder "$footer" "TASK_COUNT" "$task_count")

    # Write output
    echo "$header" > "$output_file"
    echo "$tasks_content" >> "$output_file"
    echo "" >> "$output_file"
    echo "$footer" >> "$output_file"

    # Update epic Phase 3 immediately
    update_epic_phase3 "$epic_file"

    # Report test scaffolds
    local scaffold_count=$(find "$output_dir/tests" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "Generated: $output_file ($task_count tasks from $story_num stories)"
    [[ "$scaffold_count" -gt 0 ]] && echo "Test scaffolds: $output_dir/tests/ ($scaffold_count files)"
    return 0
}

# Generate tasks from conversation text
# Usage: cmd_generate_conversation <conversation_text> <output_dir>
cmd_generate_conversation() {
    local conversation_text="$1"
    local output_dir="$2"

    [[ -z "$conversation_text" ]] && die "Conversation text required"
    [[ -z "$output_dir" ]] && die "Output directory required for conversation tasks"

    mkdir -p "$output_dir"

    local output_file="$output_dir/tasks.md"
    local template_file="$TOOLS_DIR/templates/tasks-template.md"
    local feature_name="Conversation Tasks"

    [[ ! -f "$template_file" ]] && die "Template not found: $template_file"

    echo "Parsing conversation input..."
    echo "Generating tasks.md from conversation..."

    local header=$(sed -n '/^## Task Format$/,/^## /p' "$template_file" | sed '$d')
    local footer=$(sed -n '/^## Progress Tracking/,$p' "$template_file")

    local task_count=0
    local tasks_content=""

    local tmp_file=$(mktemp)
    echo "$conversation_text" | grep -iE "(create|build|implement|add|fix|update|modify)" | head -5 > "$tmp_file"

    while IFS= read -r action; do
        task_count=$((task_count + 1))
        local task_id="T$(printf "%03d" $task_count)"
        local short_desc=$(echo "$action" | cut -c1-50)
        tasks_content+=$(generate_task_entry "$task_id" "$short_desc" "[P] " "S-000" "to-be-determined" "Implementation" "None" "$action" "Verify implementation works")
    done < "$tmp_file"
    rm -f "$tmp_file"

    header=$(substitute_placeholder "$header" "FEATURE_NAME" "$feature_name")
    header=$(substitute_placeholder "$header" "DATE" "$(date +%Y-%m-%d)")
    header=$(substitute_placeholder "$header" "EPIC_FILE" "Conversation Input")
    header=$(substitute_placeholder "$header" "EPIC_TYPE" "Ad-hoc")
    header=$(substitute_placeholder "$header" "DESCRIPTION" "Tasks generated from conversation requirements")

    footer=$(substitute_placeholder "$footer" "SETUP_COUNT" "0")
    footer=$(substitute_placeholder "$footer" "IMPL_COUNT" "$task_count")
    footer=$(substitute_placeholder "$footer" "TEST_COUNT" "0")
    footer=$(substitute_placeholder "$footer" "TASK_COUNT" "$task_count")

    echo "$header" > "$output_file"
    echo "$tasks_content" >> "$output_file"
    echo "" >> "$output_file"
    echo "$footer" >> "$output_file"

    echo "Generated: $output_file ($task_count tasks)"
    return 0
}

# =============================================================================
# PROGRESS TRACKING
# =============================================================================

# Update epic Phase 3 when tasks.md is generated
update_epic_phase3() {
    local epic_file="$1"
    [[ ! -f "$epic_file" ]] && return 0

    sed -i.bak "s/- \[[ x]\] Phase 3: Tasks generated/- [x] Phase 3: Tasks generated/" "$epic_file"
    rm -f "${epic_file}.bak"
    echo "Phase 3 marked complete in epic"
}

# Safe grep count that doesn't double-output on zero matches
count_grep() {
    local pattern="$1"
    local file="$2"
    local result
    result=$(grep -c "$pattern" "$file" 2>/dev/null) || result=0
    echo "$result"
}

recalculate_progress() {
    local tasks_file="$1"

    local total_tasks
    total_tasks=$(count_grep "^### [✅🔄❌]*T[0-9]" "$tasks_file")
    local completed_tasks
    completed_tasks=$(count_grep "^### ✅ T[0-9]" "$tasks_file")
    local progress_pct=0

    [[ $total_tasks -gt 0 ]] && progress_pct=$((completed_tasks * 100 / total_tasks))

    sed -i.bak "s/\*\*Overall Progress\*\*: [0-9]*\/[0-9]* tasks completed ([0-9]*%)/\*\*Overall Progress\*\*: $completed_tasks\/$total_tasks tasks completed ($progress_pct%)/" "$tasks_file"
    rm -f "${tasks_file}.bak"

    update_phase_progress "$tasks_file"
    echo "Progress: $completed_tasks/$total_tasks ($progress_pct%)"
}

update_phase_progress() {
    local tasks_file="$1"

    local setup_completed
    setup_completed=$(count_grep "^### ✅ T[0-9].*[Ss]etup\|^### ✅ T[0-9].*[Ii]nit" "$tasks_file")
    local test_completed
    test_completed=$(count_grep "^### ✅ T[0-9].*[Tt]est" "$tasks_file")
    local impl_completed
    impl_completed=$(grep "^### ✅ T[0-9]" "$tasks_file" 2>/dev/null | grep -v -iE "(setup|init|test)" | wc -l | tr -d ' ')

    local setup_total
    setup_total=$(count_grep "^### [✅🔄❌]*T[0-9].*[Ss]etup\|^### [✅🔄❌]*T[0-9].*[Ii]nit" "$tasks_file")
    local test_total
    test_total=$(count_grep "^### [✅🔄❌]*T[0-9].*[Tt]est" "$tasks_file")
    local impl_total
    impl_total=$(grep "^### [✅🔄❌]*T[0-9]" "$tasks_file" 2>/dev/null | grep -v -iE "(setup|init|test)" | wc -l | tr -d ' ')

    local setup_check="[ ]"
    local impl_check="[ ]"
    local test_check="[ ]"

    [[ $setup_total -gt 0 && $setup_completed -eq $setup_total ]] && setup_check="[x]"
    [[ $impl_total -gt 0 && $impl_completed -eq $impl_total ]] && impl_check="[x]"
    [[ $test_total -gt 0 && $test_completed -eq $test_total ]] && test_check="[x]"

    sed -i.bak "s/- \[[ x]\] \*\*Setup\*\*/- $setup_check \*\*Setup\*\*/" "$tasks_file"
    sed -i.bak "s/- \[[ x]\] \*\*Implementation\*\*/- $impl_check \*\*Implementation\*\*/" "$tasks_file"
    sed -i.bak "s/- \[[ x]\] \*\*Testing\*\*/- $test_check \*\*Testing\*\*/" "$tasks_file"
    rm -f "${tasks_file}.bak"
}

update_epic_phases() {
    local tasks_file="$1"
    local epic_file="$(dirname "$tasks_file")/epic.md"

    [[ ! -f "$epic_file" ]] && return 0

    local total_tasks
    total_tasks=$(count_grep "^### [✅🔄]*T[0-9]" "$tasks_file")
    local completed_tasks
    completed_tasks=$(count_grep "^### ✅ T[0-9]" "$tasks_file")
    local progress_pct=0

    [[ $total_tasks -gt 0 ]] && progress_pct=$((completed_tasks * 100 / total_tasks))

    # Phase 4: Implementation complete (100% done)
    if [[ $progress_pct -eq 100 ]]; then
        sed -i.bak "s/- \[[ x]\] Phase 4: Implementation complete/- [x] Phase 4: Implementation complete/" "$epic_file"
    else
        sed -i.bak "s/- \[[ x]\] Phase 4: Implementation complete/- [ ] Phase 4: Implementation complete/" "$epic_file"
    fi

    # Phase 5: All test tasks done
    local test_completed
    test_completed=$(count_grep "^### ✓ T[0-9].*[Tt]est" "$tasks_file")
    local test_total
    test_total=$(count_grep "^### [✓🔄❌ ]*T[0-9].*[Tt]est" "$tasks_file")

    if [[ $test_total -gt 0 && $test_completed -eq $test_total ]]; then
        sed -i.bak "s/- \[[ x]\] Phase 5: Validation runs tests/- [x] Phase 5: Validation runs tests/" "$epic_file"
    else
        sed -i.bak "s/- \[[ x]\] Phase 5: Validation runs tests/- [ ] Phase 5: Validation runs tests/" "$epic_file"
    fi

    rm -f "${epic_file}.bak"
    echo "Epic phases updated ($progress_pct% complete)"
}

# Mark task as started/completed/failed
# Usage: cmd_start <tasks_file> <task_id>
cmd_start() {
    local tasks_file="$1"
    local task_id="$2"

    [[ ! -f "$tasks_file" ]] && die "Tasks file not found: $tasks_file"
    [[ -z "$task_id" ]] && die "Task ID required"

    sed -i.bak "s/^### $task_id:/### 🔄 $task_id:/" "$tasks_file"
    rm -f "${tasks_file}.bak"

    # Auto-save context
    cmd_save "$task_id" "$tasks_file" "in_progress" "$(pwd)"

    recalculate_progress "$tasks_file"
    echo "Task $task_id started"
}

cmd_complete() {
    local tasks_file="$1"
    local task_id="$2"

    [[ ! -f "$tasks_file" ]] && die "Tasks file not found: $tasks_file"
    [[ -z "$task_id" ]] && die "Task ID required"

    # Handle both fresh tasks and in-progress tasks
    sed -i.bak "s/^### 🔄 $task_id:/### ✓ $task_id:/" "$tasks_file"
    sed -i.bak "s/^### $task_id:/### ✓ $task_id:/" "$tasks_file"
    rm -f "${tasks_file}.bak"

    recalculate_progress "$tasks_file"
    update_epic_phases "$tasks_file"
    echo "Task $task_id completed"
}

cmd_fail() {
    local tasks_file="$1"
    local task_id="$2"

    [[ ! -f "$tasks_file" ]] && die "Tasks file not found: $tasks_file"
    [[ -z "$task_id" ]] && die "Task ID required"

    sed -i.bak "s/^### 🔄 $task_id:/### ❌ $task_id:/" "$tasks_file"
    sed -i.bak "s/^### $task_id:/### ❌ $task_id:/" "$tasks_file"
    rm -f "${tasks_file}.bak"

    # Save context for resume
    cmd_save "$task_id" "$tasks_file" "failed" "$(pwd)"

    recalculate_progress "$tasks_file"
    echo "Task $task_id marked as failed"
}

cmd_validation() {
    local epic_file="$1"
    [[ ! -f "$epic_file" ]] && die "Epic file not found: $epic_file"

    sed -i.bak "s/- \[[ x]\] Phase 5: Validation runs tests/- [x] Phase 5: Validation runs tests/" "$epic_file"
    rm -f "${epic_file}.bak"
    echo "Phase 5: Validation marked complete"
}

# =============================================================================
# TASK LIFECYCLE
# =============================================================================

cmd_save() {
    local task_id="$1"
    local current_files="${2:-none}"
    local progress_state="${3:-in_progress}"
    local working_dir="${4:-$(pwd)}"

    [[ -z "$task_id" ]] && die "Task ID required"

    mkdir -p "$VORBIT_DIR/logs"
    local context_file="$VORBIT_DIR/logs/task-${task_id}-context.conf"

    cat > "$context_file" << EOF
# Task Context File for $task_id
# Generated: $(date +%Y-%m-%d\ %H:%M:%S)

TASK_ID="$task_id"
TASK_STATUS="$progress_state"
WORKING_DIR="$working_dir"
CURRENT_FILES="$current_files"
SAVED_TIMESTAMP="$(date +%s)"
EOF

    echo "Context saved: $context_file"
}

cmd_restore() {
    local task_id="$1"
    [[ -z "$task_id" ]] && die "Task ID required"

    local context_file="$VORBIT_DIR/logs/task-${task_id}-context.conf"
    [[ ! -f "$context_file" ]] && die "Context file not found: $context_file"

    source "$context_file"

    [[ -z "$TASK_ID" ]] && die "Invalid context file - missing TASK_ID"

    echo "Task ID: $TASK_ID"
    echo "Status: $TASK_STATUS"
    echo "Working Directory: $WORKING_DIR"
    echo "Current Files: $CURRENT_FILES"
    echo "Saved: $(format_timestamp "$SAVED_TIMESTAMP")"

    if [[ -d "$WORKING_DIR" ]]; then
        cd "$WORKING_DIR"
        echo "Changed to: $WORKING_DIR"
    else
        echo "WARNING: Working directory not found: $WORKING_DIR"
    fi
}

cmd_list() {
    # Show resumable tasks
    cmd_resumable
    echo ""
    # Show all tasks across features
    cmd_tasks
}

cmd_resumable() {
    local logs_dir="$VORBIT_DIR/logs"
    [[ ! -d "$logs_dir" ]] && { echo "No resumable tasks found"; return 0; }

    local count=0
    local header_printed=false

    while IFS= read -r -d '' context_file; do
        local task_id=$(grep "^TASK_ID=" "$context_file" | cut -d'"' -f2)
        local task_status=$(grep "^TASK_STATUS=" "$context_file" | cut -d'"' -f2)
        local saved_timestamp=$(grep "^SAVED_TIMESTAMP=" "$context_file" | cut -d'"' -f2)

        if [[ -n "$task_id" ]]; then
            if [[ "$header_printed" == false ]]; then
                echo "Resumable Tasks:"
                echo "================"
                header_printed=true
            fi
            count=$((count + 1))
            echo "$count. $task_id ($task_status) - $(format_timestamp "$saved_timestamp")"
        fi
    done < <(find "$logs_dir" -name "task-*-context.conf" -type f -print0 2>/dev/null)

    [[ $count -eq 0 ]] && echo "No resumable tasks found"
}

cmd_tasks() {
    [[ ! -d "$FEATURES_DIR" ]] && { echo "No features found"; return 0; }

    echo "Tasks Across All Features"
    echo "========================="

    local total_tasks=0
    local total_completed=0

    for feature_dir in "$FEATURES_DIR"/*/; do
        [[ ! -d "$feature_dir" ]] && continue

        local slug=$(basename "$feature_dir")
        local tasks_file="$feature_dir/tasks.md"
        [[ ! -f "$tasks_file" ]] && continue

        local feature_total
        feature_total=$(count_grep "^### T[0-9]" "$tasks_file")
        local feature_completed
        feature_completed=$(count_grep "^### ✓ T[0-9]" "$tasks_file")
        local feature_in_progress
        feature_in_progress=$(count_grep "^### 🔄 T[0-9]" "$tasks_file")

        total_tasks=$((total_tasks + feature_total))
        total_completed=$((total_completed + feature_completed))

        echo ""
        echo "## $slug ($feature_completed/$feature_total)"

        if [[ $feature_in_progress -gt 0 ]]; then
            grep "^### 🔄 T[0-9]" "$tasks_file" | sed 's/^### 🔄 /   [IN PROGRESS] /'
        fi

        local feature_pending=$((feature_total - feature_completed - feature_in_progress))
        if [[ $feature_pending -gt 0 ]]; then
            local next=$(grep "^### T[0-9]" "$tasks_file" | head -1 | sed 's/^### //')
            echo "   [PENDING] $next"
        fi
    done

    echo ""
    echo "========================="
    echo "Total: $total_completed/$total_tasks completed"
}

cmd_features() {
    list_features
}

cmd_cleanup() {
    local task_id="$1"
    [[ -z "$task_id" ]] && die "Task ID required"

    local context_file="$VORBIT_DIR/logs/task-${task_id}-context.conf"

    if [[ -f "$context_file" ]]; then
        rm "$context_file"
        echo "Cleaned up context for: $task_id"
    else
        echo "No context file found for: $task_id"
    fi
}

cmd_setup() {
    echo "Validating vorbit environment..."

    mkdir -p "$VORBIT_DIR/logs"
    mkdir -p "$FEATURES_DIR"

    check_file "$SCRIPT_DIR/common.sh" "common.sh"
    check_file "$SCRIPT_DIR/task.sh" "task.sh"
    check_file "$TOOLS_DIR/templates/tasks-template.md" "tasks-template.md"
    check_file "$TOOLS_DIR/templates/epic-template.md" "epic-template.md"
    check_file "$TOOLS_DIR/templates/prd-template.md" "prd-template.md"
    check_dir "$VORBIT_DIR" ".vorbit/ directory"
    check_dir "$TOOLS_DIR/templates" "templates/ directory"

    echo "Environment ready"
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    local cmd="${1:-help}"
    shift || true

    case "$cmd" in
        # Generation
        generate|gen)
            cmd_generate "$@"
            ;;
        generate-conversation|gen-conv)
            cmd_generate_conversation "$@"
            ;;

        # Progress
        start)
            cmd_start "$@"
            ;;
        complete)
            cmd_complete "$@"
            ;;
        fail)
            cmd_fail "$@"
            ;;
        recalc)
            recalculate_progress "$@"
            ;;
        validation)
            cmd_validation "$@"
            ;;

        # Lifecycle
        save)
            cmd_save "$@"
            ;;
        restore)
            cmd_restore "$@"
            ;;
        list)
            cmd_list
            ;;
        tasks)
            cmd_tasks
            ;;
        features)
            cmd_features
            ;;
        resumable)
            cmd_resumable
            ;;
        cleanup)
            cmd_cleanup "$@"
            ;;
        setup)
            cmd_setup
            ;;

        help|*)
            echo "Usage: task.sh <command> [args]"
            echo ""
            echo "Generation:"
            echo "  generate <epic_file> [output_dir]  Generate tasks from epic"
            echo "  generate-conversation <text> <dir> Generate tasks from text"
            echo ""
            echo "Progress:"
            echo "  start <tasks_file> <task_id>       Mark task in progress"
            echo "  complete <tasks_file> <task_id>    Mark task completed"
            echo "  fail <tasks_file> <task_id>        Mark task failed"
            echo "  recalc <tasks_file>                Recalculate progress"
            echo "  validation <epic_file>             Mark Phase 5 complete"
            echo ""
            echo "Lifecycle:"
            echo "  save <task_id> [files] [status]    Save task context"
            echo "  restore <task_id>                  Restore task context"
            echo "  list                               Show all tasks"
            echo "  tasks                              Show tasks by feature"
            echo "  features                           Show all features"
            echo "  resumable                          Show tasks with saved context"
            echo "  cleanup <task_id>                  Remove task context"
            echo "  setup                              Validate environment"
            ;;
    esac
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"
