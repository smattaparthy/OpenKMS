# OpenKMS Development Guide

This guide provides comprehensive information for developers working on the OpenKMS project.

## Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Docker 20.10+**
- **Docker Compose 2.0+**
- **Git**

### First-Time Setup

1. **Clone the repository**
```bash
git clone https://github.com/your-org/openkms.git
cd openkms
```

2. **Set up the development environment**
```bash
chmod +x scripts/*.sh
./scripts/check-environment.sh
./scripts/dev-setup.sh
```

3. **Start the application**
```bash
./scripts/dev-commands.sh start
```

4. **Access the application**
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development Workflow

### Environment Management

#### Check Environment Status
```bash
./scripts/check-environment.sh
```

#### Start Development Environment
```bash
./scripts/dev-commands.sh start
```

#### Stop Development Environment
```bash
./scripts/dev-commands.sh stop
```

#### Check Service Status
```bash
./scripts/dev-commands.sh status
```

### Development Features

#### Hot Reload
- **Backend**: Automatically reloads on code changes
- **Frontend**: Requires restart: `./scripts/dev-commands.sh restart frontend`

#### Live Logs
```bash
# View all logs
./scripts/dev-commands.sh logs

# View specific service logs
./scripts/dev-commands.sh logs-backend
./scripts/dev-commands.sh logs-frontend
./scripts/dev-commands.sh logs-db
```

#### Shell Access
```bash
# Access backend shell
./scripts/dev-commands.sh shell-backend

# Access frontend shell
./scripts/dev-commands.sh shell-frontend

# Access database shell
./scripts/dev-commands.sh shell-db
```

### Code Development

#### Backend Development

The backend uses FastAPI with async SQLAlchemy. Here's how to work with it:

1. **Access the backend container**
```bash
./scripts/dev-commands.sh shell-backend
```

2. **The project structure:**
```
openkms-backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core configuration and utilities
│   │   ├── config.py          # Application configuration
│   │   └── security.py        # Security utilities
│   ├── models/                 # SQLAlchemy models
│   │   └── user.py           # User model example
│   ├── schemas/               # Pydantic schemas
│   │   └── user.py           # User schemas
│   ├── api/                    # API endpoints
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   └── auth.py   # Authentication endpoints
│   │   │   └── deps.py       # Dependencies
│   └── services/              # Business logic
│       └── auth.py           # Authentication service
├── alembic/                   # Database migrations
├── tests/                     # Test files
├── requirements.txt           # Python dependencies
└── Dockerfile.dev            # Development Dockerfile
```

3. **Common development tasks:**

   **Running tests:**
   ```bash
   ./scripts/dev-commands.sh test-backend
   ```

   **Database migrations:**
   ```bash
   ./scripts/dev-commands.sh migrate      # Run migrations
   ./scripts/dev-commands.sh migrate-new   # Create new migration
   ./scripts/dev-commands.sh migrate-down  # Rollback migration
   ```

   **Code formatting:**
   ```bash
   # In backend shell
   black app/
   flake8 app/
   ```

#### Frontend Development

The frontend uses Blazor Server with C#. Here's how to work with it:

1. **Access the frontend container**
```bash
./scripts/dev-commands.sh shell-frontend
```

2. **The project structure:**
```
openkms-frontend/
├── OpenKMS.Frontend.csproj    # Project file
├── Program.cs                 # Application entry point
├── appsettings.json           # Application settings
├── Pages/                     # Blazor pages
│   ├── Index.razor           # Home page
│   ├── Auth/
│   │   ├── Login.razor       # Login page
│   │   └── Register.razor    # Register page
│   └── Admin/
│       └── Dashboard.razor  # Admin dashboard
├── Shared/                    # Shared components
│   ├── MainLayout.razor      # Main layout
│   ├── NavMenu.razor        # Navigation menu
│   └── _Imports.razor       # Global imports
├── Services/                  # Application services
│   ├── AuthService.cs        # Authentication service
│   └── BaseApiService.cs    # Base API service
├── Models/                    # Data models
│   └── Requests/
│       └── UserLoginRequest.cs
└── Handlers/                 # HTTP handlers
    └── AuthDelegatingHandler.cs
```

3. **Common development tasks:**

   **Running tests:**
   ```bash
   ./scripts/dev-commands.sh test-frontend
   ```

   **Building the application:**
   ```bash
   # In frontend shell
   dotnet build
   ```

   **Running specific tests:**
   ```bash
   # In frontend shell
   dotnet test --filter "DisplayName~LoginTests"
   ```

### Database Development

#### Database Schema
The application uses PostgreSQL with the following main tables:

- `users` - User accounts and authentication
- `training_programs` - Training program definitions
- `training_schedules` - Training schedule instances
- `training_registrations` - User registrations
- `training_materials` - Training materials
- `knowledge_articles` - Knowledge base articles

#### Database Access

```bash
# Access database shell
./scripts/dev-commands.sh shell-db

# View all tables
\dt

# View table schema
\d users

# Execute SQL queries
SELECT * FROM users LIMIT 10;
```

#### Database Backups

```bash
# Create backup
./scripts/dev-commands.sh backup

# Restore from backup
./scripts/dev-commands.sh restore /path/to/backup.sql
```

### Testing

#### Backend Tests

The backend uses pytest for testing:

```bash
# Run all tests
./scripts/dev-commands.sh test-backend

# Run specific test file
./scripts/dev-commands.sh shell-backend
pytest tests/unit/test_auth_service.py

# Run tests with coverage
pytest --cov=app --cov-report=html
```

#### Frontend Tests

The frontend uses xUnit with bUnit for Blazor testing:

```bash
# Run all tests
./scripts/dev-commands.sh test-frontend

# Run specific test
./scripts/dev-commands.sh shell-frontend
dotnet test --filter "TestCategory=Unit"

# Run tests with coverage
dotnet test --collect:"XPlat Code Coverage"
```

### Environment Configuration

#### Development Environment Variables

The `.env` file contains development configuration:

```bash
# Database
POSTGRES_PASSWORD=dev_password
DATABASE_URL=postgresql://openkms:dev_password@postgres:5432/openkms

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256

# Application
DEBUG=True
LOG_LEVEL=DEBUG
 ALLOWED_HOSTS=localhost,127.0.0.1

# URLs
FRONTEND_URL=http://localhost:8080
BACKEND_URL=http://localhost:8000
```

#### Custom Configuration

To override development settings:

1. Create a `.env.override` file
2. Add your custom configuration
3. Restart the services

### Debugging

#### Backend Debugging

1. **Use pdb for debugging:**
```bash
# In backend shell
python -m pdb your_script.py
```

2. **Add debug prints:**
```python
import logging
logging.info(f"Debug: {variable}")
```

3. **Check logs:**
```bash
./scripts/dev-commands.sh logs-backend
```

#### Frontend Debugging

1. **Use Visual Studio Code debugging:**
   - Install the C# extension
   - Attach to the container

2. **Browser developer tools:**
   - Open Chrome DevTools (F12)
   - Check Console for errors
   - Use Network tab to inspect API calls

3. **Check server logs:**
```bash
./scripts/dev-commands.sh logs-frontend
```

### Common Development Tasks

#### Adding New Features

1. **Backend:**
   ```bash
   # Access backend shell
   ./scripts/dev-commands.sh shell-backend

   # Create new model
   # Edit app/models/new_model.py

   # Create new schema
   # Edit app/schemas/new_model.py

   # Create new endpoint
   # Edit app/api/v1/endpoints/new_endpoint.py

   # Create new service
   # Edit app/services/new_service.py

   # Run tests
   pytest
   ```

2. **Frontend:**
   ```bash
   # Access frontend shell
   ./scripts/dev-commands.sh shell-frontend

   # Create new page
   # Create new Razor component

   # Create new service
   # Edit Services/NewService.cs

   # Run tests
   dotnet test
   ```

#### Database Changes

```bash
# Create migration
./scripts/dev-commands.sh migrate-new

# Run migration
./scripts/dev-commands.sh migrate

# If migration fails, rollback
./scripts/dev-commands.sh migrate-down
```

#### API Development

1. **Backend - Create new endpoint:**
```python
# app/api/v1/endpoints/new_endpoint.py
from fastapi import APIRouter, Depends, HTTPException
from ..deps import get_current_user

router = APIRouter()

@router.get("/items/")
async def read_items(current_user = Depends(get_current_user)):
    return [{"item": "Example"}]
```

2. **Frontend - Create new service:**
```csharp
// Services/NewService.cs
public class NewService : BaseApiService
{
    public NewService(HttpClient httpClient, IConfiguration configuration, IJSRuntime jsRuntime)
        : base(httpClient, configuration, jsRuntime) { }

    public async Task<List<Item>> GetItemsAsync()
    {
        return await GetAsync<List<Item>>("items");
    }
}
```

### Troubleshooting

#### Common Issues

**Port conflicts:**
```bash
# Check port usage
lsof -i :8000
lsof -i :8080

# Kill process
kill -9 <PID>
```

**Database connection issues:**
```bash
# Check database logs
./scripts/dev-commands.sh logs-db

# Reset database connection
./scripts/dev-commands.sh restart db
```

**Container build issues:**
```bash
# Rebuild containers
./scripts/dev-commands.sh rebuild

# Clean up
./scripts/dev-commands.sh clean
```

**Hot reload not working:**
```bash
# Restart specific service
./scripts/dev-commands.sh restart backend
./scripts/dev-commands.sh restart frontend
```

#### Performance Issues

**Check resource usage:**
```bash
docker stats

# Monitor backend performance
curl http://localhost:8000/metrics
```

**Database optimization:**
```bash
# Access database shell
./scripts/dev-commands.sh shell-db

# Check slow queries
SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

### Contributing

#### Code Style

**Backend:**
- Follow PEP 8
- Use black for formatting
- Use flake8 for linting
- Write comprehensive tests

**Frontend:**
- Follow C# naming conventions
- Use XML documentation for public methods
- Write unit tests for all components

#### Git Workflow

1. **Create feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make changes and commit:**
```bash
git add .
git commit -m "feat: add your feature description"
```

3. **Push and create PR:**
```bash
git push origin feature/your-feature-name
```

#### Code Review

- All changes must be reviewed
- Tests must pass
- Code must follow style guidelines
- Documentation must be updated

### Resources

#### Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Blazor Documentation](https://docs.microsoft.com/en-us/aspnet/core/blazor/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

#### Tools

- **VS Code**: Recommended IDE
- **Postman**: API testing
- **pgAdmin**: Database management
- **RedisInsight**: Redis management

#### Community

- Report bugs: [GitHub Issues](https://github.com/your-org/openkms/issues)
- Feature requests: [GitHub Discussions](https://github.com/your-org/openkms/discussions)
- Questions: [GitHub Discussions](https://github.com/your-org/openkms/discussions)

---

Happy coding! 🚀