import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from app.database.session import UnitOfWork, Base
from app.database.model.user import User
from app.service.user import UserService
from app.dto.user import UserCreateDTO, UserUpdateDTO, UserDTO


""" 
테스트 데이터베이스 환경 셋업
"""

# SQLite 인메모리 데이터베이스 URL (테스트용)
TEST_RDB_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_RDB_URL,
        echo=False,
        future=True,
    )
    
    # 모든 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # 정리
    await engine.dispose()


@pytest.fixture(scope="session")
async def test_session_factory(test_engine):
    """Create test session factory"""
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


@pytest.fixture
async def test_uow(test_session_factory):
    """Create UnitOfWork for integration tests"""
    return UnitOfWork(session=test_session_factory)


@pytest.fixture
async def test_session(test_session_factory):
    """Create test database session"""
    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def clean_database(test_session):
    """Clean database before each test"""
    # 테스트 전에 테이블 안에 데이터 삭제
    await test_session.execute(text("DELETE FROM user"))
    await test_session.commit()
    
    yield
    
    # 테스트 후에 테이블 안에 데이터 삭제
    await test_session.execute(text("DELETE FROM user"))
    await test_session.commit()


@pytest.fixture(autouse=True)
async def integration_test_setup(clean_database):
    """Auto-used fixture for integration test setup"""
    pass


""" 
테스트 목업 데이터 셋업
"""


@pytest.fixture
async def user_service_integration(test_uow):
    """UserService for integration tests with real database"""
    return UserService(uow=test_uow)


@pytest.fixture
def integration_user_create_dto():
    """Sample UserCreateDTO for integration testing"""
    return UserCreateDTO(
        email="integration@example.com",
        name="Integration Test User"
    )


@pytest.fixture
def integration_user_update_dto():
    """Sample UserUpdateDTO for integration testing"""
    return UserUpdateDTO(
        name="Updated Integration User"
    )


@pytest.fixture
async def sample_user_in_db(test_session, integration_user_create_dto):
    """Create a sample user in the test database"""
    user = User(
        email=integration_user_create_dto.email,
        name=integration_user_create_dto.name
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    
    return UserDTO.from_orm(user)


@pytest.fixture
async def multiple_users_in_db(test_session):
    """Create multiple users in the test database"""
    users_data = [
        {"email": "user1@integration.com", "name": "Integration User 1"},
        {"email": "user2@integration.com", "name": "Integration User 2"},
        {"email": "user3@integration.com", "name": "Integration User 3"},
    ]
    
    created_users = []
    for user_data in users_data:
        user = User(**user_data)
        test_session.add(user)
        created_users.append(user)
    
    await test_session.commit()
    
    for user in created_users:
        await test_session.refresh(user)
    
    return [UserDTO.from_orm(user) for user in created_users]