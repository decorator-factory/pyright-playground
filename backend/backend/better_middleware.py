from typing import Callable

from starlette.middleware import Middleware
from starlette.types import ASGIApp


class BetterMiddleware(Middleware):
    """Like `Middleware` but more type-safe."""

    def __init__(self, fn: Callable[[ASGIApp], ASGIApp]):
        self._fn = fn

    def __iter__(self):
        yield from (lambda app: self._fn(app), {})
