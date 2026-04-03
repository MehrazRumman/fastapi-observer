from __future__ import annotations

import logging


class TextFormatter(logging.Formatter):
    def __init__(
        self,
        fmt: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt: str = "%Y-%m-%d %H:%M:%S",
    ) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt)


__all__ = ["TextFormatter"]
