from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from functools import wraps


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
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