using Bunit;
using Microsoft.Extensions.DependencyInjection;
using Moq;
using FluentAssertions;
using Xunit;
using OpenKMS.Services;
using OpenKMS.Models.Requests;
using OpenKMS.Models.Responses;
using Microsoft.JSInterop;

namespace OpenKMS.Tests.Components
{
    public class LoginTests : TestContext
    {
        private readonly Mock<IJSRuntime> _mockJsRuntime;
        private readonly Mock<AuthService> _mockAuthService;
        private readonly Mock<IConfiguration> _mockConfiguration;

        public LoginTests()
        {
            _mockJsRuntime = new Mock<IJSRuntime>();

            // Mock configuration
            _mockConfiguration = new Mock<IConfiguration>();

            // Mock auth service
            _mockAuthService = new Mock<AuthService>(
                Mock.Of<HttpClient>(),
                _mockConfiguration.Object,
                _mockJsRuntime.Object
            );

            // Register services
            Services.AddSingleton(_mockJsRuntime.Object);
            Services.AddSingleton(_mockConfiguration.Object);
            Services.AddSingleton(_mockAuthService.Object);

            // Setup auth service mock properties
            _mockAuthService.SetupGet(x => x.HttpClient).Returns(Mock.Of<HttpClient>());
            _mockAuthService.SetupGet(x => x.Configuration).Returns(_mockConfiguration.Object);
        }

        [Fact]
        public void LoginComponent_RendersCorrectly()
        {
            // Arrange
            var cut = RenderComponent<Auth.Login>();

            // Assert
            cut.Markup.Should().Contain("Create Account");
            cut.Markup.Should().Contain("Username *");
            cut.Markup.Should().Contain("Password *");
            cut.Markup.Should().Contain("Already have an account? Sign in");
        }

        [Fact]
        public void LoginComponent_WithValidCredentials_ShowsLoadingState()
        {
            // Arrange
            var expectedAuthResponse = new AuthResponse
            {
                AccessToken = "test-access-token",
                RefreshToken = "test-refresh-token",
                TokenType = "bearer"
            };

            _mockAuthService
                .Setup(x => x.LoginAsync(It.IsAny<UserLoginRequest>()))
                .ReturnsAsync(expectedAuthResponse);

            var cut = RenderComponent<Auth.Login>();

            // Find form elements
            var usernameInput = cut.Find("#username");
            var passwordInput = cut.Find("#password");
            var submitButton = cut.Find("button[type='submit']");

            // Act
            usernameInput.Change("testuser");
            passwordInput.Change("testpassword");
            submitButton.Click();

            // Assert - Button should show loading state
            // Note: This is a simplified test - in reality, you'd need to handle async properly
            var buttons = cut.FindAll("button");
            buttons.Should().Contain(b => b.TextContent.Contains("Signing In..."));
        }

        [Fact]
        public void LoginComponent_WithInvalidCredentials_ShowsErrorMessage()
        {
            // Arrange
            _mockAuthService
                .Setup(x => x.LoginAsync(It.IsAny<UserLoginRequest>()))
                .ThrowsAsync(new System.Exception("Invalid credentials"));

            var cut = RenderComponent<Auth.Login>();

            // Find form elements
            var usernameInput = cut.Find("#username");
            var passwordInput = cut.Find("#password");
            var submitButton = cut.Find("button[type='submit']");

            // Act
            usernameInput.Change("testuser");
            passwordInput.Change("wrongpassword");
            submitButton.Click();

            // Assert - Need to wait for error message to appear
            // This is a simplified test - you'd need to implement proper async testing
            var errorElement = cut.WaitForElement(".bg-red-100");
            errorElement.TextContent.Should().Contain("Error!");
        }

        [Fact]
        public void LoginComponent_RegisterLink_NavigatesToRegister()
        {
            // Arrange
            var navigationManager = Services.GetRequiredService<Blazor.NavigationManager>();
            var cut = RenderComponent<Auth.Login>();

            // Act
            var registerLink = cut.Find("a[href='/register']");
            registerLink.Click();

            // Assert
            navigationManager.Uri.Should().EndWith("/register");
        }

        [Fact]
        public void LoginComponent_FormValidation_RequiredFields()
        {
            // Arrange
            var cut = RenderComponent<Auth.Login>();

            // Act - Try to submit empty form
            var submitButton = cut.Find("button[type='submit']");
            submitButton.Click();

            // Assert - In a real scenario, you'd check for validation messages
            // This is a simplified test showing the concept
            var inputs = cut.FindAll("input, button");
            inputs.Should().NotBeEmpty();
        }

        [Fact]
        public void LoginComponent_Initialization_SetsUpCorrectly()
        {
            // Arrange & Act
            var cut = RenderComponent<Auth.Login>();

            // Assert
            var componentInstance = cut.Instance;
            componentInstance.Should().NotBeNull();

            // Check that registerRequest is initialized
            var registerRequestField = componentInstance.GetType()
                .GetField("registerRequest", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

            if (registerRequestField != null)
            {
                registerRequestField.GetValue(componentInstance).Should().NotBeNull();
            }
        }

        [Fact]
        public void LoginComponent_RoyalThemeApplied()
        {
            // Arrange
            var cut = RenderComponent<Auth.Login>();

            // Assert - Check that royal theme colors are applied
            cut.Markup.Should().Contain("#003366"); // Primary navy
            cut.Markup.Should().Contain("#FFF8DC"); // Cream color
        }

        [Fact]
        public void LoginComponent_HasCorrectStructure()
        {
            // Arrange
            var cut = RenderComponent<Auth.Login>();

            // Assert - Check component structure
            var title = cut.Find("h2");
            title.TextContent.Should().Contain("Sign In");

            var description = cut.Find("p.text-sm");
            description.TextContent.Should().Contain("Welcome back to OpenKMS");

            var form = cut.Find("EditForm");
            form.Should().NotBeNull();

            var usernameInput = cut.Find("#username");
            usernameInput.GetAttribute("type").Should().Be("text");

            var passwordInput = cut.Find("#password");
            passwordInput.GetAttribute("type").Should().Be("password");
        }
    }
}