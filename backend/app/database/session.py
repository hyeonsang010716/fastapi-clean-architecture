from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker
from functools import wraps


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
        async with self.uow as session:
            return await fn(self, *args, **kwargs)
    return wrapper

Base = declarative_base()