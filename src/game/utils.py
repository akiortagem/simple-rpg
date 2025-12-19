"""Shared utilities for configuration and asset paths."""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR.parent / "assets"
CONFIG_DIR = BASE_DIR.parent / "config"


def resolve_asset(path: str) -> Path:
    """Resolve an asset path relative to the shared assets directory."""
    return ASSETS_DIR / path


def resolve_config(path: str) -> Path:
    """Resolve a config path relative to the shared config directory."""
    return CONFIG_DIR / path
