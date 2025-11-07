# 데이터베이스 마이그레이션 가이드

이 문서는 Alembic을 사용한 데이터베이스 마이그레이션 설정 및 사용 가이드입니다.

## 목차

1. [초기 설정](#초기-설정)
2. [Alembic 환경 구성](#alembic-환경-구성)
3. [마이그레이션 실행](#마이그레이션-실행)
4. [일반적인 워크플로우](#일반적인-워크플로우)
5. [문제 해결](#문제-해결)

## 초기 설정

### 1. Alembic 초기화

`backend` 디렉토리에서 다음 명령어를 실행합니다:

```bash
cd backend
alembic init migration
```

⚠️ **중요**: `migration` 디렉토리가 이미 존재하는 경우, 비워져 있어야 합니다.

### 2. 디렉토리 구조 확인

초기화 후 다음과 같은 구조가 생성됩니다:

```
backend/
├── alembic.ini          # Alembic 설정 파일
├── migration/           # 마이그레이션 디렉토리
│   ├── env.py          # Alembic 환경 설정 (수정 필요)
│   ├── script.py.mako  # 마이그레이션 스크립트 템플릿
│   └── versions/       # 마이그레이션 버전 파일들
└── app/                # 애플리케이션 코드
```

## Alembic 환경 구성

### env.py 설정

`migration/env.py` 파일을 다음 내용으로 **완전히 교체**합니다:

```python
from logging.config import fileConfig
import sys
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 데이터베이스 마이그레이션을 위한 경로 추가
sys.path.append(str(Path(__file__).parent.parent / "app"))

# Alembic Config 객체 - .ini 파일의 값들에 접근 제공
config = context.config

# Python 로깅을 위한 설정 파일 해석
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 'autogenerate' 지원을 위한 모델의 MetaData 객체 추가
from app.database.session import Base
from app.database.model import *  # 모든 모델 임포트
from app.config.setting import settings

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """'offline' 모드에서 마이그레이션 실행
    
    URL만으로 컨텍스트를 구성하고 Engine은 사용하지 않습니다.
    Engine 생성을 생략함으로써 DBAPI가 사용 가능하지 않아도 됩니다.
    """
    url = settings.SYNC_RDB_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """'online' 모드에서 마이그레이션 실행
    
    Engine을 생성하고 컨텍스트와 연결을 연결해야 합니다.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = settings.SYNC_RDB_URL
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 주요 설정 포인트

- **경로 설정**: `sys.path.append()`로 app 디렉토리를 Python 경로에 추가
- **모델 임포트**: `from app.database.model import *`로 모든 모델을 가져옴
- **데이터베이스 URL**: `settings.SYNC_RDB_URL` 사용 (동기식 PostgreSQL URL)
- **메타데이터**: `Base.metadata`를 `target_metadata`로 설정

## 마이그레이션 실행

### 1. Docker 컨테이너 접속

```bash
docker exec -it hyeonsang-backend bash
```

### 2. 가상환경 활성화

```bash
source .venv/bin/activate
```

### 3. 최초 마이그레이션 (Initial Setup)

처음 설정할 때 **한 번만** 실행:

```bash
alembic upgrade head
```

이 명령어는:
- 데이터베이스에 `alembic_version` 테이블을 생성
- 현재까지의 모든 마이그레이션을 적용

### 4. 이후 마이그레이션 워크플로우

모델을 변경한 후:

#### Step 1: 마이그레이션 파일 생성
```bash
alembic revision --autogenerate -m "마이그레이션 설명"
```

예시:
```bash
alembic revision --autogenerate -m "Add user table"
alembic revision --autogenerate -m "Add email index to user"
alembic revision --autogenerate -m "Add product and order tables"
```

#### Step 2: 마이그레이션 적용
```bash
alembic upgrade head
```

## 일반적인 워크플로우

### 개발 중 모델 변경 시

1. **모델 수정** (`app/database/model/*.py`)
   ```python
   # 예: User 모델에 새 필드 추가
   class User(Base):
       __tablename__ = "user"
       
       id = Column(Integer, primary_key=True)
       email = Column(String, unique=True, nullable=False)
       name = Column(String, nullable=False)
       created_at = Column(DateTime, default=datetime.utcnow)
       # 새로 추가된 필드
       phone = Column(String, nullable=True)  # ← 새 필드
   ```

2. **컨테이너 접속 및 환경 설정**
   ```bash
   docker exec -it hyeonsang-backend bash
   source .venv/bin/activate
   ```

3. **마이그레이션 생성**
   ```bash
   alembic revision --autogenerate -m "Add phone field to user table"
   ```

4. **마이그레이션 검토** (선택사항)
   ```bash
   # 생성된 마이그레이션 파일 확인
   cat migration/versions/xxx_add_phone_field_to_user_table.py
   ```

5. **마이그레이션 적용**
   ```bash
   alembic upgrade head
   ```

### 팀 환경에서의 워크플로우

1. **새로운 마이그레이션 파일 받기** (git pull 후)
   ```bash
   alembic upgrade head
   ```

2. **현재 마이그레이션 상태 확인**
   ```bash
   alembic current
   alembic history --verbose
   ```

## 유용한 명령어

### 마이그레이션 상태 확인

```bash
# 현재 마이그레이션 버전 확인
alembic current

# 마이그레이션 히스토리 확인
alembic history

# 더 자세한 히스토리
alembic history --verbose
```

### 마이그레이션 롤백

```bash
# 한 단계 이전으로 롤백
alembic downgrade -1

# 특정 리비전으로 롤백
alembic downgrade <revision_id>

# 모든 마이그레이션 롤백 (초기화)
alembic downgrade base
```

### 마이그레이션 미리보기

```bash
# SQL 미리보기 (실제 실행하지 않음)
alembic upgrade head --sql

# 특정 리비전까지의 SQL 미리보기
alembic upgrade <revision_id> --sql
```

## 문제 해결

### 자주 발생하는 문제들

#### 1. "Target database is not up to date" 오류

```bash
# 해결: 먼저 데이터베이스를 최신 상태로 업그레이드
alembic upgrade head
```

#### 2. 모델을 찾을 수 없는 오류

```python
# env.py에서 모든 모델이 임포트되었는지 확인
from app.database.model import *
```

#### 3. 데이터베이스 연결 오류

- `settings.SYNC_RDB_URL`이 올바른지 확인
- PostgreSQL 서비스가 실행 중인지 확인
- Docker 컨테이너가 데이터베이스에 접근할 수 있는지 확인

#### 4. 마이그레이션 충돌

```bash
# 마이그레이션 히스토리 확인
alembic history

# 필요시 수동으로 병합
alembic merge -m "merge conflicting revisions" <rev1> <rev2>
```

### 마이그레이션 파일 수동 수정

때때로 자동 생성된 마이그레이션 파일을 수동으로 수정해야 할 수 있습니다:

1. `migration/versions/` 디렉토리의 해당 파일 편집
2. 데이터 마이그레이션 로직 추가
3. 인덱스나 제약조건 수정
4. 테스트 후 적용

## 연습

### 1. 의미 있는 마이그레이션 메시지

```bash
# 좋은 예
alembic revision --autogenerate -m "Add user authentication tables"
alembic revision --autogenerate -m "Add index on user.email for performance"

# 나쁜 예
alembic revision --autogenerate -m "update"
alembic revision --autogenerate -m "fix"
```

### 2. 마이그레이션 검토

- 자동 생성된 마이그레이션 파일을 항상 검토
- 데이터 손실 위험이 있는 변경사항 주의
- 대용량 테이블 변경 시 다운타임 고려

### 3. 백업

중요한 마이그레이션 전에는 데이터베이스 백업 권장:

```bash
# PostgreSQL 백업 예시
pg_dump -h localhost -U username dbname > backup.sql
```

### 4. 테스트 환경에서 먼저 실행

프로덕션에 적용하기 전에 개발/스테이징 환경에서 마이그레이션을 테스트하세요.

---

이 가이드를 따라 안전하고 효율적으로 데이터베이스 마이그레이션을 관리하세요!