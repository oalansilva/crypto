from __future__ import annotations

import logging
from functools import lru_cache

from redis import Redis
from redis.exceptions import RedisError

from app.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache()
def get_redis_client() -> Redis | None:
    settings = get_settings()
    redis_url = (settings.redis_url or "").strip()
    if not redis_url:
        return None

    try:
        client = Redis.from_url(redis_url, decode_responses=True)
        return client
    except RedisError as exc:  # pragma: no cover - defensive runtime path
        logger.warning("Failed to initialize Redis client for %s: %s", redis_url, exc)
        return None
