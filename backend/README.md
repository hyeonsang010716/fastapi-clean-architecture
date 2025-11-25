# Server 스팩

## 의존성 라이브러리

### 웹 프레임워크 & API
- **fastapi[standard]** (0.118.0): 현대적이고 빠른 Python 웹 API 프레임워크. 자동 문서 생성과 타입 검증 지원
- **python-socketio** (5.13.0): Socket.IO 서버 구현. 실시간 양방향 통신 지원

### 데이터베이스 & ORM
- **sqlalchemy[asyncio]** (2.0.43): Python SQL 툴킷 및 ORM. 비동기 데이터베이스 작업 지원
- **alembic** (1.16.4): SQLAlchemy 기반 데이터베이스 마이그레이션 도구
- **beanie** (1.26.0): MongoDB용 비동기 ODM (Object Document Mapper)
- **motor** (3.3.2): MongoDB용 비동기 Python 드라이버
- **pymongo** (4.6.3): MongoDB 공식 Python 드라이버

### 데이터베이스 드라이버
- **asyncpg** (0.30.0): PostgreSQL용 고성능 비동기 드라이버
- **psycopg2-binary** (2.9.10): PostgreSQL 데이터베이스 어댑터 (바이너리 버전) # alembic 위해서 필요
- **redis** (6.4.0): Redis 인메모리 데이터 저장소 Python 클라이언트

### AI & LLM 통합
- **langchain** (1.0.0): LLM 애플리케이션 개발 프레임워크
- **langchain-chroma** (1.0.0): 벡터 임베딩 저장 및 검색을 위한 Chroma 벡터 데이터베이스와 LangChain 통합
- **langchain-openai** (1.0.1): OpenAI API와 LangChain 통합
- **langgraph-checkpoint-sqlite** (2.0.1): LangGraph 상태 관리용 SQLite 체크포인트 저장소

### 인증 & 보안
- **passlib[argon2]** (1.7.4): 비밀번호 해싱 라이브러리 (Argon2 알고리즘 포함)
- **pyjwt[crypto]** (2.10.1): JWT (JSON Web Token) 인코딩/디코딩 라이브러리

### 비동기 처리 & 스케줄링
- **aiofiles** (24.1.0): 파일 I/O를 위한 비동기 지원
- **aiosmtplib** (5.0.0): 비동기 SMTP 클라이언트 (이메일 전송)
- **apscheduler** (3.11.0): Python용 작업 스케줄링 라이브러리

### 설정 & 유틸리티
- **pydantic-settings** (2.10.1): Pydantic 기반 애플리케이션 설정 관리
- **loguru** (0.7.3): 간편하고 강력한 Python 로깅 라이브러리
- **pytz** (2024.1): Python 시간대 라이브러리
- **dependency-injector** (4.48.2): 의존성 주입 컨테이너 라이브러리

### 테스트
- **pytest** (8.4.2): Python 테스트 프레임워크

## 주요 기능
이 프로젝트는 다음과 같은 기능을 제공할 수 있습니다:
- RESTful API 및 WebSocket 통신
- 다중 데이터베이스 지원 (PostgreSQL, MongoDB, Redis)
- 비동기 작업 처리 및 스케줄링
- JWT 기반 인증
- LLM 통합 및 벡터 검색 (ChromaDB)
- AI 에이전트 플로우 관리 (LangGraph)
- 다중 LLM 모델 관리 (GPT-5, GPT-4o, GPT-4o-mini)
- 이메일 발송
- 실시간 통신

## 요구사항
- Python >= 3.12


## Directory Structure

```bash
backend/
├── migration/               # 데이터베이스 마이그레이션 관리 (Alembic)
│   ├── versions/            # 마이그레이션 버전 파일들
│   ├── env.py               # Alembic 환경 설정
│   ├── script.py.mako       # 마이그레이션 템플릿
│   └── README               # 마이그레이션 가이드
│
├── app/
│   ├── api/                 # REST API 엔드포인트 (라우터, 컨트롤러)
│   │   └── v1/              # API 버전별 디렉토리
│   │       ├── router.py    # 라우터 집합
│   │       └── user/        # 사용자 관련 엔드포인트
│   │
│   ├── config/              # 환경 변수 및 설정 관리
│   │   └── setting.py       # Pydantic 기반 Setting 객체
│   │
│   ├── core/                # 애플리케이션 핵심 모듈
│   │   ├── exception/       # Exception 핸들링 정의
│   │   │   └── handler.py   # 예외 처리 핸들러
│   │   ├── graph/           # AI 에이전트 그래프 플로우
│   │   │   └── example/     # 예제 AI 에이전트 구현
│   │   │       ├── chain_builder.py       # LangChain 체인 빌더
│   │   │       ├── graph_orchestrator.py  # LangGraph 오케스트레이션
│   │   │       ├── graph_state.py         # 그래프 상태 정의
│   │   │       └── prompt_manager.py      # 프롬프트 템플릿 관리
│   │   ├── lock/            # 분산 락 시스템
│   │   │   ├── base.py      # 분산 락 추상 클래스
│   │   │   └── redis_lock.py # Redis 기반 분산 락 구현
│   │   ├── chroma_manager.py # ChromaDB 벡터 데이터베이스 관리
│   │   ├── llm_manager.py    # OpenAI LLM 모델 관리
│   │   ├── logger.py        # 로깅 설정 및 유틸리티
│   │   └── redis.py         # Redis 클라이언트 관리
│   │
│   ├── database/            # 데이터베이스 관련 모듈
│   │   ├── model/           # ORM 모델 정의
│   │   │   ├── user.py      # 사용자 모델
│   │   │   └── log.py       # API 로그 모델 (MongoDB)
│   │   └── session.py       # 데이터베이스 세션 관리
│   │
│   ├── dto/                 # Data Transfer Object (Service 간 데이터 전달용)
│   │   └── user.py          # 사용자 DTO
│   │
│   ├── middleware/          # 미들웨어 (인증, 로깅, 예외 처리 등)
│   │   └── tracking.py      # 요청 추적 미들웨어
│   │
│   ├── repository/          # 데이터 접근 계층 (DB 쿼리, CRUD)
│   │   ├── user.py          # 사용자 리포지토리
│   │   └── log.py           # 로그 리포지토리 (MongoDB)
│   │
│   ├── schema/              # Request / Response 검증 스키마 (Pydantic)
│   │   └── user.py          # 사용자 스키마
│   │
│   ├── service/             # 비즈니스 로직 계층
│   │   └── user.py          # 사용자 서비스
│   │
│   ├── util/                # 공통 유틸리티 함수
│   │   ├── agent_assistant.py # AI 에이전트 헬퍼 함수
│   │   └── id_generator.py  # UUID 생성 유틸리티
│   │
│   ├── container.py         # 의존성 주입 (DI) 컨테이너 정의
│   └── main.py              # FastAPI 애플리케이션 진입점
│
├── data/                    # 영속화 데이터 저장소
│   ├── chromadb-data/       # ChromaDB 벡터 데이터베이스 저장 공간
│   │   ├── 8e0b3038.../     # 컬렉션별 데이터 파일
│   │   └── chroma.sqlite3   # ChromaDB 메타데이터
│   └── sqlite-data/         # LangGraph 메모리 저장소
│       └── example/         # 예제 에이전트용 SQLite DB
│           └── sqlite.db    # 대화 이력 저장
│
├── logs/                    # 애플리케이션 로그 파일
│   ├── app.log              # 현재 활성 로그 파일
│   ├── app.*.log            # 날짜별 롤테이션된 로그
│   └── app.*.log.gz         # 압축된 아카이브 로그
│
├── test/                    # 테스트 코드
│   └── README.md            # 테스트 가이드
│
├── Dockerfile               # Docker 이미지 빌드 설정
├── alembic.ini              # Alembic 설정 파일
├── pyproject.toml           # Python 프로젝트 설정
├── README.md                # 본 문서
└── uv.lock                  # 패키지 버전 잠금 파일


## 실행
### 1. 서비스 초기화
애플리케이션 시작 시 자동으로 다음 서비스들이 초기화됩니다:
- **PostgreSQL**: 메인 데이터베이스 연결
- **MongoDB**: 로그 저장소 연결 
- **Redis**: 캐싱 및 세션 저장소 연결
- **ChromaDB**: 벡터 임베딩 데이터베이스 초기화
- **LLM Manager**: OpenAI 모델 초기화

### 2. 실행 명령어
```bash
uv run python -m app.main
```

### 3. 헬스체크
서비스 상태는 `/health` 엔드포인트에서 확인할 수 있습니다:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "redis": "healthy"
  }
}
```

## AI 에이전트 시스템

### ChromaDB 관리자
싱글톤 패턴으로 구현된 벡터 데이터베이스 관리자로, 다음 기능을 제공합니다:
- 벡터 임베딩 저장 및 검색
- 컬렉션별 문서 관리
- 유사도 기반 검색
- OpenAI text-embedding-3-large 모델 사용

### LLM 관리자
다중 LLM 모델을 관리하는 싱글톤 매니저:
- GPT-5, GPT-4o, GPT-4o-mini 모델 지원
- 모델별 초기화 및 관리
- LangChain 통합

### LangGraph 기반 AI 에이전트
예제 AI 에이전트 플로우 싱글톤 구현:
- **GraphOrchestrator**: LangGraph 워크플로우 오케스트레이션
- **ChainBuilder**: LangChain 체인 구성 관리
- **PromptManager**: 프롬프트 템플릿 중앙 관리
- **GraphState**: 에이전트 상태 관리 (메시지, 문서, 답변)
- SQLite 기반 대화 이력 저장

## 분산 락 시스템

### Redis 기반 분산 락
분산 환경에서 동시성 제어를 위한 Redis 기반 락 시스템:
- **DistributedLock**: 분산 락을 위한 추상 기본 클래스
- **RedisLock**: Redis를 활용한 분산 락 구현체
- 컨텍스트별 토큰 관리로 안전한 락 소유권 보장
- Lua 스크립트를 통한 원자적 연산 지원

### 주요 기능
- **락 획득/해제**: 타임아웃 옵션과 TTL 설정 지원
- **락 연장**: 장시간 작업을 위한 TTL 연장 기능
- **소유권 검증**: 락 소유자만 해제/연장 가능
- **컨텍스트 매니저**: async with 구문으로 간편한 사용

### 사용 예시
```python
from app.core.lock import get_redis_lock

lock = get_redis_lock()

# 컨텍스트 매니저로 사용
async with lock.lock("critical_section", ttl=30) as acquired:
    if acquired:
        # 크리티컬 섹션 코드 실행
        await perform_critical_operation()
    else:
        logger.warning("Failed to acquire lock")

# 수동 락 관리
if await lock.acquire("resource_lock", ttl=60, timeout=5.0):
    try:
        await process_resource()
        # 필요시 TTL 연장
        await lock.extend("resource_lock", 30)
    finally:
        await lock.release("resource_lock")
```

## 로깅 시스템

### 환경 변수 설정
`.env` 파일에 다음 로깅 설정을 추가합니다:

```env
# 로깅 설정
LOG_LEVEL=INFO                        # 평소엔 INFO, 디버깅시 DEBUG
LOG_FORMAT=console                    # 개발환경: console, 운영: json
LOG_FILE_PATH=/backend/logs/app.log   # 컨테이너 내부 경로
LOG_ROTATION=100 MB                   # 100MB마다 새 파일
LOG_RETENTION=30 days                 # 30일 지난 로그 삭제
LOG_COMPRESSION=gz                    # 오래된 로그 압축
```

로그 파일 구조:
```
backend/
├── logs/
│   ├── app.log              # 현재 활성 로그
│   ├── app.2024-11-25.log   # 날짜별 롤테이션된 로그
│   └── app.2024-11-24.log.gz # 압축된 오래된 로그
```

### 환경별 설정

#### 개발 환경
```env
LOG_LEVEL=DEBUG
LOG_FILE_PATH=None  # 파일 저장 안함, 콘솔만
LOG_FORMAT=console
```

#### 스테이징/운영 환경
```env
LOG_LEVEL=INFO
LOG_FILE_PATH=/backend/logs/app.log
LOG_FORMAT=json  # 로그 수집 시스템 연동시
```

### 로그 모니터링

```bash
# 실시간 로그 모니터링 (컨테이너 로그)
docker logs -f letuin-backend

# 파일 로그 확인 (컨테이너 내부)
docker exec letuin-backend tail -f /backend/logs/app.log

# 호스트에서 직접 확인
tail -f ./backend/logs/app.log

# 특정 날짜 로그 확인
cat ./backend/logs/app.2024-11-25.log

# 압축된 로그 확인
zcat ./backend/logs/app.2024-11-24.log.gz
```

### 성능 최적화
- **비동기 로깅**: `enqueue=True`로 이미 설정되어 있어 비동기 처리됨
- **적절한 로그 레벨**: 운영 환경에서는 INFO 이상만 기록
- **자동 압축**: 오래된 로그는 gzip으로 압축하여 디스크 공간 절약
- **자동 삭제**: 보존 기간 설정으로 무한 증가 방지

### 보안 고려사항
- 민감한 정보(패스워드, 토큰, API 키) 로그 기록 금지
- 로그 파일 권한 관리 (755)
- 프로덕션 환경에서는 로그 수집 시스템 연동 권장

### 로그 포맷
#### Console 포맷 (개발용)
```
2024-11-25 12:00:00.123 | INFO     | app.api.v1.user:create:45 - User created: user_id=123
```

#### JSON 포맷 (운영용)
```json
{
  "timestamp": "2024-11-25T12:00:00.123Z",
  "level": "INFO",
  "logger": "app.api.v1.user",
  "function": "create",
  "line": 45,
  "message": "User created",
  "extra": {
    "user_id": 123
  }
}
```