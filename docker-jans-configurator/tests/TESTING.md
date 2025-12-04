# Comprehensive Testing Guide for Docker Jans Configurator

## Overview

This test suite provides comprehensive validation for the docker-jans-configurator component, focusing on the Dockerfile upgrade from Java 17 to Java 25 and ensuring all functionality remains intact.

## Test Coverage

### 1. Dockerfile Validation (`test_dockerfile.py`)
- **423 lines of tests**
- Base image verification (BellSoft Liberica JRE Alpine 25)
- SHA256 digest pinning for reproducibility
- Security best practices (non-root user, no hardcoded secrets)
- Package management (APK cache cleanup, build deps removal)
- Environment variable configuration
- OCI label compliance
- Directory structure and permissions
- Entrypoint configuration
- Build optimization

### 2. Bootstrap Script Tests (`test_bootstrap.py`)
- **446 lines of tests**
- Template encoding functionality
- OpenID key generation (RS256, ES256, etc.)
- PKCS12 certificate generation
- Context manager operations
- Configuration and secret management
- Error handling and edge cases

### 3. Settings Configuration Tests (`test_settings.py`)
- **135 lines of tests**
- Logging configuration validation
- Log format verification
- Handler configuration
- Logger hierarchy testing

### 4. Requirements Validation (`test_requirements.py`)
- **163 lines of tests**
- Package specification validation
- Version pinning for security
- No duplicate dependencies
- grpcio version pinning (aligned with Alpine package)
- Local dependency paths

### 5. Container Structure Tests (`test_container_structure.py`)
- **137 lines of tests**
- Runtime validation (requires built image)
- Package installation verification
- User and permission checks
- Entrypoint execution tests

### 6. Test Infrastructure
- `conftest.py`: Shared fixtures and test utilities (106 lines)
- `pytest.ini`: Test configuration and markers
- `run_tests.sh`: Convenient test runner script
- `README.md`: Quick reference guide

## Total Test Coverage: 1,522 lines

## Running Tests

### Quick Start
```bash
# Navigate to the docker-jans-configurator directory
cd docker-jans-configurator

# Run all unit tests (no container required)
pytest tests/ -m "not integration" -v

# Run with test runner script
./tests/run_tests.sh unit
```

### Detailed Test Execution

#### 1. All Tests
```bash
pytest tests/ -v
```

#### 2. Specific Test File
```bash
pytest tests/test_dockerfile.py -v
pytest tests/test_bootstrap.py -v
pytest tests/test_requirements.py -v
```

#### 3. Specific Test Class
```bash
pytest tests/test_dockerfile.py::TestBaseImage -v
pytest tests/test_bootstrap.py::TestCtxManager -v
```

#### 4. Specific Test Function
```bash
pytest tests/test_dockerfile.py::TestBaseImage::test_java_version_is_25 -v
```

#### 5. With Coverage Report
```bash
pytest tests/ --cov=scripts --cov-report=term-missing --cov-report=html
# View coverage: open htmlcov/index.html
```

#### 6. Integration Tests (requires built image)
```bash
# Build the image first
make build-dev

# Run integration tests
pytest tests/ -m integration -v
```

## Test Markers

Tests are organized with markers for selective execution:

- `@pytest.mark.unit`: Unit tests (default, no external dependencies)
- `@pytest.mark.integration`: Integration tests (require container)
- `@pytest.mark.security`: Security-focused tests
- `@pytest.mark.slow`: Long-running tests

### Examples
```bash
# Run only unit tests
pytest tests/ -m unit -v

# Run only security tests
pytest tests/ -m security -v

# Skip slow tests
pytest tests/ -m "not slow" -v

# Run unit but not integration
pytest tests/ -m "not integration" -v
```

## CI/CD Integration

### Recommended Pipeline Stages

#### Stage 1: Static Analysis (Fast)
```yaml
- name: Validate Dockerfile
  run: |
    cd docker-jans-configurator
    pytest tests/test_dockerfile.py -v
    pytest tests/test_requirements.py -v
    pytest tests/test_settings.py -v
```

#### Stage 2: Unit Tests
```yaml
- name: Run Unit Tests
  run: |
    cd docker-jans-configurator
    pip install -r requirements.txt
    pytest tests/ -m "not integration" --cov=scripts
```

#### Stage 3: Build & Integration Tests
```yaml
- name: Build and Test Image
  run: |
    cd docker-jans-configurator
    make build-dev
    pytest tests/ -m integration -v
```

## Test Requirements

### Python Dependencies
```bash
pip install pytest pytest-cov
```

### Optional (for enhanced testing)
```bash
pip install pytest-xdist  # Parallel test execution
pip install pytest-html   # HTML test reports
```

## Key Test Scenarios

### Java 25 Upgrade Validation
✓ Base image uses Java 25 (`:25-37`)
✓ SHA256 digest is pinned for reproducibility
✓ Alpine variant for minimal size
✓ JRE (not full JDK) for smaller footprint

### Security Validation
✓ Non-root user (UID 1000)
✓ No hardcoded secrets
✓ Tini as init system for signal handling
✓ Group permissions for OpenShift compatibility

### Build Optimization
✓ APK cache cleaned
✓ Build dependencies removed
✓ Temporary files cleaned
✓ Reasonable layer count

### Functionality Validation
✓ Bootstrap script imports work
✓ OpenID key generation functions
✓ Certificate generation functions
✓ Context management operations
✓ Configuration and secret handling

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Ensure scripts directory is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/scripts"
pytest tests/
```

#### 2. Missing Dependencies
```bash
# Install test dependencies
pip install -r requirements.txt
pip install pytest pytest-cov
```

#### 3. Integration Tests Fail
```bash
# Build image first
make build-dev
# Then run integration tests
pytest tests/ -m integration
```

## Contributing New Tests

When adding new tests:

1. **Follow naming conventions**: `test_*.py` for files, `Test*` for classes, `test_*` for functions
2. **Add docstrings**: Explain what each test validates
3. **Use descriptive names**: Test names should clearly indicate purpose
4. **Group related tests**: Use classes to organize related test cases
5. **Add appropriate markers**: Use `@pytest.mark.*` for categorization
6. **Update documentation**: Add new tests to this guide

### Example Test Template
```python
class TestNewFeature:
    """Test new feature functionality."""

    def test_feature_basic_case(self, fixture):
        """Verify feature works in basic scenario."""
        # Arrange
        input_data = "test"
        
        # Act
        result = feature_function(input_data)
        
        # Assert
        assert result == expected, "Feature should produce expected output"

    def test_feature_edge_case(self):
        """Verify feature handles edge cases."""
        # Test implementation
        pass
```

## Continuous Improvement

This test suite will evolve with the codebase. Suggestions for expansion:

- [ ] Add performance benchmarks for key generation
- [ ] Add security scanning integration (trivy, grype)
- [ ] Add mutation testing for test quality verification
- [ ] Add container structure tests using container-structure-test
- [ ] Add end-to-end integration tests with real backends

## Support

For questions or issues with tests:
1. Check this documentation
2. Review test docstrings
3. Check pytest output for detailed error messages
4. Review CI/CD pipeline logs