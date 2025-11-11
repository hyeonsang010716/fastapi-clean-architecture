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