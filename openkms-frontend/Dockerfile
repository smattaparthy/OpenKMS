# Use ASP.NET 8.0 runtime for optimal performance
FROM mcr.microsoft.com/dotnet/sdk:8.0-bullseye-slim AS build
WORKDIR /app

# Copy .csproj file and restore dependencies
COPY *.csproj ./
RUN dotnet restore

# Copy rest of the files and build the application
COPY . .
WORKDIR "/app"
RUN dotnet build "OpenKMS.Frontend.csproj" -c Release -o /app/build

# Publish the application
FROM build AS publish
RUN dotnet publish "OpenKMS.Frontend.csproj" -c Release -o /app/publish

# Final stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0-bullseye-slim AS final
WORKDIR /app

# Install additional dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        wget \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
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