#!/bin/bash

# OpenKMS Frontend Test Runner
# A comprehensive test runner for the Blazor frontend application

echo "🚀 OpenKMS Frontend Test Runner"
echo "=================================="

# Set script to exit on any error
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to check if dotnet is available
check_dotnet() {
    if ! command -v dotnet &> /dev/null; then
        print_error ".NET SDK is not installed or not in PATH"
        echo "Please install .NET SDK 8.0 or later"
        exit 1
    fi
    print_status ".NET SDK found: $(dotnet --version)"
}

# Function to clean previous builds
clean_build() {
    echo "🧹 Cleaning previous builds..."
    dotnet clean
    if [ $? -eq 0 ]; then
        print_status "Build cleaned successfully"
    else
        print_warning "Clean command failed (may not have previous build)"
    fi
}

# Function to build the test project
build_tests() {
    echo "🏗️  Building test project..."
    dotnet build OpenKMS.Frontend.Tests.csproj

    if [ $? -eq 0 ]; then
        print_status "Test project built successfully"
    else
        print_error "Test project build failed"
        exit 1
    fi
}

# Function to run all tests
run_all_tests() {
    echo "🧪 Running all tests..."
    dotnet test OpenKMS.Frontend.Tests.csproj --logger "console;verbosity=detailed" --collect:"XPlat Code Coverage"

    if [ $? -eq 0 ]; then
        print_status "All tests passed!"
    else
        print_error "Some tests failed"
        exit 1
    fi
}

# Function to run unit tests only
run_unit_tests() {
    echo "🧪 Running unit tests..."
    dotnet test OpenKMS.Frontend.Tests.csproj --filter "Category=Unit" --logger "console;verbosity=detailed"

    if [ $? -eq 0 ]; then
        print_status "Unit tests passed!"
    else
        print_error "Unit tests failed"
        exit 1
    fi
}

# Function to run component tests
run_component_tests() {
    echo "🧪 Running component tests..."
    dotnet test OpenKMS.Frontend.Tests.csproj --filter "Category=Component" --logger "console;verbosity=detailed"

    if [ $? -eq 0 ]; then
        print_status "Component tests passed!"
    else
        print_error "Component tests failed"
        exit 1
    fi
}

# Function to run service tests
run_service_tests() {
    echo "🧪 Running service tests..."
    dotnet test OpenKMS.Frontend.Tests.csproj --filter "Category=Service" --logger "console;verbosity=detailed"

    if [ $? -eq 0 ]; then
        print_status "Service tests passed!"
    else
        print_error "Service tests failed"
        exit 1
    fi
}

# Function to run tests with coverage
run_coverage() {
    echo "📊 Running tests with coverage..."
    dotnet test OpenKMS.Frontend.Tests.csproj --collect:"XPlat Code Coverage" --results-directory TestResults

    if [ $? -eq 0 ]; then
        print_status "Tests with coverage completed!"
        echo " Coverage report generated in TestResults directory"

        # Check if coverage report exists and display location
        if [ -f "TestResults/coverage.cobertura.xml" ]; then
            echo " XML Coverage Report: TestResults/coverage.cobertura.xml"
        fi

        if [ -f "TestResults/coverage.opencover.xml" ]; then
            echo " OpenCover Report: TestResults/coverage.opencover.xml"
        fi
    else
        print_error "Tests with coverage failed"
        exit 1
    fi
}

# Function to run specific test file
run_specific_test() {
    local test_file=$1

    if [ -z "$test_file" ]; then
        print_error "No test file specified"
        exit 1
    fi

    echo "🧪 Running specific test: $test_file"
    dotnet test OpenKMS.Frontend.Tests.csproj --filter "FullyQualifiedName~$test_file" --logger "console;verbosity=detailed"

    if [ $? -eq 0 ]; then
        print_status "Specific test passed!"
    else
        print_error "Specific test failed"
        exit 1
    fi
}

# Function to run tests in verbose mode
run_verbose_tests() {
    echo "🔍 Running tests in verbose mode..."
    dotnet test OpenKMS.Frontend.Tests.csproj --logger "console;verbosity=diagnostic"

    if [ $? -eq 0 ]; then
        print_status "Verbose test run completed!"
    else
        print_error "Verbose test run failed"
        exit 1
    fi
}

# Function to show test project structure
show_structure() {
    echo "📁 Test Project Structure:"
    echo "├── OpenKMS.Frontend.Tests.csproj"
    echo "└── Tests/"
    echo "    ├── Components/"
    echo "    │   └── LoginTests.cs"
    echo "    └── Services/"
    echo "        └── AuthServiceTests.cs"
    echo ""

    if [ -d "Tests" ]; then
        echo "📋 Files in Tests directory:"
        find Tests -name "*.cs" | while read file; do
            echo "   ├── $file"
        done
    else
        print_warning "Tests directory not found"
    fi
}

# Function to generate test report
generate_report() {
    echo "📈 Generating test report..."

    # Run tests and capture output
    dotnet test OpenKMS.Frontend.Tests.csproj --logger "trx;LogFileName=TestResults.trx" --results-directory TestResults 2>&1 | tee test_output.log

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        print_status "Tests completed and report generated!"

        if [ -f "TestResults/TestResults.trx" ]; then
            echo " TRX Report: TestResults/TestResults.trx"
        fi

        if [ -f "test_output.log" ]; then
            echo " Log File: test_output.log"
        fi
    else
        print_error "Tests failed, but report still generated"
        exit 1
    fi
}

# Function to install missing dependencies
install_dependencies() {
    echo "📦 Installing test dependencies..."
    dotnet restore OpenKMS.Frontend.Tests.csproj

    if [ $? -eq 0 ]; then
        print_status "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
}

# Main script execution
main() {
    # Parse command line arguments
    case "${1:-all}" in
        "all")
            check_dotnet
            install_dependencies
            clean_build
            build_tests
            run_all_tests
            ;;
        "unit")
            check_dotnet
            install_dependencies
            build_tests
            run_unit_tests
            ;;
        "component")
            check_dotnet
            install_dependencies
            build_tests
            run_component_tests
            ;;
        "service")
            check_dotnet
            install_dependencies
            build_tests
            run_service_tests
            ;;
        "coverage")
            check_dotnet
            install_dependencies
            clean_build
            build_tests
            run_coverage
            ;;
        "specific")
            check_dotnet
            install_dependencies
            build_tests
            run_specific_test "$2"
            ;;
        "verbose")
            check_dotnet
            install_dependencies
            build_tests
            run_verbose_tests
            ;;
        "report")
            check_dotnet
            install_dependencies
            build_tests
            generate_report
            ;;
        "clean")
            clean_build
            ;;
        "build")
            check_dotnet
            install_dependencies
            build_tests
            ;;
        "structure")
            show_structure
            ;;
        "install")
            install_dependencies
            ;;
        "help"|"-h"|"--help")
            echo "OpenKMS Frontend Test Runner"
            echo ""
            echo "Usage: $0 [command] [options]"
            echo ""
            echo "Commands:"
            echo "  all          Run all tests (default)"
            echo "  unit         Run unit tests only"
            echo "  component    Run component tests only"
            echo "  service      Run service tests only"
            echo "  coverage     Run tests with code coverage"
            echo "  specific     Run specific test file (usage: $0 specific ClassName)"
            echo "  verbose      Run tests in verbose mode"
            echo "  report       Generate test report"
            echo "  clean        Clean build artifacts"
            echo "  build        Build test project only"
            echo "  structure    Show test project structure"
            echo "  install      Install test dependencies"
            echo "  help         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run all tests"
            echo "  $0 component           # Run component tests"
            echo "  $0 coverage            # Run tests with coverage"
            echo "  $0 specific LoginTests # Run specific test class"
            echo "  $0 help                # Show help"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' to see available commands"
            exit 1
            ;;
    esac
}

# Create TestResults directory if it doesn't exist
mkdir -p TestResults

# Execute main function
main "$@"

echo ""
echo "🎉 Test execution completed!"