# Use ASP.NET 8.0 SDK for development
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS final
WORKDIR /app

# Install additional dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        wget \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (ignore if already exists)
RUN useradd --create-home --shell /bin/bash app 2>/dev/null || true \
    && chown -R app:app /app || true
USER app

# Expose port
EXPOSE 8080

# Set environment variables for development
ENV ASPNETCORE_URLS=http://+:8080
ENV ASPNETCORE_ENVIRONMENT=Development

# Default command (will be overridden by docker-compose)
ENTRYPOINT ["dotnet", "run", "--project", "openkms-frontend.csproj", "--urls", "http://+:8080"]