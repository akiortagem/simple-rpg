"""Asyncio scheduler for running tasks on a shared event loop."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any


class AsyncScheduler:
    """Own a single asyncio loop to advance background tasks per frame."""

    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    def create_task(self, coro: Coroutine[Any, Any, Any]) -> asyncio.Task[Any]:
        return self._loop.create_task(coro)

    def tick(self) -> None:
        if self._loop.is_closed():
            return
        self._loop.run_until_complete(asyncio.sleep(0))
