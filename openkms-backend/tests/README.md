# OpenKMS Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for the OpenKMS backend application. The testing framework is designed to ensure reliability, security, and performance across all layers of the application.

## Testing Pyramid

### 🧪 Unit Tests (70%)
- **Location**: `tests/unit/`
- **Purpose**: Test individual components in isolation
- **Coverage**: Business logic, data validation, utility functions
- **Tools**: pytest, unittest.mock, pytest-asyncio

### 🔗 Integration Tests (25%)
- **Location**: `tests/integration/`
- **Purpose**: Test interactions between components
- **Coverage**: API endpoints, database interactions, authentication flows
- **Tools**: TestClient, AsyncClient, real database instances

### 🚀 End-to-End Tests (5%)
- **Location**: tests/e2e/ (planned)
- **Purpose**: Test complete user workflows
- **Coverage**: Full application scenarios, user journeys
- **Tools**: Playwright, Selenium (for future frontend testing)

## Test Types

### 1. Unit Tests

#### Auth Service Tests (`test_auth_service.py`)
- User login with valid credentials
- User login with invalid credentials
- User registration with unique data
- User registration with duplicate data
- Token refresh functionality
- Password change operations
- Error handling for edge cases

#### User CRUD Tests (`test_user_crud.py`)
- Create user with valid data
- Get user by ID, username, email
- Update user information
- Delete user operations
- User authentication
- Search and filtering operations

#### Service Layer Tests (planned)
- Training service business logic
- Registration service validation
- Conflict detection algorithms
- Email notification services

### 2. Integration Tests

#### Authentication API Tests (`test_auth_api.py`)
- Complete user registration flows
- Login/logout functionality
- Token refresh cycles
- Password change operations
- Protected endpoint access
- Error handling and validation

#### Users API Tests (`test_users_api.py`)
- User profile management
- Role-based access control
- Admin vs regular user permissions
- User search and filtering
- Pagination functionality
- Registration and attendance queries

#### Training API Tests (`test_training_api.py`)
- Training CRUD operations
- Registration workflows
- Conflict detection
- Admin permissions validation
- Data validation and error handling

#### Async API Tests
- Concurrent request handling
- Token lifecycle management
- Performance under load
- Race condition prevention

### 3. Performance Tests (planned)
- Load testing for concurrent users
- Response time benchmarks
- Database query optimization
- API endpoint performance

### 4. Security Tests (planned)
- Authentication bypass prevention
- Authorization validation
- Input sanitization
- SQL injection prevention
- XSS vulnerability testing

## Test Configuration

### pytest.ini Configuration

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    --asyncio-mode=auto
```

### Test Markers

```python
@pytest.mark.unit           # Unit tests
@pytest.mark.integration    # Integration tests
@pytest.mark.slow           # Slow running tests
@pytest.mark.auth           # Authentication tests
@pytest.mark.api            # API endpoint tests
@pytest.mark.database       # Database-related tests
@pytest.mark.service        # Service layer tests
```

### Database Setup

#### Test Database Configuration
- **Database**: PostgreSQL 15+
- **Name**: openkms_test
- **Connection**: Async SQLAlchemy with asyncpg
- **Isolation**: Each test runs in transaction with rollback

#### Migration Strategy
```python
@pytest.fixture(scope="session")
async def test_db_setup():
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

## Test Data Management

### Fixtures

#### Core Fixtures (`conftest.py`)
```python
@pytest.fixture
def test_user_data():  # Test user data blueprint

@pytest_asyncio.fixture
async def test_user():  # Create test user in database

@pytest_asyncio.fixture
async def test_admin():  # Create admin user

@pytest_asyncio.fixture
async def test_training():  # Create training session

@pytest.fixture
def auth_headers():  # Authentication headers for requests
```

#### Data Validation
- Unique data generation for each test
- Cleanup and rollback between tests
- Realistic test data that mirrors production

## Test Execution

### Test Runner (`test_runner.py`)

#### Command Line Options
```bash
# Run all tests
python test_runner.py --type all

# Run unit tests only
python test_runner.py --type unit

# Run integration tests only
python test_runner.py --type integration

# Run smoke tests
python test_runner.py --type smoke

# Run performance tests
python test_runner.py --type performance

# Generate coverage report
python test_runner.py --type coverage

# Run tests with specific markers
python test_runner.py --markers api auth

# Run security scan
python test_runner.py --security

# Set up test database
python test_runner.py --setup-db
```

### Continuous Integration

#### GitHub Actions Integration (planned)
```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: python test_runner.py --type all --security
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Coverage Goals

### Target Coverage
- **Overall Coverage**: 80% minimum
- **App Core**: 95% coverage
- **API Endpoints**: 90% coverage
- **Business Logic**: 95% coverage
- **Utility Functions**: 90% coverage

### Coverage Reports
- **HTML Report**: `htmlcov/index.html`
- **XML Report**: `coverage.xml` (CI integration)
- **Terminal Report**: Real-time coverage display

## Best Practices

### 1. Test Organization
- **One test per file**: Focus on specific functionality
- **Descriptive naming**: Clear test names that describe what's being tested
- **Arrange-Act-Assert**: Clear test structure
- **Minimal setup**: Keep fixtures simple and focused

### 2. Test Independence
- **Isolated tests**: No dependencies between tests
- **Cleanup**: Proper teardown and resource cleanup
- **Deterministic**: Same results every time
- **Fast execution**: Optimize for quick feedback

### 3. Security Testing
- **Authentication flow**: Validate all auth paths
- **Authorization**: Test role-based access control
- **Input validation**: Test data sanitization
- **Error handling**: Test secure error responses

### 4. Performance Considerations
- **Async support**: All async operations properly tested
- **Database efficiency**: Monitor query performance
- **Memory usage**: Test for memory leaks
- **Concurrency**: Test race condition handling

## Monitoring and Metrics

### Test Metrics
- **Pass rate**: Percentage of passing tests
- **Coverage**: Code coverage percentage
- **Execution time**: Test duration metrics
- **Flakiness**: Test stability indicators

### CI/CD Metrics
- **Build success rate**
- **Test execution time trends**
- **Coverage trends**
- **Defect density**

## Security Considerations

### Test Data Security
- **Never commit real credentials**: Use test-only data
- **Secure test environment**: Isolated test database
- **Data sanitization**: Remove sensitive test data
- **Environment isolation**: Separate test and production

### Access Control Testing
- **Role-based access**: Test all permission levels
- **Endpoint protection**: Verify authentication requirements
- **Data encryption**: Test secure data handling
- **Audit trails**: Verify logging of sensitive operations

## Future Enhancements

### 1. Expanded Test Coverage
- **E2E tests**: Frontend to backend integration
- **Performance testing**: Load and stress testing
- **Accessibility testing**: WCAG compliance testing
- **Compatibility testing**: Browser and device testing

### 2. Advanced Testing Tools
- **Mutation testing**: Assess test effectiveness
- **Contract testing**: API contract validation
- **Visual regression testing**: UI consistency testing
- **Chaos engineering**: Fault tolerance testing

### 3. Automation Improvements
- **Parallel test execution**: Speed up test runs
- **Test data automation**: Dynamic test data generation
- **Smart test selection**: Run only relevant tests
- **AI-assisted testing**: Automated test generation

## Running Tests in Development

### Quick Development Cycle
```bash
# Install dependencies
pip install -r requirements.txt

# Set up test database
python test_runner.py --setup-db

# Run unit tests (fast)
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_auth_service.py::TestAuthService::test_login_user_success -v

# Run with coverage
pytest tests/unit/ --cov=app --cov-report=term-missing
```

### Common Test Commands
```bash
# Run all tests
pytest

# Run with markers
pytest -m "auth or api"

# Run failed tests only
pytest --lf

# Run tests with verbose output
pytest -v

# Run tests with coverage
pytest --cov=app --cov-report=html
```

## Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Solution: Check PostgreSQL is running and test database exists
python test_runner.py --setup-db
```

#### Test Dependencies Missing
```bash
# Solution: Install test dependencies
pip install pytest pytest-asyncio pytest-mock httpx coverage pytest-cov
```

#### Async Test Issues
```bash
# Solution: Ensure proper async fixtures and event loop
pytest --asyncio-mode=auto
```

### Debugging Tests
```bash
# Run with verbose output
pytest -v --tb=long

# Stop on first failure
pytest -x

# Run with Python debugger
pytest --pdb

# Show local variables in tracebacks
pytest -l
```

## Conclusion

This comprehensive testing strategy ensures that OpenKMS maintains high quality, security, and reliability. The testing pyramid provides maximum coverage with efficient execution times, while the integrated tools and processes enable continuous quality improvement throughout the development lifecycle.