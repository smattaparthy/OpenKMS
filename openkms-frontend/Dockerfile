# Use ASP.NET 8.0 SDK for build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app

# Copy main project file and restore dependencies
COPY openkms-frontend.csproj ./
RUN dotnet restore openkms-frontend.csproj

# Copy only the necessary source files for the main application
# Exclude test files and unnecessary directories
COPY Program.cs ./
COPY Properties/ ./Properties/
COPY Components/ ./Components/
COPY Services/ ./Services/
COPY Models/ ./Models/
COPY Handlers/ ./Handlers/
COPY appsettings.json ./
COPY appsettings.Development.json ./
COPY wwwroot/ ./wwwroot/

# Build the application
RUN dotnet build "openkms-frontend.csproj" -c Release -o /app/build

# Publish the application
FROM build AS publish
RUN dotnet publish "openkms-frontend.csproj" -c Release -o /app/publish

# Final stage - use ASP.NET runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
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

# Copy published files
COPY --from=publish /app/publish .

# Expose port (Blazor Server uses different port than backend)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080 || exit 1

# Set environment variables for production
ENV ASPNETCORE_URLS=http://+:8080
ENV ASPNETCORE_ENVIRONMENT=Production

# Run the application
ENTRYPOINT ["dotnet", "OpenKMS.Frontend.dll"]