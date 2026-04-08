from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import UnitOfWork, transactional
from app.repository.user import UserRepository
from app.dto.user import UserCreateDTO, UserUpdateDTO, UserDTO


class UserService:
    """User Service"""
    
    def __init__(self, uow: UnitOfWork = None):
        self.uow = uow

    @transactional
    async def create_user(self, user_data: UserCreateDTO) -> UserDTO:
        """사용자 생성"""
        user_repo = UserRepository(self._session)
        
        existing_user = await user_repo.get_by_email(user_data.email)
        if existing_user:
            raise ValueError(f"User with email {user_data.email} already exists")
        
        return await user_repo.create(user_data)

    async def create_user_with_session(self, session: AsyncSession, user_data: UserCreateDTO) -> UserDTO:
        """사용자 생성 (컨트롤러 레벨 트랜잭션용)"""
        user_repo = UserRepository(session)
        
        existing_user = await user_repo.get_by_email(user_data.email)
        if existing_user:
            raise ValueError(f"User with email {user_data.email} already exists")
        
        return await user_repo.create(user_data)

    @transactional
    async def get_user_by_email(self, email: str) -> Optional[UserDTO]:
        """이메일로 사용자 조회"""
        user_repo = UserRepository(self._session)
        return await user_repo.get_by_email(email)

    @transactional
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> Tuple[List[UserDTO], int]:
        """모든 사용자 조회 (페이징 포함)"""
        user_repo = UserRepository(self._session)
        
        users = await user_repo.get_all(skip=skip, limit=limit)
        total = await user_repo.count_all()
        
        return users, total

    @transactional
    async def update_user(self, email: str, user_data: UserUpdateDTO) -> Optional[UserDTO]:
        """사용자 정보 업데이트"""
        user_repo = UserRepository(self._session)
        
        existing_user = await user_repo.get_by_email(email)
        if not existing_user:
            raise ValueError(f"User with email {email} not found")
        
        if not any(v is not None for v in user_data.model_dump().values()):
            raise ValueError("No data provided for update")
        
        return await user_repo.update(email, user_data)

    @transactional
    async def delete_user(self, email: str) -> bool:
        """사용자 삭제"""
        user_repo = UserRepository(self._session)
        
        existing_user = await user_repo.get_by_email(email)
        if not existing_user:
            raise ValueError(f"User with email {email} not found")
        
        return await user_repo.delete(email)