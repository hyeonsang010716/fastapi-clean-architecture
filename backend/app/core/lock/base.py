from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator
from contextlib import asynccontextmanager


class DistributedLock(ABC):
    """분산 락을 위한 추상 기본 클래스"""
    
    @abstractmethod
    async def acquire(self, name: str, ttl: int = 30, timeout: Optional[float] = None) -> bool:
        """
        락을 획득합니다.
        
        Args:
            name: 락의 이름
            ttl: 락의 생존 시간 (초 단위)
            timeout: 락 획득 대기 시간 (None이면 즉시 반환)
            
        Returns:
            bool: 락 획득 성공 여부
        """
        pass
    
    @abstractmethod
    async def release(self, name: str) -> bool:
        """
        락을 해제합니다.
        
        Args:
            name: 락의 이름
            
        Returns:
            bool: 락 해제 성공 여부
        """
        pass
    
    @abstractmethod
    async def extend(self, name: str, ttl: int) -> bool:
        """
        락의 TTL을 연장합니다.
        
        Args:
            name: 락의 이름
            ttl: 연장할 시간 (초 단위)
            
        Returns:
            bool: 연장 성공 여부
        """
        pass
    
    @abstractmethod
    async def is_locked(self, name: str) -> bool:
        """
        락이 설정되어 있는지 확인합니다.
        
        Args:
            name: 락의 이름
            
        Returns:
            bool: 락 설정 여부
        """
        pass
    
    @asynccontextmanager
    async def lock(self, name: str, ttl: int = 30, timeout: Optional[float] = None) -> AsyncIterator[bool]:
        """
        컨텍스트 매니저로 락을 사용합니다.
        
        Args:
            name: 락의 이름
            ttl: 락의 생존 시간 (초 단위)
            timeout: 락 획득 대기 시간
            
        Yields:
            bool: 락 획득 성공 여부
        """
        acquired = await self.acquire(name, ttl, timeout)
        try:
            yield acquired
        finally:
            if acquired:
                await self.release(name)