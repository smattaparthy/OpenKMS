#!/usr/bin/env python3
"""
OpenKMS Test Runner
A comprehensive test runner for the OpenKMS backend application.
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle the result."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(command)}")
    print(f"{'-'*60}")

    result = subprocess.run(command, capture_output=True, text=True)

    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)

    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        return True
    else:
        print(f"❌ {description} - FAILED (Exit code: {result.returncode})")
        return False


def create_test_database():
    """Create and set up the test database."""
    print(f"{'='*60}")
    print("🗄️  Setting up test database")
    print(f"{'='*60}")

    # Check if test database exists, create if not
    commands = [
        ["psql", "-U", "postgres", "-c", "SELECT 1 FROM pg_database WHERE datname = 'openkms_test'"],
        ["psql", "-U", "postgres", "-c", "CREATE DATABASE openkms_test"],
        ["psql", "-U", "postgres", "-d", "openkms_test", "-c", "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""],
        ["psql", "-U", "postgres", "-d", "openkms_test", "-c", "CREATE EXTENSION IF NOT EXISTS \"pgcrypto\""],
    ]

    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 and "already exists" not in result.stderr:
            print(f"⚠️ Database setup warning: {result.stderr}")

    print("✅ Test database setup completed")


def run_unit_tests():
    """Run unit tests only."""
    return run_command(
        ["pytest", "tests/unit/", "-v", "-x", "--cov=app", "--cov-report=term-missing"],
        "Running Unit Tests"
    )


def run_integration_tests():
    """Run integration tests only."""
    return run_command(
        ["pytest", "tests/integration/", "-v", "-x", "--cov=app", "--cov-report=term-missing"],
        "Running Integration Tests"
    )


def run_all_tests():
    """Run all tests."""
    return run_command(
        ["pytest", "tests/", "-v", "--cov=app", "--cov-report=html", "--cov-report=term-missing"],
        "Running All Tests"
    )


def run_tests_with_markers(markers):
    """Run tests with specific markers."""
    marker_expr = " or ".join(markers)
    return run_command(
        ["pytest", "-v", "-x", f"-m \"{marker_expr}\""],
        f"Running Tests with Markers: {', '.join(markers)}"
    )


def run_performance_tests():
    """Run performance tests (if any)."""
    return run_command(
        ["pytest", "-v", "-x", "-m", "slow"],
        "Running Performance Tests"
    )


def generate_coverage_report():
    """Generate comprehensive coverage report."""
    success = run_command(
        ["pytest", "tests/", "--cov=app", "--cov-report=html:htmlcov", "--cov-report=xml:coverage.xml"],
        "Generating Coverage Report"
    )

    if success:
        print("\n📊 Coverage reports generated:")
        print("   - HTML: htmlcov/index.html")
        print("   - XML: coverage.xml")

    return success


def run_smoke_tests():
    """Run basic smoke tests to ensure critical functionality works."""
    return run_command(
        ["pytest", "-v", "-x", "-m", "api", "--tb=short"],
        "Running Smoke Tests"
    )


def security_scan():
    """Run basic security scan on the codebase."""
    print(f"{'='*60}")
    print("🔒 Running Security Scan")
    print(f"{'='*60}")

    security_tools = []

    # Check for bandit
    try:
        subprocess.run(["bandit", "--version"], capture_output=True, check=True)
        security_tools.append("bandit")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Bandit not installed. Install with: pip install bandit")

    # Check for saftey
    try:
        subprocess.run(["safety", "--version"], capture_output=True, check=True)
        security_tools.append("safety")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Safety not installed. Install with: pip install safety")

    success = True

    if "bandit" in security_tools:
        success &= run_command(
            ["bandit", "-r", "app/", "-f", "json"],
            "Running Bandit Security Scan"
        )

    if "safety" in security_tools:
        success &= run_command(
            ["safety", "check"],
            "Running Safety Vulnerability Check"
        )

    return success


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="OpenKMS Test Runner")
    parser.add_argument("--type", choices=["unit", "integration", "all", "smoke", "performance", "coverage"],
                       default="all", help="Type of tests to run")
    parser.add_argument("--markers", nargs="+",
                       choices=["unit", "integration", "slow", "auth", "api", "database", "service"],
                       help="Test markers to run")
    parser.add_argument("--security", action="store_true",
                       help="Run security scans")
    parser.add_argument("--setup-db", action="store_true",
                       help="Set up test database")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")

    args = parser.parse_args()

    print("🚀 OpenKMS Test Runner")
    print(f"{'='*60}")

    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    success_count = 0
    total_count = 0

    # Set up test database if requested
    if args.setup_db:
        create_test_database()

    # Run tests based on type
    if args.markers:
        total_count += 1
        if run_tests_with_markers(args.markers):
            success_count += 1
    else:
        test_functions = {
            "unit": run_unit_tests,
            "integration": run_integration_tests,
            "all": run_all_tests,
            "smoke": run_smoke_tests,
            "performance": run_performance_tests,
            "coverage": generate_coverage_report,
        }

        if args.type in test_functions:
            total_count += 1
            if test_functions[args.type]():
                success_count += 1

    # Run security scan if requested
    if args.security:
        total_count += 1
        if security_scan():
            success_count += 1

    # Print summary
    print(f"\n{'='*60}")
    print("📋 Test Summary")
    print(f"{'='*60}")
    print(f"Total test suites: {total_count}")
    print(f"Passed: {success_count}")
    print(f"Failed: {total_count - success_count}")

    if success_count == total_count:
        print("🎉 All tests passed! 🎉")
        sys.exit(0)
    else:
        print("💥 Some tests failed! 💥")
        sys.exit(1)


if __name__ == "__main__":
    main()