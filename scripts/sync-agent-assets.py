#!/usr/bin/env python3
"""Repository-local entry point for safe Vorbit asset synchronization."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from vorbit_core.sync import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
