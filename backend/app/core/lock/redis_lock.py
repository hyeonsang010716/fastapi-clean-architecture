import uuid
import asyncio
from typing import Optional, Dict
from contextvars import ContextVar

from app.core.lock.base import DistributedLock
from app.core.redis import get_redis_client
from app.core.logger import get_logger

logger = get_logger("redis.lock")


_LOCK_TOKENS: ContextVar[Dict[str, str]] = ContextVar("_LOCK_TOKENS", default=None)


def _get_token_map() -> Dict[str, str]:
    """현재 실행 컨텍스트(태스크) 전용 토큰 맵을 가져온다."""
    try:
        m = _LOCK_TOKENS.get()
        if m is None:
            m = {}
            _LOCK_TOKENS.set(m)
        return m
    except LookupError:
        m = {}
        _LOCK_TOKENS.set(m)
        return m


class RedisLock(DistributedLock):
    """Redis를 사용한 분산 락 구현체"""

    # 락 소유자만 해제
    RELEASE_SCRIPT = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """

    # 락 소유자만 TTL 연장
    EXTEND_SCRIPT = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("expire", KEYS[1], ARGV[2])
    else
        return 0
    end
    """

    def __init__(self) -> None:
        self._lock_prefix = "lock:"

    def _get_lock_key(self, name: str) -> str:
        return f"{self._lock_prefix}{name}"

    async def acquire(self, name: str, ttl: int = 30, timeout: Optional[float] = None) -> bool:
        """
        Redis 락 획득
        - 성공 시, 현재 태스크의 토큰 맵에 name->token 저장
        - timeout=None: 즉시 실패 반환
          timeout==0  : 무제한 대기
          timeout>0   : 해당 시간까지만 polling
        """
        client = await get_redis_client()
        lock_key = self._get_lock_key(name)

        loop = asyncio.get_running_loop()
        start_time = loop.time()
        token = str(uuid.uuid4())

        while True:
            try:
                acquired = await client.set(lock_key, token, nx=True, ex=ttl)
                if acquired:
                    token_map = _get_token_map()
                    if name in token_map:
                        logger.warning(f"Overwriting existing token for lock '{name}' in current task")
                    token_map[name] = token
                    logger.debug(f"Lock '{name}' acquired (ttl={ttl}s)")
                    return True

                if timeout is None:
                    return False
                elif timeout == 0:
                    await asyncio.sleep(0.1)
                else:
                    elapsed = loop.time() - start_time
                    if elapsed >= timeout:
                        logger.debug(f"Lock '{name}' acquisition timed out after {elapsed:.2f}s")
                        return False
                    await asyncio.sleep(min(0.1, timeout - elapsed))

            except Exception as e:
                logger.error(f"Error acquiring lock '{name}': {e}")
                return False

    async def release(self, name: str) -> bool:
        """
        Redis 락 해제
        - 현재 태스크의 토큰 맵에서 token을 찾아 Lua로 소유자 검증 후 삭제
        """
        client = await get_redis_client()
        lock_key = self._get_lock_key(name)

        token = _get_token_map().get(name)
        if not token:
            logger.warning(f"No token found for lock '{name}' in current task")
            return False

        try:
            result = await client.eval(self.RELEASE_SCRIPT, 1, lock_key, token)
            if result:
                _get_token_map().pop(name, None)
                logger.debug(f"Lock '{name}' released")
                return True
            else:
                logger.warning(f"Failed to release lock '{name}' - not owned by current task/token")
                return False
        except Exception as e:
            logger.error(f"Error releasing lock '{name}': {e}")
            return False

    async def extend(self, name: str, ttl: int) -> bool:
        """
        락 TTL 연장(옵션)
        - 현재 태스크 보유 토큰으로만 연장 가능
        """
        client = await get_redis_client()
        lock_key = self._get_lock_key(name)

        token = _get_token_map().get(name)
        if not token:
            logger.warning(f"No token found for lock '{name}' in current task")
            return False

        try:
            result = await client.eval(self.EXTEND_SCRIPT, 1, lock_key, token, ttl)
            if result:
                logger.debug(f"Lock '{name}' TTL extended by {ttl}s")
                return True
            else:
                logger.warning(f"Failed to extend lock '{name}' - not owned by current task/token")
                return False
        except Exception as e:
            logger.error(f"Error extending lock '{name}': {e}")
            return False

    async def is_locked(self, name: str) -> bool:
        """락 존재 여부"""
        client = await get_redis_client()
        lock_key = self._get_lock_key(name)
        try:
            return bool(await client.exists(lock_key))
        except Exception as e:
            logger.error(f"Error checking lock '{name}': {e}")
            return False

    async def is_owned_by_me(self, name: str) -> bool:
        """
        현재 태스크가 해당 락의 소유자인지 확인
        - Redis의 값(value)과 현재 태스크의 token 일치 여부 검사
        """
        client = await get_redis_client()
        lock_key = self._get_lock_key(name)

        token = _get_token_map().get(name)
        if not token:
            return False

        try:
            value = await client.get(lock_key)
            return value == token
        except Exception as e:
            logger.error(f"Error checking lock ownership '{name}': {e}")
            return False
