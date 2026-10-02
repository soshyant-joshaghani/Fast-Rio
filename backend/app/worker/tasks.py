"""Generic background tasks — register app-specific workers here."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def ping(ctx: dict, message: str = "pong") -> dict[str, str]:
    """Demo / health task — enqueue to verify workers are running."""
    logger.info("ping job received: %s", message)
    return {"message": message, "status": "ok"}
