"""Asset loading utilities that hide framework-specific details."""

from __future__ import annotations

from pathlib import Path

import pygame


def load_image(
    path: str | Path,
    fallback_size: tuple[int, int],
    fallback_color: tuple[int, int, int],
) -> pygame.Surface:
    """Load an image file or create a colored placeholder surface.

    The returned object is compatible with the pygame-backed renderer but keeps
    pygame details out of higher-level modules and examples.
    """

    asset_path = Path(path)
    if asset_path.exists():
        return pygame.image.load(asset_path).convert_alpha()

    surface = pygame.Surface(fallback_size, pygame.SRCALPHA)
    surface.fill(fallback_color)
    return surface
