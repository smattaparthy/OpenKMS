# OpenKMS - Open Knowledge Management System

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

OpenKMS is a comprehensive knowledge management system designed to streamline training administration, user management, and knowledge sharing within organizations. Built with modern web technologies, it provides a robust platform for managing training programs, user registrations, and learning resources.

## 🌟 Features

### Core Functionality
- **Training Management**: Create, manage, and track training programs and schedules
- **User Administration**: Complete user lifecycle management with role-based access control
- **Registration System**: Streamlined training enrollment and attendance tracking
- **Knowledge Base**: Centralized repository for learning materials and documentation
- **Admin Dashboard**: Comprehensive dashboard for system administration and analytics

### Technical Features
- **Modern UI/UX**: Responsive web interface built with Blazor Server and Bootstrap
- **RESTful API**: FastAPI backend with automatic API documentation
- **Authentication & Authorization**: JWT-based authentication with role-based permissions
- **Database Management**: PostgreSQL with async SQLAlchemy for optimal performance
- **Caching Layer**: Redis integration for improved performance
- **Containerized**: Docker-compose orchestration for easy deployment

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/openkms.git
   cd openkms
   ```

2. **Set up environment**
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

## 📋 Architecture

### System Overview
OpenKMS follows a modern microservices architecture with clear separation of concerns:

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Frontend          │    │   Backend          │    │   Infrastructure   │
│                     │    │                     │    │                     │
│  • Blazor Server   │◄──►│  • FastAPI         │◄──►│  • PostgreSQL      │
│  • Bootstrap UI    │    │  • SQLAlchemy      │    │  • Redis           │
│  • C#/.NET 8      │    │  • JWT Auth        │    │  • Docker          │
│  • SignalR        │    │  • Pydantic        │    │  • Nginx (Prod)    │
│                     │    │  • Alembic         │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### Technology Stack

#### Frontend
- **Framework**: ASP.NET Core 8 Blazor Server
- **UI Framework**: Bootstrap 5 with custom design system
- **Language**: C# 12
- **Authentication**: JWT tokens with local storage
- **Communication**: SignalR for real-time updates

#### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.9+
- **ORM**: SQLAlchemy 2.0 with async support
- **Authentication**: JWT with Pydantic validation
- **API Documentation**: OpenAPI/Swagger auto-generated
- **Database Migrations**: Alembic

#### Infrastructure
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx (Production)
- **SSL/TLS**: Let's Encrypt support

## 🛠 Development

### Development Setup
For detailed development instructions, see [README.DEVELOPMENT.md](README.DEVELOPMENT.md).

### Key Development Commands
```bash
# Start development environment
./scripts/dev-commands.sh start

# View logs
./scripts/dev-commands.sh logs
./scripts/dev-commands.sh logs-backend
./scripts/dev-commands.sh logs-frontend

# Run tests
./scripts/dev-commands.sh test-backend
./scripts/dev-commands.sh test-frontend

# Database operations
./scripts/dev-commands.sh migrate      # Run migrations
./scripts/dev-commands.sh migrate-new   # Create migration
./scripts/dev-commands.sh backup       # Create backup
```

### Project Structure
```
openkms/
├── openkms-backend/          # Python FastAPI backend
│   ├── app/
│   │   ├── core/            # Core configuration
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── api/             # API endpoints
│   │   └── services/        # Business logic
│   ├── tests/               # Test files
│   └── requirements.txt     # Dependencies
├── openkms-frontend/        # C# Blazor frontend
│   ├── Components/          # Blazor components
│   │   ├── Auth/           # Authentication components
│   │   ├── Admin/          # Admin components
│   │   ├── Training/       # Training components
│   │   └── Layout/         # Layout components
│   ├── Services/           # Application services
│   ├── Models/             # Data models
│   └── Properties/         # Build configuration
├── scripts/                 # Development scripts
├── docs/                   # Documentation
├── nginx/                  # Nginx configuration
└── docker-compose.yml       # Container orchestration
```

## 📚 Documentation

### Core Documentation
- [Development Guide](README.DEVELOPMENT.md) - Comprehensive development setup and workflow
- [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions
- [API Documentation](docs/API.md) - Backend API reference
- [Component Documentation](docs/COMPONENTS.md) - Frontend component reference

### User Guides
- [Admin Guide](docs/ADMIN_GUIDE.md) - System administration tasks
- [Training Management](docs/TRAINING_GUIDE.md) - Creating and managing training programs
- [User Management](docs/USER_MANAGEMENT.md) - User administration and permissions

## 🔧 Configuration

### Environment Variables
The application uses environment variables for configuration. Copy `.env.example` to `.env`:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://openkms:your_secure_password@postgres:5432/openkms

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-very-secure-secret-key-here
ALGORITHM=HS256

# Application
DEBUG=False          # Set to False in production
LOG_LEVEL=INFO
ALLOWED_HOSTS=yourdomain.com

# URLs
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://api.yourdomain.com
```

## 🌐 Deployment

### Quick Deployment
For production deployment, see [DEPLOYMENT.md](DEPLOYMENT.md).

### Production Setup
```bash
# Configure production environment
cp .env.example .env.production
# Edit .env.production with production values

# Deploy with production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Deployment Options
- **Docker Compose**: Recommended for single-server deployments
- **Kubernetes**: For orchestrating multiple containers (see deployment guide)
- **Cloud Platforms**: AWS, Azure, GCP deployment guides available

## 🔒 Security

### Security Features
- **JWT Authentication**: Stateless authentication with secure token handling
- **Role-Based Access Control**: Granular permissions for different user roles
- **Password Security**: Password hashing with bcrypt and complexity requirements
- **Input Validation**: Comprehensive validation using Pydantic schemas
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **HTTPS Enforcement**: SSL/TLS encryption for all communications

### Security Best Practices
- Secure password requirements (12+ characters, complexity enforced)
- Regular security updates for all dependencies
- Environment variable secrets management
- Request rate limiting
- CORS configuration
- Security headers implementation

## 🎯 User Roles & Permissions

### Available Roles
- **EMPLOYEE**: Basic user access, can browse and register for trainings
- **KNOWLEDGE_MANAGER**: Can create and manage training programs
- **ADMIN**: Full system access, user management, and system configuration

### Permission Matrix
| Feature | EMPLOYEE | KNOWLEDGE_MANAGER | ADMIN |
|---------|----------|-------------------|-------|
| View Trainings | ✅ | ✅ | ✅ |
| Register for Trainings | ✅ | ✅ | ✅ |
| Create Trainings | ❌ | ✅ | ✅ |
| Manage Users | ❌ | ❌ | ✅ |
| System Administration | ❌ | ❌ | ✅ |
| View Reports | 🔒* | ✅ | ✅ |

*Limited to own attendance data

## 📊 Monitoring & Analytics

### Application Monitoring
- **Health Checks**: Automatic health monitoring for all services
- **Performance Metrics**: Request times, database queries, cache performance
- **Error Tracking**: Comprehensive error logging and alerting
- **User Analytics**: Training completion rates, user engagement metrics

### Monitoring Tools
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Dashboard visualization
- **ELK Stack**: Log aggregation and analysis
- **Sentry**: Error tracking and reporting

## 🔄 API Integrations

### Supported Integrations
- **LDAP/Active Directory**: Enterprise user authentication
- **OAuth 2.0**: Third-party authentication providers
- **Webhooks**: Event notifications to external systems
- **REST API**: Full API for external system integration

### Integration Points
- User synchronization with HR systems
- Training content management systems
- Learning record stores (LRS)
- Email and notification systems

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- **Backend**: Follow PEP 8, use black formatter, write comprehensive tests
- **Frontend**: Follow C# naming conventions, use XML documentation
- **Testing**: Maintain test coverage above 80% for all components

### Bug Reports
For bug reports and feature requests, please use the [GitHub Issues](https://github.com/your-org/openkms/issues) page.

## 📈 Performance

### Performance Benchmarks
- **Response Time**: <200ms for API endpoints (95th percentile)
- **Database Queries**: <50ms for common operations with proper indexing
- **Concurrent Users**: 1000+ concurrent users with proper scaling
- **Database Size**: Optimized for 100,000+ user records

### Optimization Features
- Database indexing strategy
- Redis caching for frequently accessed data
- Async processing for non-blocking operations
- CDN support for static assets
- Database connection pooling

## 🧪 Testing

### Testing Strategy
- **Unit Tests**: Component-level testing with mocking
- **Integration Tests**: API endpoint testing with database
- **End-to-End Tests**: Full user journey testing with Playwright
- **Load Testing**: Performance testing under peak load scenarios

### Test Coverage
- **Backend**: pytest with 80%+ coverage requirement
- **Frontend**: xUnit with bUnit for Blazor component testing
- **API**: Automated testing with pytest + httpx
- **E2E**: Playwright for critical user workflows

## 🆘 Support

### Getting Help
- **Documentation**: Check the comprehensive guides in the `docs/` directory
- **Issues**: [GitHub Issues](https://github.com/your-org/openkms/issues) for bug reports
- **Discussions**: [GitHub Discussions](https://github.com/your-org/openkms/discussions) for questions
- **Email**: support@openkms.com for enterprise support

### Troubleshooting
For common issues and solutions, see the troubleshooting sections in:
- [Development Guide](README.DEVELOPMENT.md#troubleshooting)
- [Deployment Guide](DEPLOYMENT.md#troubleshooting)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI Team**: For the excellent web framework
- **Microsoft**: For the Blazor framework and .NET ecosystem
- **Bootstrap Team**: For the responsive UI framework
- **PostgreSQL**: For the robust database system
- **Docker Team**: For containerization technology

## 📞 Contact

- **Website**: https://openkms.com
- **Email**: info@openkms.com
- **Twitter**: @openkms
- **GitHub**: https://github.com/your-org/openkms

---

![OpenKMS Logo](https://openkms.com/logo.png)

*Empowering organizations through streamlined knowledge management and training administration.*