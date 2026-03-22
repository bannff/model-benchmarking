#!/usr/bin/env bash
set -euo pipefail

# verify_repo.sh
# Ensures compliance with Model-Benchmarking Repo Standards (Python-Factory Style)

echo "🔍 Running Repository Verification..."

# 1. Check for required infrastructure files
REQUIRED_FILES=(
    ".beads/README.md"
    ".beads/config.yaml"
    ".agents/steering/dev-principles.md"
    ".agents/steering/project-overview.md"
    ".agents/steering/workflow.md"
    ".github/dependabot.yml"
    ".github/ISSUE_TEMPLATE/bug_report.yml"
    ".github/pull_request_template.md"
    "LICENSE"
    "NOTICE"
)

MISSING=0
for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "❌ Missing required file: $file"
        MISSING=1
    fi
done

if [[ $MISSING -eq 1 ]]; then
    echo "❌ Infrastructure check failed."
else
    echo "✅ All required infrastructure files present."
fi

# 2. Strict LOC Check (<200 lines for .py and .md)
echo "📏 Checking LOC limits (<200 lines per file)..."

VIOLATING_FILES=$(find src benchmarking docs .agents -type f \( -name "*.py" -o -name "*.md" \) -not -path "*/venv/*" -not -path "*/.venv/*" -exec wc -l {} + | awk '$1 > 200 && $2 != "total" {print $2 " (" $1 " lines)"}')

if [[ -n "$VIOLATING_FILES" ]]; then
    echo "❌ The following files exceed the 200 LOC limit:"
    echo "$VIOLATING_FILES"
    echo "⚠️  Strict LOC check failed."
else
    echo "✅ All files comply with the <200 LOC limit."
fi

# 3. Simple SRP / Complexity Check using standard tools if available
if command -v flake8 >/dev/null 2>&1; then
    echo "🧪 Running flake8..."
    flake8 src benchmarking || echo "⚠️ Flake8 found issues."
elif command -v ruff >/dev/null 2>&1; then
    echo "🧪 Running ruff..."
    ruff check src benchmarking || echo "⚠️ Ruff found issues."
else
    echo "⚠️ Neither flake8 nor ruff found. Skipping code quality linting."
fi

echo "🏁 Verification complete."
