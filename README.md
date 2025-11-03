# Server 스팩

## 의존성 라이브러리 설명

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
- **langchain-chroma** (1.0.0): Chroma 벡터 데이터베이스와 LangChain 통합
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

## 주요 기능
이 프로젝트는 다음과 같은 기능을 제공할 수 있습니다:
- RESTful API 및 WebSocket 통신
- 다중 데이터베이스 지원 (PostgreSQL, MongoDB, Redis)
- 비동기 작업 처리 및 스케줄링
- JWT 기반 인증
- LLM 통합 및 벡터 검색
- 이메일 발송
- 실시간 통신

## 요구사항
- Python >= 3.12