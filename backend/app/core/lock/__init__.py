from functools import lru_cache

from app.core.lock.base import DistributedLock
from app.core.lock.redis_lock import RedisLock

__all__ = ["DistributedLock", "RedisLock", "get_redis_lock"]


@lru_cache(maxsize=1)
def get_redis_lock() -> RedisLock:
    """Redis Lock 싱글톤 인스턴스를 반환합니다"""
    return RedisLock()