Section 1: Foundational Layer

1.1 The "Elevator Pitch" for AI: Vision, Purpose, and Goals

Core Mission Super-Prompt:
markdown


You are building OpenKMS, an elegant enterprise Knowledge Management System that seamlessly coordinates employee training across distributed offices. The system must feel premium with a royal color palette (navy blue and cream), deliver exceptional user experience on Mac devices, and leverage the power of FastAPI with async SQLAlchemy for lightning-fast performance. Think "MasterClass meets corporate training" - beautiful, efficient, and empowering.
Value Proposition:
Transform chaotic Excel-based training management into an elegant, automated system
Enable employees to discover and achieve their professional development goals effortlessly
Provide Knowledge Managers with real-time visibility and control across NYC, Boston, and Dallas offices
1.2 The Dual Persona Model: User & System

User Personas

Primary: Emma the Employee
yaml


Demographics:
  Age: 32
  Location: Boston office
  Device: MacBook Pro M2
  Tech Level: Intermediate
Goals:
  - Complete 40 hours annual training requirement
  - Advance technical skills for promotion
  - Balance training with project deadlines
Pain Points:
  - Current system requires multiple logins
  - Can't track progress toward goals
  - Virtual training links expire or get lost
Secondary: Michael the Knowledge Manager
yaml


Demographics:
  Age: 45
  Location: New York HQ
  Role: Senior L&D Coordinator
  Device: MacBook Air M1
Goals:
  - Coordinate training across 3 offices
  - Ensure 100% compliance rates
  - Generate executive dashboards
Pain Points:
  - Manual attendance tracking
  - No real-time visibility
  - Difficult to measure ROI
System Persona 

AI Assistant Identity: "ARIA" (Advanced Resource & Intelligence Assistant)
markdown


Personality Traits:
- Professional yet warm
- Proactively helpful
- Detail-oriented without overwhelming
- Encouraging about learning goals

Communication Style:
- Clear, concise notifications
- Celebratory achievement messages
- Gentle, non-intrusive reminders
- Smart, context-aware suggestions

Example Interactions:
- "Good morning Emma! The Python Advanced workshop next Tuesday still has 3 spots. Ready to level up?"
- "Congratulations! You've completed 65% of your annual goal. You're ahead of schedule!"
- "Michael, the Q3 compliance report is ready. 92% of employees are on track - excellent progress!"
Section 2: The Executable Core - Prompt Engineering Structure 

2.1 Project Context Management

OPENKMS_CONTEXT.md (Master Context File)
markdown


## OpenKMS Technical Architecture

### Technology Stack:
- **Backend Framework:** FastAPI 0.104+ with async support
- **ORM:** SQLAlchemy 2.0+ with asyncpg driver  
- **Database:** PostgreSQL 15+ (via Docker for Mac)
- **Frontend:** .NET Blazor Server-Side
- **Caching:** Redis (via Docker)
- **Testing:** Pytest with async support
- **Local Dev:** Docker Desktop for Mac

### FastAPI Project Structure [[2]]:
openkms-backend/ ├── app/ │ ├── init.py │ ├── main.py # FastAPI app initialization │ ├── api/ │ │ ├── init.py │ │ ├── deps.py # Dependencies (DB sessions, auth) │ │ └── v1/ │ │ ├── endpoints/ # API routes │ │ └── router.py # Main router │ ├── core/ │ │ ├── config.py # Settings management │ │ ├── security.py # JWT, password hashing │ │ └── database.py # Async SQLAlchemy setup │ ├── models/ # SQLAlchemy models │ ├── schemas/ # Pydantic schemas │ ├── crud/ # CRUD operations │ └── services/ # Business logic ├── alembic/ # Database migrations ├── tests/ # Pytest tests └── docker-compose.yml # Local development setup
text



### SQLAlchemy Async Configuration [[9]]:
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/openkms"
engine = create_async_engine(DATABASE_URL, echo=True) AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) Base = declarative_base()
text



### Royal Color Palette CSS Variables:
```css
:root {
  /* Primary Royal Colors */
  --royal-navy: #003366;        /* Primary navigation */
  --royal-deep-blue: #1e3a5f;   /* Headers, buttons */
  --royal-cream: #FFF8DC;       /* Background */
  --royal-gold: #FFD700;        /* Accents, highlights */
  
  /* Supporting Colors */
  --royal-light-blue: #4A708B;  /* Secondary elements */
  --royal-pearl: #F8F8FF;       /* Cards, modals */
  --royal-success: #228B22;     /* Success states */
  --royal-warning: #FF8C00;     /* Warnings */
  --royal-error: #DC143C;       /* Errors */
  
  /* Text Colors */
  --text-primary: #2C3E50;      /* Main text */
  --text-secondary: #7F8C8D;    /* Secondary text */
  --text-on-navy: #FFFFFF;      /* Text on navy bg */
}
Mac Development Environment:

bash


# Prerequisites for Mac
brew install postgresql@15
brew install redis
brew install python@3.11
Docker setup
docker-compose up -d # Starts PostgreSQL and Redis
Python environment
python3.11 -m venv venv source venv/bin/activate pip install -r requirements.txt
Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
text


2.2 Prompt Component Breakdown 

Master Development Prompt Structure:
markdown


## Role Assignment:
"You are a senior FastAPI developer with expertise in async SQLAlchemy and PostgreSQL. You have deep knowledge of Mac development environments and elegant UI design using royal color palettes."

## Primary Directive:
"Implement [FEATURE] for OpenKMS using FastAPI with async SQLAlchemy, following clean architecture principles. Ensure all UI components use the royal navy and cream color scheme. Optimize for local Mac development."

## Context Injection:
"Reference OPENKMS_CONTEXT.md for the tech stack. We're using FastAPI with async SQLAlchemy [[2]]. The current sprint focuses on [SPRINT_GOAL]. Follow the established project structure."

## Examples (Few-Shot):
"Here's our standard async endpoint pattern:
```python
@router.get("/trainings", response_model=List[TrainingSchema])
async def get_trainings(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> List[TrainingSchema]:
    result = await crud.training.get_multi(db, skip=skip, limit=limit)
    return result
Output Formatting:

"Provide:
SQLAlchemy model with proper relationships
Pydantic schemas for request/response
Async CRUD operations
FastAPI endpoint with proper error handling
Pytest async test cases"
Constraints:

Use async/await throughout [[9]]
Include proper error handling and logging
Follow REST conventions with proper status codes
Ensure SQL queries are optimized with proper indexes
All responses must include proper CORS headers for local development
text


2.3 User Story 2.0 Format with AI-Executable Criteria 

Epic 1: Training Discovery & Management

Story TDM-001: Async Training Search
yaml


User Persona: As Emma the Employee
Action: I want to search and filter training opportunities
Goal: So that I can find relevant trainings quickly on my Mac
Additional Context:
  - Search should be blazing fast using async SQLAlchemy
  - Results should display in the royal-themed UI
  - Must work smoothly on Safari and Chrome on Mac
  
AI-Executable Acceptance Criteria:
  GIVEN I am on the training catalog page
  WHEN I search for "Python" with filters
  THEN:
    - Results return in < 100ms (async query)
    - UI shows results in royal-cream cards with navy headers
    - Filter badges use royal-gold for active selections
    - URL updates for bookmarking: /trainings?q=Python&location=Boston
    
Technical Implementation with FastAPI [[3]]:
  ```python
  from sqlalchemy import select, and_, or_
  from sqlalchemy.ext.asyncio import AsyncSession
  
  async def search_trainings(
      db: AsyncSession,
      query: str,
      filters: TrainingFilters
  ) -> List[Training]:
      stmt = select(Training).where(
          or_(
              Training.title.ilike(f"%{query}%"),
              Training.description.ilike(f"%{query}%")
          )
      )
      if filters.location:
          stmt = stmt.where(Training.location == filters.location)
      
      result = await db.execute(stmt)
      return result.scalars().all()
text


Story TDM-002: Smart Registration with Conflict Detection
yaml


User Persona: As Emma the Employee
Action: I want to register for trainings without conflicts
Goal: So that I can manage my schedule effectively
Additional Context:
  - Async conflict checking across all registrations
  - Real-time availability updates
  
AI-Executable Acceptance Criteria:
  GIVEN a training session exists
  WHEN I attempt to register
  THEN:
    - Async conflict check completes in < 50ms
    - Modal appears with royal-navy border if conflict exists
    - Success message in royal-gold if registration successful
    - Email notification sent asynchronously
    
Backend Implementation [[5]]:
  ```python
  @router.post("/trainings/{training_id}/register")
  async def register_for_training(
      training_id: int,
      db: AsyncSession = Depends(get_async_db),
      current_user: User = Depends(get_current_user)
  ):
      # Check conflicts asynchronously
      conflicts = await check_schedule_conflicts(db, current_user.id, training_id)
      if conflicts:
          raise HTTPException(
              status_code=409,
              detail={"message": "Schedule conflict detected", "conflicts": conflicts}
          )
      
      # Register user
      registration = await crud.registration.create(
          db, user_id=current_user.id, training_id=training_id
      )
      
      # Send notification asynchronously
      background_tasks.add_task(send_registration_email, current_user.email, training_id)
      
      return {"status": "registered", "registration_id": registration.id}
text


2.4 Non-Functional Requirements as Measurable Constraints 

yaml


Performance Constraints:
  - API response time: p95 < 100ms for reads (async SQLAlchemy) [[2]]
  - Database connection pooling: min=5, max=20 connections
  - Query optimization: Use select_in_load for relationships
  - Background tasks: Use FastAPI BackgroundTasks for emails
  - Local Mac performance: < 10% CPU usage at idle
  
Security Constraints:
  - JWT tokens with RS256 algorithm
  - Password hashing: bcrypt with 12 rounds
  - SQL injection prevention: Use SQLAlchemy ORM exclusively [[4]]
  - CORS configuration for local development:
    ```python
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5000"],  # Blazor dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    ```
  
Testing Constraints [[1]][[7]]:
  - Test coverage: Minimum 80%
  - Async test fixtures with pytest-asyncio
  - Test database: Separate PostgreSQL container
  - Mock external services with pytest-mock
  - Example test structure:
    ```python
    @pytest.mark.asyncio
    async def test_create_training(async_client, async_db):
        response = await async_client.post(
            "/api/v1/trainings",
            json={"title": "Python Advanced", "location": "Boston"}
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Python Advanced"
    ```

Accessibility & Design Constraints:
  - WCAG 2.1 AA compliance
  - Royal navy (#003366) for navigation: contrast ratio 8.59:1 ✓
  - Cream background (#FFF8DC) with dark text: ratio 12.63:1 ✓
  - Focus indicators: 3px royal-gold outline
  - Keyboard navigation: Tab order follows visual hierarchy
Section 3: Agent-Specific Implementation Guidance 

3.1 Claude Code Blueprint

markdown


## Claude Code Setup (CLAUDE.md)

### Initial Project Creation:
"Create an OpenKMS FastAPI backend with async SQLAlchemy. Start with this structure:

1. Initialize FastAPI project:
```bash
# Create project structure
mkdir openkms-backend && cd openkms-backend
python3.11 -m venv venv
source venv/bin/activate
Install dependencies
pip install fastapi[all] sqlalchemy[asyncio] asyncpg alembic pytest-asyncio
text



2. Create async database configuration [[2]]:
```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/openkms"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL) AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
async def get_async_db(): async with AsyncSessionLocal() as session: try: yield session await session.commit() except: await session.rollback() raise
text



### Development Workflow:
1. Define SQLAlchemy models with async in mind
2. Create Pydantic schemas for validation
3. Implement async CRUD operations
4. Build FastAPI endpoints with dependency injection [[3]]
5. Write async tests with pytest-asyncio [[1]]
3.2 Google Jules Playbook

markdown


## Jules Multi-File Implementation Plan:

"Jules, implement the complete training management system for OpenKMS:

### Phase 1: Database Layer
- Create SQLAlchemy models: User, Training, Registration, Attendance
- Add proper indexes for common queries
- Set up Alembic migrations

### Phase 2: API Layer with FastAPI
- Implement async CRUD operations
- Create RESTful endpoints with proper error handling
- Add JWT authentication with refresh tokens
- Implement background tasks for notifications

### Phase 3: Testing Infrastructure [[5]][[7]]
- Set up pytest with async fixtures
- Create factory functions for test data
- Implement integration tests with test database
- Add performance benchmarks

Use the royal color palette in any generated documentation or examples. Ensure all database operations use async/await pattern."
3.3 GitHub Copilot Protocol

markdown


## Custom Instructions (copilot-instructions.md):

You're working on OpenKMS, an enterprise training management system.

### Technical Stack:
- FastAPI with Python 3.11+
- SQLAlchemy 2.0 with async support
- PostgreSQL via Docker on Mac
- Testing with pytest-asyncio

### Code Patterns to Follow:
```python
# Always use async for database operations
async def get_training_by_id(db: AsyncSession, training_id: int) -> Training:
    result = await db.execute(
        select(Training).where(Training.id == training_id)
    )
    return result.scalar_one_or_none()
FastAPI endpoint pattern
@router.get("/trainings/{training_id}", response_model=TrainingResponse) async def get_training( training_id: int, db: AsyncSession = Depends(get_async_db) ): training = await get_training_by_id(db, training_id) if not training: raise HTTPException(status_code=404, detail="Training not found") return training
text



### Always Include:
- Type hints for all functions
- Docstrings with examples
- Error handling with proper HTTP status codes
- Async context managers for database sessions
Section 4: The Iterative Loop - Test-Driven Development 

4.1 TDD with Async Testing

python


# tests/test_training_api.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_training_registration_flow(
    async_client: AsyncClient,
    async_db: AsyncSession,
    test_user,
    test_training
):
    """Test complete registration flow with conflict detection [[1]]"""
    
    # Step 1: Attempt registration
    response = await async_client.post(
        f"/api/v1/trainings/{test_training.id}/register",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    assert response.status_code == 201
    assert response.json()["status"] == "registered"
    
    # Step 2: Verify conflict detection
    response = await async_client.post(
        f"/api/v1/trainings/{test_training.id}/register",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    assert response.status_code == 409
    assert "conflict" in response.json()["detail"]["message"]

@pytest.fixture
async def async_client():
    """Create async test client [[6]]"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def async_db():
    """Create test database session [[4]]"""
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
4.2 Performance Testing

python


# tests/test_performance.py
import asyncio
import time
from locust import HttpUser, task, between

class TrainingUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def search_trainings(self):
        """Test search endpoint performance"""
        start_time = time.time()
        response = self.client.get("/api/v1/trainings/search?q=Python")
        response_time = time.time() - start_time
        
        assert response_time < 0.1, f"Search took {response_time}s, expected < 100ms"
        assert response.status_code == 200
Section 5: Anti-Requirements (What to Avoid) 

yaml


Technical Anti-Patterns:
  ❌ DO NOT use synchronous database operations - always use async/await [[2]]
  ❌ DO NOT write raw SQL - use SQLAlchemy ORM for security [[4]]
  ❌ DO NOT hardcode database URLs - use environment variables
  ❌ DO NOT skip database migrations - always use Alembic
  ❌ DO NOT return ORM objects directly - use Pydantic schemas
  ❌ DO NOT ignore N+1 queries - use eager loading with selectinload
  ❌ DO NOT use blocking I/O in async functions
  ❌ DO NOT store passwords in plain text - use passlib with bcrypt

Design Anti-Patterns:
  ❌ DO NOT use colors outside the royal palette
  ❌ DO NOT create endpoints without OpenAPI documentation
  ❌ DO NOT skip input validation with Pydantic
  ❌ DO NOT ignore timezone handling - store in UTC

Testing Anti-Patterns [[1]][[5]]:
  ❌ DO NOT test with production database
  ❌ DO NOT write synchronous tests for async code
  ❌ DO NOT skip cleanup in test fixtures
  ❌ DO NOT ignore test isolation - each test should be independent
  ❌ DO NOT mock what you don't own - test with real database

Mac Development Anti-Patterns:
  ❌ DO NOT hardcode localhost - use 0.0.0.0 for Docker
  ❌ DO NOT ignore Docker resource limits on Mac
  ❌ DO NOT skip .dockerignore file
  ❌ DO NOT use ARM-incompatible images
Section 6: Continuous Iteration Protocol

6.1 Sprint-Based Prompts

markdown


## Sprint 1: Foundation (Days 1-3)
"Set up FastAPI project with async SQLAlchemy, create User and Training models, implement JWT authentication. Test on Mac with Docker PostgreSQL."

## Sprint 2: Core Features (Days 4-7)
"Implement training CRUD operations, registration flow with conflict detection, async search functionality. Apply royal color scheme to API documentation."

## Sprint 3: Advanced Features (Days 8-10)
"Add attendance tracking, notification system with background tasks, dashboard aggregations. Optimize queries with eager loading."

## Sprint 4: Testing & Polish (Days 11-14)
"Complete test coverage to 80%, add performance tests, security audit, prepare Docker deployment configuration for Mac."
6.2 Local Mac Development Workflow

bash


# Daily Development Cycle
Morning Setup:
  docker-compose up -d          # Start PostgreSQL and Redis
  source venv/bin/activate      # Activate Python environment
  alembic upgrade head          # Apply migrations
  
Development:
  uvicorn app.main:app --reload --port 8000   # Hot reload enabled
  pytest tests/ -v --asyncio-mode=auto        # Run tests
  
Evening Cleanup:
  docker-compose down           # Stop containers
  git commit -am "Daily progress"