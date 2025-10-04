#!/usr/bin/env bash
set -euo pipefail
HOOK_DIR=".git/hooks"
if [ ! -d "$HOOK_DIR" ]; then
  echo "No .git/hooks directory — are you in a git repo?" >&2
  exit 1
fi
cp tools/precommit/check-large-files.sh "$HOOK_DIR/pre-commit"
chmod +x "$HOOK_DIR/pre-commit"
echo "Installed pre-commit hook to $HOOK_DIR/pre-commit"
