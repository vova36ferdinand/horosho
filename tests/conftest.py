"""Test configuration and project import path setup."""

import os
import sys

PROJECT_SRC = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "src")
)
if PROJECT_SRC not in sys.path:
    sys.path.insert(0, PROJECT_SRC)
