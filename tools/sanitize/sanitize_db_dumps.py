#!/usr/bin/env python3
"""Sanitize DB dumps by replacing external script path references with a placeholder.

This script writes sanitized copies to `benchmark-test/cve-bench/sanitized-db/` preserving originals.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_GLOB = 'benchmark-test/cve-bench/**/db/db.sql'
OUT_DIR = ROOT / 'benchmark-test' / 'cve-bench' / 'sanitized-db'
OUT_DIR.mkdir(parents=True, exist_ok=True)

PATTERN = re.compile(r"<path_cacti>/scripts/[^\)\'\",\s]*")
PLACEHOLDER = '<REMOVED_SCRIPT_PATH>'

def sanitize_file(src: Path, dst: Path):
    text = src.read_text(encoding='utf-8', errors='ignore')
    new = PATTERN.sub(PLACEHOLDER, text)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(new, encoding='utf-8')

def main():
    files = list(ROOT.glob(SOURCE_GLOB))
    if not files:
        print('No db.sql files found to sanitize.')
        return
    for f in files:
        rel = f.relative_to(ROOT / 'benchmark-test' / 'cve-bench')
        out = OUT_DIR / rel
        sanitize_file(f, out)
        print(f'Wrote sanitized copy: {out}')

if __name__ == '__main__':
    main()
