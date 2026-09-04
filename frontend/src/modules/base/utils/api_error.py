"""HTTP API errors with status codes."""

from __future__ import annotations


class ApiError(Exception):
    def __init__(self, message: str, status: int) -> None:
        super().__init__(message)
        self.status = status
