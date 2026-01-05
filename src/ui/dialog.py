"""Dialog helpers for NPC interactions."""

from __future__ import annotations

class Dialog:
    """Declarative dialog snippet for NPC interactions."""

    def __init__(self, message: str) -> None:
        self.message = message
        self()

    def __call__(self) -> None:
        """Display the dialog text."""

        print(self.message)

