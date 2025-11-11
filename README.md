# Production-Ready FastAPI Template

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.118.0-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-blue.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-Ready-green.svg)
![Redis](https://img.shields.io/badge/Redis-Ready-red.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-Ready-orange.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Ready-green.svg)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Ready-purple.svg)

**A production-ready FastAPI template featuring clean architecture, dependency injection patterns, Alembic migrations, AI/LLM integration, and organized project structure for scalable API development.**

[🛠️ Quick Start](#quick-start) • [🧪 Testing](#testing--quality-assurance)

</div>

---

## Why Choose This Template?

- **Production-Ready**: Battle-tested patterns and enterprise-grade architecture  
- **Clean Architecture**: Properly separated layers (API → Service → Repository → Database)  
- **Dependency Injection**: Type-safe DI with `dependency-injector` for better testability  
- **Comprehensive Testing**: Unit & Integration tests with 90%+ coverage  
- **Database Migrations**: Seamless schema evolution with Alembic  
- **Dual Database**: PostgreSQL for data + MongoDB for logs & analytics  
- **AI/LLM Integration**: LangChain + ChromaDB + LangGraph for intelligent applications  
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

**Required AI/LLM Variables:**
```env
# OpenAI API Configuration
OPENAI_API_KEY=your-api-key-here
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

# Expected response:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "services": {
#     "redis": "healthy"
#   }
# }

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
│   ├── core/             # Core application modules
│   │   ├── graph/        # LangGraph AI agent workflows
│   │   ├── chroma_manager.py # ChromaDB vector store
│   │   ├── llm_manager.py    # LLM model management
│   │   ├── logger.py     # Logging configuration
│   │   └── redis.py      # Redis client
│   ├── service/          # Business logic
│   ├── repository/       # Data access layer
│   ├── database/         # Models & session management
│   ├── schema/           # Pydantic request/response models
│   ├── dto/              # Data transfer objects
│   ├── util/             # Helper utilities
│   │   └── agent_assistant.py # AI agent helpers
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
```

### **Automatic API Logging**
```python
# Every API call is automatically logged to MongoDB
# GET /api/v1/users → MongoDB Log Document:
{
    "created_at": "2024-01-01T12:00:00Z",
    "called_api": "/api/v1/users",
    "method": "GET",
    "status_code": 200,
    "response_time": 45.23,  # milliseconds
    "ip_address": "127.0.0.1"
}
```

### **Redis Caching & Session Management**
```python
# Built-in Redis client with automatic connection management
from app.core.redis import get_redis_client

# Use for caching
redis = await get_redis_client()
await redis.set("user:123", user_data, ex=3600)

# Session management
await redis.hset("session:abc123", mapping={
    "user_id": "123",
    "last_access": datetime.now()
})
```

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

### **AI & LLM Integration**

#### **ChromaDB Vector Store**
```python
# Singleton ChromaDB manager for vector embeddings
from app.core.chroma_manager import ChromaManager

chroma = ChromaManager.get_instance()

# Store document embeddings
await chroma.add_documents(
    collection_name="knowledge_base",
    documents=["Document content..."],
    metadata=[{"source": "api_docs"}]
)

# Semantic search
results = await chroma.search(
    collection_name="knowledge_base",
    query="How to implement authentication?",
    k=5
)
```

#### **Multi-Model LLM Management**
```python
# Singleton LLM manager supporting multiple models
from app.core.llm_manager import LLMManager

llm_manager = LLMManager.get_instance()

# Get specific model
gpt5 = llm_manager.get_llm("gpt-5")
gpt4o = llm_manager.get_llm("gpt-4o")
gpt4o_mini = llm_manager.get_llm("gpt-4o-mini")

# Use in chains
response = await gpt5.ainvoke("Explain quantum computing")
```

#### **LangGraph AI Agents**
```python
# Example AI agent with stateful workflow
from app.core.graph.example import GraphOrchestrator

orchestrator = GraphOrchestrator.get_instance()

# Run agent workflow
result = await orchestrator.run_graph({
    "messages": [{"role": "user", "content": "Analyze this data"}],
    "documents": ["doc1", "doc2"]
})

# Access conversation history (SQLite persisted)
history = await orchestrator.get_conversation_history()
```

#### **Agent Components**
- **GraphOrchestrator**: Manages LangGraph workflows with state persistence
- **ChainBuilder**: Constructs LangChain chains for different tasks
- **PromptManager**: Centralized prompt template management
- **GraphState**: Manages agent state (messages, documents, answers)

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

# View MongoDB logs
docker exec -it mongodb-container mongosh
> use your_db_name
> db.log.find().sort({created_at: -1}).limit(10)

# Access Redis CLI
docker exec -it redis-container redis-cli
> KEYS *
> GET "user:123"

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
| **AI/ML** | LangChain + OpenAI | LLM integration & orchestration |
| **Vector DB** | ChromaDB | Semantic search & embeddings |
| **AI Workflow** | LangGraph | Stateful AI agent workflows |
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