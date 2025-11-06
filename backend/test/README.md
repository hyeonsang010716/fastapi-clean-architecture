# 테스트 가이드라인 (단위 테스트 & 통합 테스트)

이 문서는 `@backend/app/service/` 계층의 단위 테스트와 통합 테스트를 작성하기 위한 가이드라인을 제공합니다.

## 목차

1. [테스트 구조](#테스트-구조)
2. [단위 테스트 (Unit Tests)](#단위-테스트-unit-tests)
3. [통합 테스트 (Integration Tests)](#통합-테스트-integration-tests)
4. [Mocking 전략](#mocking-전략)
5. [테스트 패턴](#테스트-패턴)
6. [연습](#연습)
7. [실행 방법](#실행-방법)
8. [체크리스트](#체크리스트)
9. [참고 사항](#참고사항)

## 테스트 구조

### 프로젝트 구조
```
backend/
├── test/
│   ├── unit/                          # 단위 테스트
│   │   ├── __init__.py
│   │   ├── conftest.py               # 단위 테스트용 fixture
│   │   └── test_user_service.py      # UserService 단위 테스트
│   ├── integration/                   # 통합 테스트
│   │   ├── __init__.py
│   │   ├── conftest.py               # 통합 테스트용 fixture
│   │   └── test_user_service.py
│   └── README.md                     # 가이드 문서
├── app/
│   └── service/                      # 테스트 대상 서비스들
└── pyproject.toml                    # pytest 설정
```

### 테스트 분류
- **단위 테스트** (`test/unit/`): Mock을 사용해 외부 의존성을 제거한 빠른 테스트
- **통합 테스트** (`test/integration/`): 실제 데이터베이스를 사용한 전체 플로우 테스트

### 테스트 파일 명명 규칙
- 단위 테스트: `test/unit/test_{service_name}_service.py`
- 통합 테스트: `test/integration/test_{service_name}_service.py`
- 테스트 클래스: `Test{ServiceName}Service`
- 테스트 메서드: `test_{method_name}_{scenario}`

## Mocking 전략

### 1. DI 기반 Repository Mocking

`@patch` 대신 의존성 주입(DI) 패턴을 사용하여 깔끔하게 Mock을 주입합니다.


### 2. UnitOfWork Mocking

UnitOfWork는 트랜잭션 관리를 담당하므로 적절히 mock해야 합니다.

```python
@pytest.fixture
def mock_uow():
    uow = Mock(spec=UnitOfWork)
    mock_session = AsyncMock()
    
    uow.__aenter__ = AsyncMock(return_value=mock_session)
    uow.__aexit__ = AsyncMock(return_value=None)
    
    return uow
```

### 3. DTO Fixtures

테스트에서 사용할 DTO 객체들을 미리 정의합니다.

```python
@pytest.fixture
def sample_user_create_dto():
    return UserCreateDTO(
        email="test@example.com",
        name="Test User"
    )
```

## 테스트 패턴

### 1. AAA 패턴 (Arrange, Act, Assert)

```python
async def test_create_user_success(self, mock_user_repo_class):
    # Arrange (Given)
    mock_user_repo = AsyncMock(spec=UserRepository)
    mock_user_repo_class.return_value = mock_user_repo
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.create.return_value = self.sample_user_dto
    
    # Act (When)
    result = await self.user_service.create_user(self.sample_user_create_dto)
    
    # Assert (Then)
    assert result == self.sample_user_dto
    mock_user_repo.get_by_email.assert_called_once_with(self.sample_user_create_dto.email)
    mock_user_repo.create.assert_called_once_with(self.sample_user_create_dto)
```

### 2. 성공/실패 시나리오 분리

각 메서드에 대해 성공 케이스와 실패 케이스를 모두 테스트합니다.

```python
async def test_create_user_success(self):
    # 성공 케이스 테스트
    pass

async def test_create_user_already_exists(self):
    # 실패 케이스 테스트 (이미 존재하는 사용자)
    with pytest.raises(ValueError, match="already exists"):
        await self.user_service.create_user(self.sample_user_create_dto)
```

## 연습

### 1. Mock 검증

Mock 객체가 올바르게 호출되었는지 검증합니다.

```python
# 호출 횟수 검증
mock_user_repo.get_by_email.assert_called_once_with(email)

# 호출되지 않았음을 검증
mock_user_repo.create.assert_not_called()

# 특정 인자로 호출되었는지 검증
mock_user_repo.update.assert_called_once_with(email, update_dto)
```

### 2. Fixture 활용

공통으로 사용되는 테스트 데이터는 fixture로 정의합니다.

```python
@pytest.fixture(autouse=True)
def setup(self, mock_uow, sample_user_create_dto):
    self.mock_uow = mock_uow
    self.sample_user_create_dto = sample_user_create_dto
    self.user_service = UserService(uow=mock_uow)
```

### 3. 마커 사용

테스트 종류를 구분하기 위해 마커를 사용합니다.

```python
@pytest.mark.unit
class TestUserService:
    pass

@pytest.mark.integration
class TestUserServiceIntegration:
    pass
```

### 4. 예외 메시지 검증

예외가 발생하는 경우 메시지도 함께 검증합니다.

```python
with pytest.raises(ValueError, match="User with email .* not found"):
    await self.user_service.update_user(email, update_dto)
```

## 단위 테스트 (Unit Tests)

단위 테스트는 `test/unit/` 디렉토리에 위치하며, 모든 외부 의존성(데이터베이스, 외부 API 등)을 Mock으로 대체합니다.

### 특징
- **빠른 실행**: 외부 의존성 없이 메모리에서만 실행
- **독립성**: 각 테스트가 완전히 독립적
- **예측 가능**: Mock을 통해 모든 시나리오 제어 가능

### fixture 활용
단위 테스트는 `test/unit/conftest.py`의 Mock fixture들을 활용합니다:
- `user_service_with_di`: DI 기반 UserService와 Mock Repository Mapping 딕셔너리
- `mock_repository_factory`: 범용 Repository Mock 팩토리
- `service_di_factory`: 범용 Service DI 팩토리 
- `mock_user_repository`: UserRepository Mock
- `mock_uow`: UnitOfWork Mock (기존 방식)
- `sample_user_*_dto`: 테스트용 DTO 객체들

#### 팩토리 패턴 활용

새로운 Repository나 Service를 위한 Mock을 쉽게 생성할 수 있습니다:

```python
# 새로운 Repository Mock 생성
@pytest.fixture
def mock_product_repository(mock_repository_factory):
    return mock_repository_factory(
        ProductRepository,
        get_by_id=None,
        get_all=[],
        create=None,
        update=None,
        delete=False,
    )

# 새로운 Service DI 생성  
@pytest.fixture
def product_service_with_di(mock_product_repository, service_di_factory):
    return service_di_factory(
        ProductService,
        "app.service.product",
        {"ProductRepository": mock_product_repository}
    )
```

#### DI 기반 테스트 작성법
```python
@pytest.fixture(autouse=True)
def setup(self, user_service_with_di, sample_user_create_dto):
    self.user_service, repo_mapping = user_service_with_di
    self.mock_repository = repo_mapping["UserRepository"]

    self.sample_user_create_dto = sample_user_create_dto

async def test_create_user_success(self):
    # Mock 동작 설정
    self.mock_repository.get_by_email.return_value = None
    self.mock_repository.create.return_value = expected_user_dto
    
    # 테스트 실행
    result = await self.user_service.create_user(self.sample_user_create_dto)
    
    # 검증
    assert result == expected_user_dto
    self.mock_repository.get_by_email.assert_called_once()
```

## 통합 테스트 (Integration Tests)

통합 테스트는 `test/integration/` 디렉토리에 위치하며, 실제 데이터베이스를 사용합니다.

### 특징
- **실제 환경**: SQLite 인메모리 DB 사용
- **전체 플로우**: Service → Repository → Database 전체 흐름 테스트
- **실제 트랜잭션**: 실제 데이터베이스 트랜잭션 사용

### fixture 활용
통합 테스트는 `test/integration/conftest.py`의 DB fixture들을 활용합니다:
- `test_engine`: 테스트용 데이터베이스 엔진
- `test_uow`: 실제 UnitOfWork 인스턴스
- `clean_database`: 테스트 전후 DB 정리
- `sample_user_in_db`: DB에 생성된 테스트 사용자

## 실행 방법

### 모든 테스트 실행
```bash
cd backend
uv run pytest
```

### 단위 테스트만 실행
```bash
uv run pytest -m unit
uv run pytest test/unit/
```

### 통합 테스트만 실행
```bash
uv run pytest -m integration
uv run pytest test/integration/
```

### 특정 테스트 파일 실행
```bash
# 단위 테스트
uv run pytest test/unit/test_user_service.py

# 통합 테스트
uv run pytest test/integration/test_user_service.py
```

### 느린 테스트 제외하고 실행
```bash
uv run pytest -m "not slow"
```

## 체크리스트

### 단위 테스트 체크리스트
- [ ] `test/unit/test_{service_name}_service.py` 파일 생성
- [ ] 필요한 Mock fixture를 `test/unit/conftest.py`에 추가
- [ ] **DI 기반 Mock Repository fixture 구현**
  - [ ] `{service_name}_service_with_di` fixture 생성
  - [ ] `monkeypatch`를 사용한 Repository 주입
  - [ ] `@transactional` 데코레이터 bypass
- [ ] 각 service 메서드에 대한 성공/실패 케이스 작성
- [ ] 엣지 케이스 테스트 추가
- [ ] Mock 호출 검증 구현
- [ ] 예외 메시지 검증 추가
- [ ] `@pytest.mark.unit` 마커 추가

### 통합 테스트 체크리스트
- [ ] `test/integration/test_{service_name}_service.py` 파일 생성
- [ ] 필요한 DB fixture를 `test/integration/conftest.py`에 추가
- [ ] 실제 데이터베이스를 사용한 전체 플로우 테스트 작성
- [ ] 데이터베이스 상태 검증 추가
- [ ] 트랜잭션 롤백/커밋 테스트 추가
- [ ] `@pytest.mark.integration` 마커 추가
- [ ] 대량 데이터 처리 테스트 추가 (필요시, `@pytest.mark.slow`)

## 참고사항

### 단위 테스트 주의할 점
1. **실제 데이터베이스 사용 금지**: 단위 테스트에서는 실제 DB에 연결하지 않습니다.
2. **외부 의존성 최소화**: 모든 외부 의존성은 mock으로 대체합니다.
3. **테스트 격리**: 각 테스트는 독립적으로 실행되어야 합니다.
4. **빠른 실행**: 단위 테스트는 수 밀리초 내에 완료되어야 합니다.

### 통합 테스트 주의할 점
1. **테스트 데이터 정리**: 각 테스트 후 데이터베이스를 정리합니다.
2. **트랜잭션 관리**: 테스트 간 데이터 오염을 방지합니다.
3. **실제 환경 모방**: 가능한 한 실제 환경과 유사하게 테스트합니다.
4. **느린 테스트 마킹**: 시간이 오래 걸리는 테스트는 `@pytest.mark.slow`로 마킹합니다.

### 공통 고려사항
- **명확한 테스트 이름**: 테스트 이름만 보고도 무엇을 테스트하는지 알 수 있어야 합니다.
- **비동기 처리**: `async def`로 정의하고 `await`로 호출합니다.
- **AsyncMock 사용**: 비동기 메서드를 mock할 때는 `AsyncMock`을 사용합니다.
- **마커 활용**: 테스트 유형에 따라 적절한 마커를 사용합니다.

### 테스트 실행 전략
1. **개발 중**: 단위 테스트만 빠르게 실행 (`pytest -m unit`)
2. **PR 전**: 모든 테스트 실행 (`pytest`)
3. **CI/CD**: 단위 테스트 → 통합 테스트 순서로 실행
4. **릴리즈 전**: 느린 테스트 포함 전체 실행 (`pytest -m "slow"`)

이 가이드라인을 따라 일관성 있고 신뢰할 수 있는 테스트를 작성하세요.