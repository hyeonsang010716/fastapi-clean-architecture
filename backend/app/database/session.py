from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker
from functools import wraps
from contextvars import ContextVar

"""
RDB
"""

_current_session: ContextVar = ContextVar('_current_session', default=None) # 트랜잭션 전파 관리

class UnitOfWork:
    def __init__(self, session: async_sessionmaker):
        self.session_factory = session

    async def __aenter__(self):
        self.session = self.session_factory()
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()


def transactional(fn):
    @wraps(fn)
    async def wrapper(self, *args, **kwargs):
        existing = _current_session.get()
        if existing is not None:
            # 이미 트랜잭션이 열려 있으면 기존 세션에 참여
            self._session = existing
            return await fn(self, *args, **kwargs)

        # 새 트랜잭션 시작
        async with self.uow as session:
            token = _current_session.set(session)
            self._session = session
            try:
                return await fn(self, *args, **kwargs)
            finally:
                _current_session.reset(token)
                self._session = None
    return wrapper


Base = declarative_base()

"""
NoSQL
"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie

from app.config.setting import settings
from app.database.model.log import Log
from app.database.model.progress import Progress

class MongoDB:
    """MongoDB 클라이언트 및 데이터베이스 관리"""
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None # type: ignore
        self.database: Optional[AsyncIOMotorDatabase] = None # type: ignore
        
    async def connect(self):
        """MongoDB 연결 및 초기화"""
        self.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=100,
            minPoolSize=10,
            tz_aware=True,
        )
        self.database = self.client[settings.MONGODB_NAME]
        
        await init_beanie(
            database=self.database,
            document_models=[Log, Progress]
        )
        
    async def disconnect(self):
        """MongoDB 연결 종료"""
        if self.client:
            self.client.close()
            
mongodb = MongoDB()


async def init_mongodb():
    """MongoDB 초기화 (앱 시작 시 호출)"""
    await mongodb.connect()
    

async def close_mongodb():
    """MongoDB 종료 (앱 종료 시 호출)"""
    await mongodb.disconnect()