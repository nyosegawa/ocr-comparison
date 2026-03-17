"""Pytest configuration."""

import sys
from pathlib import Path

# Add structured_eval to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
