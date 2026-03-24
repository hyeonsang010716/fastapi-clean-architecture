import redis.asyncio as redis
from app.config.setting import settings


class RedisClient:
    """Redis 클라이언트 관리 클래스"""
    
    _instance = None
    _client = None
    
    # 캐시 TTL 상수
    DEFAULT_CACHE_TTL = 86400  # 24 hours in seconds
    SHORT_CACHE_TTL = 3600     # 1 hour in seconds
    MEDIUM_CACHE_TTL = 43200   # 12 hours in seconds
    PROGRESS_TTL = 300         # 5 minutes in seconds
    
    @classmethod
    async def get_client(cls) -> redis.Redis:
        """Redis 클라이언트를 반환하는 메서드"""
        if cls._client is None:
            cls._client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                encoding="utf-8"
            )
        return cls._client
    
    @classmethod
    async def close(cls):
        """Redis 연결 종료"""
        if cls._client:
            await cls._client.close()
            cls._client = None


async def get_redis_client() -> redis.Redis:
    """Redis 클라이언트를 반환하는 함수"""
    return await RedisClient.get_client()


async def close_redis():
    """Redis 연결 종료"""
    await RedisClient.close()