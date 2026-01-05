"""Shared utility helpers.

Use ``resolve_asset`` and ``resolve_config`` to build asset/config paths rooted
at the project ``ASSETS_DIR`` and ``CONFIG_DIR`` constants.
"""

from .paths import ASSETS_DIR, BASE_DIR, CONFIG_DIR, resolve_asset, resolve_config

__all__ = [
    "ASSETS_DIR",
    "BASE_DIR",
    "CONFIG_DIR",
    "resolve_asset",
    "resolve_config",
]
