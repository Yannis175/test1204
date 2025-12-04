#!/bin/bash
# Test runner script for docker-jans-configurator
#
# Usage:
#   ./run_tests.sh              # Run all tests
#   ./run_tests.sh unit         # Run only unit tests
#   ./run_tests.sh integration  # Run only integration tests
#   ./run_tests.sh coverage     # Run with coverage report

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Docker Jans Configurator Test Runner${NC}"
echo "======================================"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install it with: pip install pytest pytest-cov"
    exit 1
fi

# Determine test mode
MODE="${1:-all}"

case "$MODE" in
    unit)
        echo -e "${YELLOW}Running unit tests only...${NC}"
        pytest tests/ -m "not integration" -v
        ;;
    integration)
        echo -e "${YELLOW}Running integration tests...${NC}"
        echo -e "${YELLOW}Note: Integration tests require built container image${NC}"
        pytest tests/ -m integration -v
        ;;
    coverage)
        echo -e "${YELLOW}Running tests with coverage...${NC}"
        pytest tests/ --cov=scripts --cov-report=term-missing --cov-report=html -v
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    quick)
        echo -e "${YELLOW}Running quick tests (unit only, less verbose)...${NC}"
        pytest tests/ -m "not integration" --tb=short
        ;;
    all)
        echo -e "${YELLOW}Running all tests...${NC}"
        pytest tests/ -v
        ;;
    *)
        echo -e "${RED}Unknown mode: $MODE${NC}"
        echo "Usage: $0 {all|unit|integration|coverage|quick}"
        exit 1
        ;;
esac

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
fi

exit $EXIT_CODE