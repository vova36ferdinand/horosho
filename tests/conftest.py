"""Test configuration and project import path setup."""

import os
import sys

import pytest

PROJECT_SRC = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "src")
)
if PROJECT_SRC not in sys.path:
    sys.path.insert(0, PROJECT_SRC)


@pytest.fixture
def empty_data():
    """Isolate in-memory tuple tables for direct tests and menu tests."""
    import data_layer

    tables = (data_layer.ACCOUNTS, data_layer.MESSAGES, data_layer.FEEDBACKS)
    for table in tables:
        table.clear()
    yield
    for table in tables:
        table.clear()
