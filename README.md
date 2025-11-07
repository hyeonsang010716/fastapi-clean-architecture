# Production-Ready FastAPI Template

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.118.0-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-blue.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-Ready-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)

**A production-ready FastAPI template featuring clean architecture, dependency injection patterns, Alembic migrations, and organized project structure for scalable API development.**

[🌟 **Give it a Star!**](#star-this-repo) • [📖 Documentation](#documentation) • [🛠️ Quick Start](#quick-start) • [🧪 Testing](#testing--quality-assurance)

</div>

---

## Why Choose This Template?

- **Production-Ready**: Battle-tested patterns and enterprise-grade architecture  
- **Clean Architecture**: Properly separated layers (API → Service → Repository → Database)  
- **Dependency Injection**: Type-safe DI with `dependency-injector` for better testability  
- **Comprehensive Testing**: Unit & Integration tests with 90%+ coverage  
- **Database Migrations**: Seamless schema evolution with Alembic  
- **Dual Database**: PostgreSQL for data + MongoDB for logs & analytics  
- **Modern Stack**: FastAPI + SQLAlchemy 2.0 + Beanie + Python 3.12+  
- **Developer Experience**: Extensive documentation and type hints everywhere  

## Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- PostgreSQL (or use Docker)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/production-fastapi-template.git
cd production-fastapi-template
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit your environment variables
nano .env
```

### 3. Start with Docker
```bash
# Start all services (API + PostgreSQL + MongoDB + Redis)
docker-compose up -d

# Or run locally
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv install
uv run python -m app.main
```

### 4. Verify Installation
```bash
# Check API health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

🎉 **That's it!** Your production-ready API is running!

## Architecture Overview

```
├── API Layer          # FastAPI routers & endpoints
├── Service Layer      # Business logic & validation  
├── Repository Layer   # Database operations & queries
├── Database Layer     # Dual DB: PostgreSQL (main) + MongoDB (logs)
├── Middleware Layer   # Request tracking, logging, security
└── Testing Layer     # Unit & Integration tests
```

### Project Structure
```bash
backend/
├── app/
│   ├── api/v1/           # REST API endpoints
│   ├── config/           # Environment & settings  
│   ├── service/          # Business logic
│   ├── repository/       # Data access layer
│   ├── database/         # Models & session management
│   ├── schema/           # Pydantic request/response models
│   ├── dto/              # Data transfer objects
│   └── container.py      # Dependency injection setup
├── test/
│   ├── unit/             # Fast unit tests with mocks
│   └── ntegration/      # Full-stack integration tests
├── migration/            # Database migration scripts
└── Dockerfile           # Production container setup
```

## Key Features

### **Clean Architecture Pattern**
```python
# Properly separated concerns
API Layer → Service Layer → Repository Layer → Database

# Example: User creation flow
@router.post("/users")                    # API Layer
async def create_user(data: UserCreate):
    return await user_service.create(data) # Service Layer
    
class UserService:
    async def create(self, data):
        return await user_repo.create(data) # Repository Layer
```

### **Dependency Injection**
```python
# Type-safe DI container
container = Container()
container.user_service()  # Automatically resolves dependencies
container.user_repository() 

### **Production-Grade Testing**
```python
# DI-based unit tests (no @patch needed!)
@pytest.fixture
def user_service_with_di(mock_user_repository, service_di_factory):
    return service_di_factory(UserService, "app.service.user", {
        "UserRepository": mock_user_repository
    })

# Integration tests with real database
async def test_user_creation_full_flow(test_db):
    # Tests complete flow: API → Service → Repository → Database
```

### **Database Migrations**
```bash
# Auto-generate migrations from model changes
alembic revision --autogenerate -m "Add user table"

# Apply migrations
alembic upgrade head

# Production-ready migration workflow
```

### **Dual Database Architecture**
```python
# PostgreSQL for relational data
async with AsyncSession() as session:
    user = await user_repository.create(user_data)

# MongoDB for logs & analytics
@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    await LogRepository.create(
        called_api=request.url.path,
        status_code=response.status_code,
        response_time=response.headers["X-Process-Time"]
    )
```

### **AI & LLM Ready**
```python
# Built-in LangChain integration
from langchain_openai import OpenAI
from app.service.ai import AIService

ai_service = AIService()
response = await ai_service.chat("Hello, AI!")
```

## Testing & Quality Assurance

### **Fast Unit Tests**
```bash
# Run lightning-fast unit tests
uv run pytest -m unit           # ~100ms per test

# DI-based mocking (no monkey patching!)
uv run pytest test/unit/
```

### **Integration Tests**
```bash
# Full-stack testing with real database
uv run pytest -m integration

# Test complete workflows
uv run pytest test/integration/
```

### **Test Coverage**
```bash
# Generate coverage report
uv run pytest --cov=app --cov-report=html

# Aim for 90%+ coverage
open htmlcov/index.html
```

### **Test Factory Pattern**
```python
# Extensible test factories for any service
@pytest.fixture
def any_service_with_di(mock_repository_factory, service_di_factory):
    return service_di_factory(
        AnyService,
        "app.service.any", 
        {"AnyRepository": mock_repository_factory(...)}
    )
```

## Database & Migrations

### **PostgreSQL + SQLAlchemy 2.0**
```python
# Modern async database patterns
async with AsyncSession() as session:
    users = await session.execute(select(User))
```

### **Alembic Migrations**
```bash
# 1. Modify your models
class User(Base):
    phone = Column(String)  # Add new field

# 2. Generate migration
alembic revision --autogenerate -m "Add phone field"

# 3. Apply to database  
alembic upgrade head
```

### **Docker Development**
```bash
# Complete development environment
docker-compose up -d  # PostgreSQL + MongoDB + Redis + API

# Container-based migrations
docker exec -it api-container alembic upgrade head

## Tech Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| **API Framework** | FastAPI 0.118.0 | High-performance async API |
| **Database** | PostgreSQL + SQLAlchemy 2.0 | Relational data with async ORM |
| **NoSQL Database** | MongoDB + Beanie | API logs & unstructured data |
| **Cache** | Redis | Session storage & caching |
| **Migrations** | Alembic | Schema version control |
| **Testing** | pytest + pytest-asyncio | Unit & integration testing |
| **DI Container** | dependency-injector | Type-safe dependency injection |
| **AI/ML** | LangChain + OpenAI | LLM integration ready |
| **Validation** | Pydantic | Request/response validation |
| **Authentication** | JWT + Passlib | Secure token-based auth |
| **Logging** | Loguru + MongoDB | Structured logging & API analytics |
| **Deployment** | Docker + uv | Containerized deployment |

## Documentation

Comprehensive guides for every aspect:

- **[Backend Setup](backend/README.md)** - Complete backend configuration
- **[Testing Guide](backend/test/README.md)** - Unit & integration testing 
- **[Migration Guide](backend/migration/README.md)** - Database migrations
- **[Docker Guide](docker-compose.yml)** - Container orchestration

### Development Checklist
- [ ] Add unit tests for new features
- [ ] Update integration tests if needed
- [ ] Run `uv run pytest` (all tests pass)
- [ ] Update documentation
- [ ] Follow clean architecture patterns

---

<div align="center">

**Made with ❤️ for the Python community**

**Don't forget to ⭐ star this repository if you found it useful!**

[🔝 Back to Top](#-production-ready-fastapi-template)

</div>