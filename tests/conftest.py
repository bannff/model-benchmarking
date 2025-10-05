import sys
from pathlib import Path

# Ensure the src/ package is importable during tests
root = Path(__file__).resolve().parents[1]
src = root / 'src'
sys.path.insert(0, str(src))
