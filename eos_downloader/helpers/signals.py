"""Signal-scoped helpers for download workflows."""

from __future__ import annotations

import signal
from contextlib import contextmanager
from threading import Event
from typing import Any, Iterator


@contextmanager
def sigint_guard(done_event: Event) -> Iterator[None]:
    """Route ``SIGINT`` to a done event, then defer to the previous handler."""
    previous: Any = None
    installed = False

    def handler(signum: int, frame: Any) -> None:
        done_event.set()
        if callable(previous):
            previous(signum, frame)
        elif previous == signal.SIG_DFL:
            signal.default_int_handler(signum, frame)

    try:
        previous = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, handler)
        installed = True
    except ValueError:
        installed = False
    try:
        yield
    finally:
        if installed:
            signal.signal(signal.SIGINT, previous)
