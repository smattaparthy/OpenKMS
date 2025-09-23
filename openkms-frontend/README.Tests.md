# OpenKMS Frontend Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for the OpenKMS Blazor frontend application. The testing framework ensures component reliability, service functionality, and overall application quality.

## Testing Architecture

### Test Categories

#### 1. Component Tests (70%)
- **Purpose**: Test individual Blazor components in isolation
- **Tools**: bUnit, xUnit, FluentAssertions
- **Focus**: UI rendering, user interactions, data binding

#### 2. Service Tests (25%)
- **Purpose**: Test service layer functionality
- **Tools**: Moq, xUnit, FluentAssertions
- **Focus**: API calls, business logic, data management

#### 3. Integration Tests (5%)
- **Purpose**: Test component interactions and end-to-end flows
- **Tools**: Playwright (planned), integration testing framework
- **Focus**: Full user journeys, cross-component communication

## Test Structure

```
OpenKMS.Frontend.Tests/
├── OpenKMS.Frontend.Tests.csproj     # Test project file
├── Tests/
│   ├── Components/                    # Component tests
│   │   └── LoginTests.cs             # Authentication component tests
│   ├── Services/                      # Service tests
│   │   └── AuthServiceTests.cs        # Authentication service tests
│   ├── Integration/                   # Integration tests (planned)
│   │   └── UserJourneysTests.cs      # End-to-end user journey tests
│   └── Helpers/                       # Test helpers and utilities
│       └── TestHelpers.cs             # Common test utilities
├── TestResults/                       # Test output directory
└── coverage.cobertura.xml             # Coverage report
```

## Test Dependencies

### Core Testing Framework
```xml
<PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.8.0" />
<PackageReference Include="xunit" Version="2.6.1" />
<PackageReference Include="xunit.runner.visualstudio" Version="2.5.3" />
<PackageReference Include="coverlet.collector" Version="6.0.0" />
```

### Component Testing
```xml
<PackageReference Include="bunit" Version="1.20.7" />
<PackageReference Include="Microsoft.AspNetCore.Components.Testing" Version="3.2.0" />
```

### Mocking and Assertions
```xml
<PackageReference Include="Moq" Version="4.20.69" />
<PackageReference Include="FluentAssertions" Version="6.12.0" />
```

## Test Categories and Markers

### xUnit Test Categories
```csharp
[Trait("Category", "Component")]     // UI component tests
[Trait("Category", "Service")]       // Service layer tests
[Trait("Category", "Integration")]  // Integration tests
[Trait("Category", "Unit")]          // Unit tests
```

### Test Organization
```csharp
namespace OpenKMS.Tests.Components
{
    public class LoginTests : TestContext
    {
        [Fact]                   // Simple test
        [Theory]                 // Data-driven test
        [InlineData("test")]    // Test data
        public void TestMethod() { }
    }
}
```

## Component Testing Strategy

### 1. Blazor Component Testing with bUnit

#### Login Component Tests (`LoginTests.cs`)
```csharp
public class LoginTests : TestContext
{
    private readonly Mock<IJSRuntime> _mockJsRuntime;
    private readonly Mock<AuthService> _mockAuthService;

    [Fact]
    public void LoginComponent_RendersCorrectly()
    {
        // Arrange
        var cut = RenderComponent<Auth.Login>();

        // Assert
        cut.Markup.Should().Contain("Sign In");
        cut.Markup.Should().Contain("#003366"); // Royal theme
    }

    [Fact]
    public void LoginComponent_WithValidCredentials_ShowsLoadingState()
    {
        // Arrange
        var cut = RenderComponent<Auth.Login>();
        var submitButton = cut.Find("button[type='submit']");

        // Act
        submitButton.Click();

        // Assert
        cut.Find(".loading-indicator").Should().NotBeNull();
    }
}
```

#### Testing Component Interactions
```csharp
[Fact]
public void RegisterLink_NavigatesToRegisterPage()
{
    // Arrange
    var cut = RenderComponent<Auth.Login>();

    // Act
    var registerLink = cut.Find("a[href='/register']");
    registerLink.Click();

    // Assert
    Services
        .GetRequiredService<NavigationManager>()
        .Uri.Should().EndWith("/register");
}
```

#### Testing Form Validation
```csharp
[Fact]
public void LoginForm_HasValidationAttributes()
{
    // Arrange
    var cut = RenderComponent<Auth.Login>();

    // Act & Assert
    var usernameInput = cut.Find("#username");
    usernameInput.GetAttribute("required").Should().Be("required");

    var emailInput = cut.Find("#email");
    emailInput.GetAttribute("type").Should().Be("email");
}
```

### 2. Service Testing Strategy

#### Authentication Service Tests (`AuthServiceTests.cs`)
```csharp
public class AuthServiceTests
{
    private readonly Mock<IJSRuntime> _mockJsRuntime;
    private readonly Mock<HttpClient> _mockHttpClient;
    private readonly AuthService _authService;

    [Fact]
    public async Task LoginAsync_WithValidCredentials_ReturnsAuthResponse()
    {
        // Arrange
        var loginRequest = new UserLoginRequest
        {
            Username = "testuser",
            Password = "testpassword123"
        };

        var expectedResponse = new AuthResponse
        {
            AccessToken = "test-token",
            RefreshToken = "test-refresh",
            TokenType = "bearer"
        };

        _mockHttpClient
            .Setup(x => x.PostAsync(It.IsAny<string>(), It.IsAny<StringContent>()))
            .ReturnsAsync(new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(JsonSerializer.Serialize(expectedResponse))
            });

        // Act
        var result = await _authService.LoginAsync(loginRequest);

        // Assert
        result.Should().BeEquivalentTo(expectedResponse);
    }

    [Fact]
    public async Task IsAuthenticatedAsync_WithValidToken_ReturnsTrue()
    {
        // Arrange
        _mockJsRuntime
            .Setup(x => x.InvokeAsync<string>("localStorage.getItem", "accessToken"))
            .ReturnsAsync("valid-token");

        // Act
        var result = await _authService.IsAuthenticatedAsync();

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public async Task LogoutAsync_ClearsAllTokens()
    {
        // Act
        await _authService.LogoutAsync();

        // Assert
        _mockJsRuntime.Verify(
            x => x.InvokeVoidAsync("localStorage.removeItem", "accessToken"),
            Times.Once
        );
    }
}
```

#### Testing HTTP Service Communication
```csharp
[Fact]
public async Task GetCurrentUserAsync_WithValidToken_ReturnsUser()
{
    // Arrange
    var expectedUser = new User { Id = 1, Username = "testuser" };
    var responseMessage = new HttpResponseMessage(HttpStatusCode.OK)
    {
        Content = new StringContent(JsonSerializer.Serialize(expectedUser))
    };

    _mockHttpClient
        .Setup(x => x.GetAsync("users/me"))
        .ReturnsAsync(responseMessage);

    _mockJsRuntime
        .Setup(x => x.InvokeAsync<string>("localStorage.getItem", "accessToken"))
        .ReturnsAsync("valid-token");

    // Act
    var result = await _authService.GetCurrentUserAsync();

    // Assert
    result.Should().BeEquivalentTo(expectedUser);
}
```

### 3. Integration Testing Strategy (Planned)

#### User Journey Tests
```csharp
[Trait("Category", "Integration")]
public class UserRegistrationJourneyTests : TestContext
{
    [Fact]
    public async Task CompleteRegistrationFlow_ShowsSuccessMessage()
    {
        // Arrange
        var cut = RenderComponent<App>();

        // Navigate to register page
        var registerLink = cut.Find("a[href='/register']");
        registerLink.Click();

        // Wait for component to render
        var registerComponent = cut.FindComponent<Auth.Register>();

        // Fill form
        var usernameInput = registerComponent.Find("#username");
        usernameInput.Change("newuser");

        var emailInput = registerComponent.Find("#email");
        emailInput.Change("newuser@example.com");

        var submitButton = registerComponent.Find("button[type='submit']");

        // Act
        submitButton.Click();

        // Assert
        cut.WaitForElement(".bg-green-100")
           .TextContent.Should().Contain("Account created successfully");
    }
}
```

## Test Data Management

### Mock Data for Tests
```csharp
public static class TestUserData
{
    public static UserLoginRequest ValidLoginRequest => new()
    {
        Username = "testuser",
        Password = "testpassword123"
    };

    public static UserCreateRequest ValidRegistrationRequest => new()
    {
        Username = "newuser",
        Email = "newuser@example.com",
        FullName = "New User",
        Password = "newpassword123",
        OfficeLocation = "Test Office",
        Department = "Test Department"
    };

    public static AuthResponse ValidAuthResponse => new()
    {
        AccessToken = "test-access-token",
        RefreshToken = "test-refresh-token",
        TokenType = "bearer"
    };
}
```

### Test Context Setup
```csharp
public class TestBase
{
    protected TestContext Context { get; }
    protected Mock<IJSRuntime> MockJsRuntime { get; }
    protected Mock<AuthService> MockAuthService { get; }

    public TestBase()
    {
        Context = new TestContext();
        MockJsRuntime = new Mock<IJSRuntime>();
        MockAuthService = new Mock<AuthService>(
            Mock.Of<HttpClient>(),
            Mock.Of<IConfiguration>(),
            MockJsRuntime.Object
        );

        // Register services
        Context.Services.AddSingleton(MockJsRuntime.Object);
        Context.Services.AddSingleton(MockAuthService.Object);
    }
}
```

## Test Execution

### Frontend Test Runner (`test_runner.sh`)

#### Command Line Options
```bash
# Run all tests
./test_runner.sh all

# Run specific test category
./test_runner.sh component
./test_runner.sh service
./test_runner.sh unit

# Run tests with coverage
./test_runner.sh coverage

# Run specific test class
./test_runner.sh specific LoginTests

# Run tests in verbose mode
./test_runner.sh verbose

# Generate test report
./test_runner.sh report

# Show test project structure
./test_runner.sh structure

# Install dependencies
./test_runner.sh install

# Clean build artifacts
./test_runner.sh clean

# Get help
./test_runner.sh help
```

### Visual Studio Test Explorer
1. Build the test project
2. Open Visual Studio
3. Navigate to Test Explorer (Test → Test Explorer)
4. Run tests individually or all at once

### VS Code Testing
1. Install .NET Test Explorer extension
2. Open the solution
3. Tests appear in Testing tab
4. Run and debug tests from the sidebar

## Coverage and Reporting

### Code Coverage Configuration
```xml
<ItemGroup>
  <PackageReference Include="coverlet.collector" Version="6.0.0" />
</ItemGroup>
```

### Running with Coverage
```bash
# Generate coverage reports
dotnet test --collect:"XPlat Code Coverage"

# Generate HTML report
dotnet test --collect:"XPlat Code Coverage;Format=Html"

# Generate specific format reports
dotnet test --collect:"XPlat Code Coverage;Format=Cobertura;Format=OpenCover"
```

### Coverage Reports Location
```
TestResults/
├── coverage.cobertura.xml       # Cobertura XML format
├── coverage.opencover.xml       # OpenCover XML format
├── coverage.html                # HTML report (if generated)
└── TestResults.trx              # Test results in TRX format
```

## Test Best Practices

### 1. Component Testing Best Practices

#### Test Naming
```csharp
// Good naming
[Fact]
public void LoginComponent_RendersCorrectly()
[Fact]
public void LoginComponent_WithValidCredentials_ShowsLoadingState()
[Fact]
public void RegisterLink_NavigatesToRegisterPage()

// Avoid generic names
[Fact]
public void Test1()  // Bad: not descriptive
[Fact]
public void LoginTest()  // Bad: too general
```

#### Arrange-Act-Assert Pattern
```csharp
[Fact]
public async Task Login_WithValidCredentials_Succeeds()
{
    // Arrange
    var mockAuthService = new Mock<AuthService>();
    var cut = RenderComponent<Auth.Login>();
    var submitButton = cut.Find("button[type='submit']");

    // Act
    submitButton.Click();

    // Assert
    cut.WaitForState(() => cut.Instance.IsLoading == false)
        .Should().BeTrue();
}
```

#### Component Lifecycle Testing
```csharp
[Fact]
public void Component_CallingOnInitialized_SetsUpCorrectly()
{
    // Arrange
    var cut = RenderComponent<TestComponent>();

    // Act - Component initialization happens automatically

    // Assert
    cut.Instance.IsInitialized.Should().BeTrue();
}
```

### 2. Service Testing Best Practices

#### Mocking Dependencies
```csharp
[Fact]
public async Task AuthService_Login_StoresTokensInLocalStorage()
{
    // Arrange
    var mockJsRuntime = new Mock<IJSRuntime>();
    var authService = new AuthService(
        Mock.Of<HttpClient>(),
        Mock.Of<IConfiguration>(),
        mockJsRuntime.Object
    );

    // Act
    await authService.LoginAsync(validRequest);

    // Assert
    mockJsRuntime.Verify(
        x => x.InvokeVoidAsync("localStorage.setItem", "accessToken", It.IsAny<string>()),
        Times.Once
    );
}
```

#### Exception Handling Tests
```csharp
[Fact]
public async Task AuthService_Login_WithNetworkError_ThrowsException()
{
    // Arrange
    var mockHttpClient = new Mock<HttpClient>();
    mockHttpClient
        .Setup(x => x.PostAsync(It.IsAny<string>(), It.IsAny<StringContent>()))
        .ThrowsAsync(new HttpRequestException("Network error"));

    var authService = new AuthService(
        mockHttpClient.Object,
        Mock.Of<IConfiguration>(),
        Mock.Of<IJSRuntime>()
    );

    // Act & Assert
    await Assert.ThrowsAsync<HttpRequestException>(
        () => authService.LoginAsync(validRequest)
    );
}
```

### 3. Async Testing Best Practices

#### Proper Async Testing
```csharp
[Fact]
public async Task AsyncOperation_CompletesSuccessfully()
{
    // Arrange
    var service = new AsyncTestService();

    // Act
    var result = await service.AsyncOperation();

    // Assert
    result.Should().NotBeNull();
}

// BAD: Don't do this
[Fact]
public void AsyncOperation_SyncTest()  // Wrong: missing async/await
{
    var service = new AsyncTestService();
    var task = service.AsyncOperation();  // Don't forget to await
    task.Result.Should().NotBeNull();     // Avoid .Result in tests
}
```

### 4. Test Data Management

#### Test Data Builders
```csharp
public class UserTestBuilder
{
    private User _user = new();

    public UserTestBuilder WithUsername(string username)
    {
        _user.Username = username;
        return this;
    }

    public UserTestBuilder WithEmail(string email)
    {
        _user.Email = email;
        return this;
    }

    public User Build() => _user;
}

// Usage
var testUser = new UserTestBuilder()
    .WithUsername("testuser")
    .WithEmail("test@example.com")
    .Build();
```

## Continuous Integration

### GitHub Actions Integration (Planned)
```yaml
name: Frontend Tests

on:
  push:
    paths:
      - 'openkms-frontend/**'
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: windows-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup .NET
      uses: actions/setup-dotnet@v3
      with:
        dotnet-version: 8.0.x

    - name: Restore dependencies
      run: dotnet restore openkms-frontend/OpenKMS.Frontend.Tests.csproj

    - name: Build
      run: dotnet build openkms-frontend/OpenKMS.Frontend.Tests.csproj

    - name: Test
      run: dotnet test openkms-frontend/OpenKMS.Frontend.Tests.csproj --collect:"XPlat Code Coverage"

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Troubleshooting

### Common Issues

#### 1. Component Test Issues
```bash
# Problem: Component not found
# Solution: Ensure component is marked with @inherits LayoutComponentBase
# Check using: grep -r "@inherits" Components/

# Problem: Blazor component rendering issues
# Solution: Check that all required services are registered
```

#### 2. Service Test Issues
```bash
# Problem: Moq setup not working
# Solution: Ensure virtual methods in service classes
# Check method signature: public virtual async Task

# Problem: HTTP client mocking issues
# Solution: Use StringContent for request body
# Set content type: application/json
```

#### 3. Async Test Issues
```bash
# Problem: Tests hanging
# Solution: Use ConfigureAwait(false) in service methods
# Or use proper async test methods

# Problem: Race conditions in tests
# Solution: Use cut.WaitForState() for async operations
# Add proper assertions for completed states
```

### Debugging Tests

#### Visual Studio Debugging
1. Set breakpoints in test methods
2. Use "Debug Test" from Test Explorer
3. Inspect component behavior during execution

#### Live Unit Testing (VS Enterprise)
1. Enable Live Unit Testing
2. Real-time feedback as you code
3. Automatic test execution on changes

### Performance Considerations

#### Test Execution Time
```csharp
// Fast tests (under 10ms)
[Fact]
public void FastTest() {Assert.True(true);}

// Medium tests (under 100ms)
[Trait("Category", "Service")]
public async Task MediumTest() {await service.Operation();}

// Slow tests (over 100ms)
[Trait("Category", "Integration")]
[Trait("Category", "Slow")]
public async Task SlowTest() { await FullUserJourney(); }
```

## Future Enhancements

### 1. Expanded Test Coverage
- **E2E testing**: Playwright for full browser testing
- **Visual testing**: Percy or Applitools for visual regression
- **Performance testing**: Component render time analysis
- **Accessibility testing**: Axe-core for WCAG compliance

### 2. Advanced Testing Features
- **Mutation testing**: Stryker for mutation testing
- **Behavior-driven tests**: SpecFlow for BDD-style testing
- **Contract testing**: Pact for API contract validation
- **A/B testing**: Feature flag testing framework

### 3. Test Automation
- **Parallel execution**: Run tests in parallel for speed
- **Test categorization**: Fast vs slow test separation
- **Smart test selection**: Run only affected tests
- **Test data automation**: Dynamic test data generation

## Conclusion

This comprehensive testing strategy ensures that the OpenKMS Blazor frontend maintains high quality, reliability, and user experience. The combination of component testing, service testing, and integration testing provides complete coverage of the application functionality, while the modern testing tools and frameworks ensure efficient and maintainable test development.

## Running Tests in Development

### Quick Development Cycle
```bash
# Install dependencies
./test_runner.sh install

# Run quick component tests
./test_runner.sh component

# Run specific test file during development
./test_runner.sh specific LoginTests

# Run with coverage before committing
./test_runner.sh coverage

# Clean and rebuild if issues occur
./test_runner.sh clean && ./test_runner.sh build && ./test_runner.sh test
```

### Common Test Commands
```bash
# Run all tests
dotnet test

# Run with verbose output
dotnet test --logger "console;verbosity=diagnostic"

# Run tests with coverage
dotnet test --collect:"XPlat Code Coverage"

# Filter by category
dotnet test --filter "Category=Component"

# Run specific test method
dotnet test --filter "FullyQualifiedName~LoginTests"
```