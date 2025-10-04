#!/usr/bin/env bash
# simple pre-commit hook: prevent staged files larger than threshold
MAX_BYTES=${1:-52428800}
EXIT=0
for file in $(git diff --cached --name-only); do
  if [ -f "$file" ]; then
    size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file")
    if [ "$size" -gt "$MAX_BYTES" ]; then
      echo "ERROR: staged file $file is $size bytes (max: $MAX_BYTES). Use git-lfs or external storage." >&2
      EXIT=1
    fi
  fi
done
exit $EXIT
