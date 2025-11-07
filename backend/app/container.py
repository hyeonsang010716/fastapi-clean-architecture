from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database.session import UnitOfWork
from app.config.setting import settings
from app.service.user import UserService

class Container(containers.DeclarativeContainer):
    """DI Container — 의존성 선언"""

    engine = providers.Singleton(
        create_async_engine,
        settings.RDB_URL,
        echo=False,
        future=True,
    )

    session_factory = providers.Singleton(
        async_sessionmaker,
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    uow = providers.Factory(UnitOfWork, session=session_factory)

    # 서비스 계층 주입
    user_service = providers.Factory(UserService, uow=uow)
    
    # 컨트롤러 계층 주입
    user_service_session = providers.Factory(UserService, uow=None)
