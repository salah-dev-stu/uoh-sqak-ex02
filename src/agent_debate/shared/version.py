"""Code version tracking (R6 — starts at 1.00, bumps +0.01 per change).

Validates loaded config files declare a compatible version at startup.
"""
from __future__ import annotations

CODE_VERSION = "1.00"


def validate_config_version(config_version: str, source: str) -> None:
    if config_version != CODE_VERSION:
        raise ValueError(
            f"Config version mismatch: {source} declares {config_version} "
            f"but code expects {CODE_VERSION}"
        )
