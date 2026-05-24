"""Shared pytest fixtures. Phase-specific fixtures get added as tasks reach them."""
from __future__ import annotations

import os

import pytest


def pytest_collection_modifyitems(config, items):
    """Skip e2e tests unless RUN_E2E=1."""
    if os.environ.get("RUN_E2E") == "1":
        return
    skip_e2e = pytest.mark.skip(reason="requires RUN_E2E=1")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip_e2e)
