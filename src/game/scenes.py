"""Backward-compatible import surface for domain scenes."""

from __future__ import annotations

from .domain.scenes import DemoScene, MapScene, Scene

__all__ = ["Scene", "DemoScene", "MapScene"]
