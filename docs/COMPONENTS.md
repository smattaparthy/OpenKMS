# OpenKMS Frontend Component Documentation

## Overview

The OpenKMS frontend is built with ASP.NET Core 8 Blazor Server, providing a rich, interactive user experience with modern web technologies. Components are organized logically to promote reusability, maintainability, and clear separation of concerns.

### Technology Stack
- **Framework**: ASP.NET Core 8 Blazor Server
- **Language**: C# 12
- **UI Framework**: Bootstrap 5 with custom design system
- **Authentication**: JWT-based authentication with local storage
- **State Management**: Component-scoped state with service layer
- **Routing**: Blazor Router with NavigationManager

---

## Component Architecture

### Directory Structure
```
openkms-frontend/Components/
├── Auth/                    # Authentication components
│   ├── Login.razor         # Login page component
│   └── Register.razor      # Registration page component
├── Admin/                  # Administration components
│   ├── Dashboard.razor    # Admin dashboard overview
│   ├── Settings.razor     # System settings
│   ├── Trainings.razor    # Training management
│   ├── Users.razor        # User management
│   └── Reports.razor      # System reports
├── Training/              # Training-related components
│   ├── TrainingList.razor # Browse trainings
│   ├── TrainingDetails.razor # Training detail view
│   ├── MyRegistrations.razor # User's training registrations
│   └── Calendar.razor     # Training calendar
├── Layout/                # Layout components
│   ├── MainLayout.razor   # Main application layout
│   └── NavMenu.razor      # Navigation menu
├── Shared/                # Reusable components
│   └── UserCreateModal.razor # User creation modal
└── _Imports.razor        # Global component imports
```

---

## Core Components

### 🏗️ Layout Components

#### MainLayout.razor
**File**: `Components/Layout/MainLayout.razor`

**Purpose**: Main application layout providing navigation structure and authentication state management.

**Key Features**:
- Authentication state checking with automatic redirect
- Role-based navigation menu display
- Responsive Bootstrap navbar
- User profile display in header
- Error handling and user data loading

**Usage**:
```csharp
// Automatically used as root layout
// Implements role-based navigation access
```

**Event Handlers**:
- `CheckAuthentication()`: Validates user authentication status
- `LoadUserData()`: Loads current user information
- `Logout()`: Handles user logout and cleanup

**Parameters/Properties**:
- `showNavbar`: Controls navigation visibility
- `currentUser`: Current authenticated user
- `UserHasAdminRole`: Admin role visibility flag

---

#### NavMenu.razor
**File**: `Components/Layout/NavMenu.razor`

**Purpose**: Navigation menu component with collapsible mobile support.

**Key Features**:
- Responsive mobile-first navigation
- Active route highlighting
- Role-based menu item visibility
- Bootstrap collapse integration

**Usage**:
```csharp
// Integrated into MainLayout
// Automatically highlights active routes
```

---

### 🔐 Authentication Components

#### Login.razor
**File**: `Components/Auth/Login.razor`

**Purpose**: User authentication page with form validation and error handling.

**Key Features**:
- Form validation with DataAnnotationsValidator
- Loading state management
- Error message display
- Authentication failure handling
- Automatic redirect on successful login

**Usage**:
```csharp
// Navigate to /login for authentication
// Handles credential submission and JWT storage
```

**Event Handlers**:
- `HandleLogin()`: Processes login form submission
- `OnAfterRenderAsync()`: Initializes authentication service

**Parameters/Properties**:
- `loginRequest`: UserLoginRequest model
- `isLoading`: Loading state indicator
- `showError`: Error visibility flag
- `errorMessage`: Error message content

**Example Form**:
```razor
<EditForm Model="@loginRequest" OnValidSubmit="@HandleLogin">
    <DataAnnotationsValidator />
    <InputText @bind-Value="loginRequest.Username" />
    <InputText type="password" @bind-Value="loginRequest.Password" />
    <button type="submit" disabled="@isLoading">Sign in</button>
</EditForm>
```

---

#### Register.razor
**File**: `Components/Auth/Register.razor`

**Purpose**: User registration page with comprehensive form validation.

**Key Features**:
- Multi-step form validation
- Password strength validation
- Confirmation password matching
- Role selection (for admin users)
- Account creation feedback

**Usage**:
```csharp
// Navigate to /register for new user creation
// Supports user self-registration and admin creation
```

**Event Handlers**:
- `HandleRegister()`: Processes registration form submission
- `ValidatePassword()`: Validates password strength
- `GenerateUsername()`: Auto-generates username suggestions

---

### 👥 Admin Components

#### Users.razor
**File**: `Components/Admin/Users.razor`

**Purpose**: User management dashboard with CRUD operations and role-based access control.

**Key Features**:
- User listing with search and filtering
- Role assignment and status management
- User creation modal integration
- Pagination support
- Bulk operations (active/inactive toggle)

**Usage**:
```csharp
// Navigate to /admin/users for user management
// Requires ADMIN role access
```

**Key Methods**:
- `LoadUsers()`: Loads user list with filters
- `ShowUserCreateModal()`: Opens user creation dialog
- `HandleUserCreated()`: Processes modal form submission
- `ToggleUserStatus()`: Activates/deactivates users

**Data Binding**:
```csharp
// User list data binding
private List<UserResponse> users = new();

// Modal state management
private bool showCreateModal = false;

// Search/filter parameters
private string searchQuery = "";
private UserRole? selectedRole = null;
private bool? activeFilter = true;
```

---

#### Dashboard.razor
**File**: `Components/Admin/Dashboard.razor`

**Purpose**: Administrative overview dashboard with system metrics and analytics.

**Key Features**:
- Real-time statistics cards
- User engagement metrics
- Training completion rates
- System health indicators
- Recent activity feed
- Quick action buttons

**Usage**:
```csharp
// Navigate to /admin for dashboard view
// Requires ADMIN role access
```

**Data Models**:
```csharp
public class DashboardMetrics
{
    public int TotalUsers { get; set; }
    public int ActiveUsers { get; set; }
    public int TotalTrainings { get; set; }
    public int PendingRegistrations { get; set; }
    public int CompletedTrainingsThisMonth { get; set; }
}
```

---

#### Settings.razor
**File**: `Components/Admin/Settings.razor`

**Purpose**: System configuration and settings management.

**Key Features**:
- Application-wide settings configuration
- Email notification settings
- Security policy configuration
- Integration setup (LDAP, OAuth)
- Backup configuration

**Usage**:
```csharp
// Navigate to /admin/settings for configuration
// Requires ADMIN role access
```

---

### 📚 Training Components

#### TrainingList.razor
**File**: `Components/Training/TrainingList.razor`

**Purpose**: Training program browsing and discovery interface.

**Key Features**:
- Search and advanced filtering
- Grid/list view toggle
- Category and level filters
- Credit information display
- Registration status indicators
- Pagination support

**Usage**:
```csharp
// Navigate to /trainings for training browsing
// Available to all authenticated users
```

**Event Handlers**:
- `HandleSearch()`: Processes search queries
- `HandleFilterChange()`: Updates filter parameters
- `RegisterForTraining()`: Handles training registration

**Search Implementation**:
```razor
// Search input with two-way binding
<InputText id="search" @bind-Value="searchText" placeholder="Search trainings..." />

// Filter dropdowns
<InputSelect @bind-Value="selectedCategory">
    <option value="">All Categories</option>
    <option value="SECURITY">Security</option>
    <option value="LEADERSHIP">Leadership</option>
</InputSelect>
```

---

#### TrainingDetails.razor
**File**: `Components/Training/TrainingDetails.razor**

**Purpose**: Detailed training program information and registration interface.

**Key Features**:
- Training information display
- Schedule information
- Prerequisites listing
- Registration status management
- Materials download
- Feedback submission

**Usage**:
```csharp
// Navigate to /trainings/{id} for details
// Parameters: trainingId (from route)
```

**Route Parameters**:
```csharp
[Parameter]
public int TrainingId { get; set; }

// Component initialization
protected override async Task OnInitializedAsync()
{
    await LoadTrainingDetails();
}
```

---

#### MyRegistrations.razor
**File**: `Components/Training/MyRegistrations.razor`

**Purpose**: User's training registration history and management interface.

**Key Features**:
- Registration status display
- Certificate generation
- Feedback submission
- Cancellation options
- Completion tracking

**Usage**:
```csharp
// Navigate to /my-registrations for personal training management
// Available to all authenticated users
```

---

### 📅 Calendar Component

#### Calendar.razor
**File**: `Components/Training/Calendar.razor`

**Purpose**: Training schedule calendar with month/week/day views.

**Key Features**:
- Multiple view modes (month/week/day)
- Event filtering by category
- Registration links from calendar
- Recurring event support
- Export functionality (PDF, iCal)

**Usage**:
```csharp
// Navigate to /calendar for training schedule view
// Available to all authenticated users
```

**Calendar Integration**:
```csharp
// Calendar data source
private List<CalendarEvent> TrainingEvents = new();

// Event click handler
private void HandleEventClick(CalendarEvent @event)
{
    NavigationManager.NavigateTo($"/trainings/{@event.TrainingId}");
}
```

---

### 🎛️ Reusable Components

#### UserCreateModal.razor
**File**: `Components/Shared/UserCreateModal.razor`

**Purpose**: Modal dialog for creating new users with comprehensive form validation.

**Key Features**:
- Bootstrap modal integration
- Multi-section form organization
- Password visibility toggle
- Real-time validation feedback
- Role-based field visibility
- Form submission handling

**Usage**:
```csharp
<!-- In parent component -->
<UserCreateModal OnUserCreated="HandleUserCreated" />

<!-- Event handler in parent component -->
private async Task HandleUserCreated(UserCreateRequest userRequest)
{
    // Process user creation
    await LoadUsers();
}
```

**Parameters**:
- `OnUserCreated`: Event callback for successful user creation
- `ShowModal`: Controls modal visibility (optional)

**Form Sections**:
1. **Basic Information**: Username, full name, email
2. **Password Setup**: Password with confirmation
3. **Role Assignment**: User role selection
4. **Organizational Info**: Department, office location

**Validation Rules**:
```csharp
[Required(ErrorMessage = "Username is required")]
[StringLength(50, ErrorMessage = "Username cannot exceed 50 characters")]
[RegularExpression(@"^[a-zA-Z0-9_]+$", ErrorMessage = "Username can only contain letters, numbers, and underscores")]
public string Username { get; set; } = "";
```

---

## Component Patterns

### 🔄 Data Loading Pattern
```csharp
protected override async Task OnInitializedAsync()
{
    await LoadData();
}

private async Task LoadData()
{
    try
    {
        IsLoading = true;
        Data = await ApiService.GetDataAsync();
    }
    catch (Exception ex)
    {
        ErrorMessage = ex.Message;
        ShowError = true;
    }
    finally
    {
        IsLoading = false;
        StateHasChanged();
    }
}
```

### 📝 Form Validation Pattern
```razor
<EditForm Model="@Model" OnValidSubmit="@HandleValidSubmit">
    <DataAnnotationsValidator />
    <ValidationSummary />

    <div class="form-group">
        <label for="field">Field *</label>
        <InputText id="field" @bind-Value="Model.Field" class="form-control" />
        <ValidationMessage For="@(() => Model.Field)" class="text-danger" />
    </div>

    <button type="submit" disabled="@isLoading">Submit</button>
</EditForm>
```

### 🎭 Loading State Pattern
```razor
@if (IsLoading)
{
    <div class="loading-spinner">
        <span class="spinner spinner-sm"></span>
        Loading...
    </div>
}
else if (ShowError)
{
    <div class="alert alert-error">
        @ErrorMessage
    </div>
}
else
{
    @* Main component content *@
}
```

### 🎨 Responsive Design Pattern
```razor
<div class="row g-3">
    <div class="col-12 col-md-6 col-lg-4">
        <!-- Stack on mobile, 50% width on tablet, 33% on desktop -->
    </div>
</div>

<div class="d-none d-md-block">
    <!-- Hidden on mobile, visible on tablet+ -->
</div>
```

---

## Services Integration

### 🛡️ AuthService
```csharp
// Authentication service integration
@inject AuthService AuthService

// Authentication check
var isAuthenticated = await AuthService.IsAuthenticatedAsync();

// Get current user
var currentUser = await AuthService.GetCurrentUserAsync();

// Login/Logout
await AuthService.LoginAsync(loginRequest);
await AuthService.LogoutAsync();
```

### 🗺️ NavigationManager
```csharp
// Navigation service injection
@inject NavigationManager NavigationManager

// Navigation examples
NavigationManager.NavigateTo("/login");
NavigationManager.NavigateTo($"/trainings/{trainingId}");
NavigationManager.NavigateTo(NavigationManager.Uri, forceLoad: true);
```

---

## Styling and Theming

### 🎨 CSS Variables
```razor
<!-- Design system variables in CSS -->
:root {
    --text-sm: 0.875rem;
    --text-base: 1rem;
    --text-lg: 1.125rem;
    --text-xl: 1.25rem;
    --text-2xl: 1.5rem;
    --text-3xl: 1.875rem;

    --color-primary: #2563eb;
    --color-success: #10b981;
    --color-warning: #f59e0b;
    --color-error: #ef4444;
}
```

### 💅 Bootstrap Integration
```razor
<!-- Bootstrap utility classes -->
<div class="card shadow-sm">
    <div class="card-body">
        <h5 class="card-title">Title</h5>
        <p class="card-text">Content</p>
        <button class="btn btn-primary">Action</button>
    </div>
</div>
```

### 📱 Responsive Classes
```razor
<!-- Responsive design patterns -->
<div class="row">
    <div class="col-12 d-lg-none">Mobile only</div>
    <div class="col-12 d-none d-lg-block">Desktop only</div>
</div>
```

---

## Performance Considerations

### ⚡ Optimization Techniques
1. **Virtualization**: Use `Virtualize` component for large lists
2. **Lazy Loading**: Implement `if (visible)` for complex components
3. **State Management**: Keep component state minimal
4. **Data Caching**: Cache API responses appropriately
5. **Rendering Optimization**: Avoid unnecessary `StateHasChanged()` calls

### 🔄 Component Lifecycle
```csharp
protected override void OnParametersSet() { }
protected override void OnAfterRender(bool firstRender) { }
protected override async Task OnInitializedAsync() { }
protected override bool ShouldRender() { return true; }
```

### 💾 Memory Management
```csharp
// Dispose resources properly
public class MyComponent : ComponentBase, IDisposable
{
    private Timer _timer;

    public void Dispose()
    {
        _timer?.Dispose();
    }
}
```

---

## Testing Components

### 🧪 Unit Testing (bUnit)
```csharp
// Testing component rendering
var cut = RenderComponent<MyComponent>();

// Test parameter passing
cut.SetParametersAndRender(parameters => parameters
    .Add(p => p.Title, "Test Title"));

// Test event handlers
await cut.Find("button").ClickAsync();

// Assert DOM content
cut.Find("h1").MarkupMatches("<h1>Test Title</h1>");
```

### 🔧 Integration Testing
```csharp
// Test user interaction
await cut.Find("#username").ChangeAsync("testuser");
await cut.Find("#password").ChangeAsync("password123");
await cut.Find("form").SubmitAsync();

// Test navigation
cut.NavigateTo("/login");
```

---

## Best Practices

### 📋 Development Guidelines
1. **Component Design**: Single responsibility, focused purpose
2. **Parameter Validation**: Use `[Parameter]` with validation attributes
3. **Error Handling**: Comprehensive try-catch blocks
4. **Accessibility**: ARIA labels, keyboard navigation support
5. **Performance**: Minimal state, efficient rendering

### 🎨 UI/UX Standards
1. **Consistent Spacing**: Use spacing scale (2, 4, 8, 16px)
2. **Loading States**: Always show loading indicators
3. **Error Messages**: Clear, actionable error feedback
4. **Mobile First**: Design for mobile, enhance for desktop
5. **Color Usage**: Semantic color application (success, error, warning)

### 🔒 Security Considerations
1. **Input Validation**: Always validate user input
2. **Authentication**: Check user roles and permissions
3. **CSRF Protection**: Use antiforgery tokens for forms
4. **XSS Prevention**: Properly escape user-generated content
5. **Secure Storage**: Don't store sensitive data in component state

---

## Troubleshooting

### 🔧 Common Issues

**Component Not Rendering**:
- Check route configuration in `_Imports.razor`
- Verify component name and namespace
- Check for compilation errors

**State Not Updating**:
- Call `StateHasChanged()` after state updates
- Check if using `@bind-Value` correctly
- Verify event handler signatures

**JavaScript Interop Issues**:
- Ensure component is in interactive mode
- Check IJSRuntime injection
- Handle interop exceptions gracefully

**API Integration Problems**:
- Verify service registration in Program.cs
- Check base URL configuration
- Handle HTTP errors properly

---

## Migration Guide

### 🔄 .NET 7 to .NET 8 Migration
- Update Blazor Server to InteractiveServer render mode
- Migrate to new authentication patterns
- Update component lifecycle methods
- Upgrade to Bootstrap 5 components

### 📦 Component Migration Checklist
- [ ] Update namespaces and imports
- [ ] Migrate event handlers to new patterns
- [ ] Update parameter binding
- [ ] Test with new authentication flow
- [ ] Verify responsive design

---

## Future Enhancements

### 🚀 Planned Features
1. **WebAssembly Support**: Hybrid Blazor deployment
2. **Progressive Web App**: Offline support and push notifications
3. **Real-time Updates**: SignalR integration for live updates
4. **Advanced Search**: Elasticsearch integration
5. **Analytics Dashboard**: Enhanced reporting and metrics

### 🎨 UI Improvements
1. **Dark Mode**: Theme toggle support
2. **Advanced Charts**: Data visualization components
3. **Drag & Drop**: File upload and dashboard customization
4. **Keyboard Shortcuts**: Enhanced accessibility
5. **Internationalization**: Multi-language support

---

*Last updated: December 1, 2023*