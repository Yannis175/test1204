# Docker Janssen Configurator Tests

This directory contains comprehensive unit tests for the `docker-jans-configurator` Dockerfile.

## Test Coverage

The test suite covers:

### Base Image Tests (`test_base_image.py`)
- Base image validation (Bellsoft Liberica OpenJRE Alpine)
- Java version verification (Java 25)
- SHA256 digest validation
- Security best practices
- Image provenance from trusted registry

### Dockerfile Structure Tests (`test_dockerfile_structure.py`)
- Dockerfile structure and organization
- Best practices compliance
- Alpine package management
- Java configuration
- Python environment setup
- Git sparse checkout
- Security configurations
- Environment variable groups
- Script configuration

### Validation Tests (`test_dockerfile_validation.py`)
- Version consistency
- Build arguments
- Path consistency
- Requirements file validation
- Hadolint compliance
- OCI image metadata
- Entrypoint configuration

### Requirements Tests (`test_requirements.py`)
- Requirements.txt content validation
- Package version pinning
- No duplicate dependencies
- Documentation of pinned versions

## Running the Tests

### Prerequisites
```bash
pip install pytest
```

### Run all tests
```bash
cd docker-jans-configurator
pytest tests/
```

### Run specific test files
```bash
pytest tests/test_base_image.py
pytest tests/test_dockerfile_structure.py
pytest tests/test_dockerfile_validation.py
pytest tests/test_requirements.py
```

### Run with verbose output
```bash
pytest -v tests/
```

### Run specific test classes
```bash
pytest tests/test_base_image.py::TestBaseImage
pytest tests/test_base_image.py::TestJavaVersion
```

### Run specific test methods
```bash
pytest tests/test_base_image.py::TestBaseImage::test_base_image_is_java_25
pytest tests/test_base_image.py::TestBaseImage::test_sha256_digest_is_updated
```

## Test Organization

Tests are organized into classes by functionality:
- `TestBaseImage`: Base image validation
- `TestBaseImageSecurity`: Security-focused base image tests
- `TestJavaVersion`: Java version requirements
- `TestDockerfileStructure`: General structure tests
- `TestDockerfileBestPractices`: Best practices compliance
- `TestAlpinePackages`: Package installation tests
- `TestJavaConfiguration`: Java-specific configuration
- `TestPythonConfiguration`: Python environment tests
- `TestGitConfiguration`: Git sparse checkout tests
- `TestSecurityConfiguration`: Security settings
- `TestEnvironmentVariableGroups`: Environment variable validation
- `TestVersionConsistency`: Version consistency checks
- `TestBuildArguments`: Build argument validation
- `TestPathConsistency`: Path consistency validation
- `TestImageMetadata`: OCI metadata validation
- `TestEntrypointConfiguration`: Entrypoint and CMD tests

## What Changed

The primary change tested is the upgrade from:
- **Old**: `bellsoft/liberica-openjre-alpine:17.0.12@sha256:29cb2ee552c7c7a924b6a1b59802508dc5123e7edad1d65d575bbf07cd05fa6d`
- **New**: `bellsoft/liberica-openjre-alpine:25-37@sha256:218ff7542fc2e54b984cab13eac969f447365b55b053e9ec91f5a90415451f1a`

Tests specifically validate:
1. The new Java 25 version is being used
2. The old Java 17 version is NOT present
3. SHA256 digest has been updated correctly
4. All other Dockerfile configurations remain valid

## Test Examples

### Testing Base Image
```python
def test_base_image_is_java_25(self, dockerfile_lines):
    """Verify that the base image is using Java 25 (not Java 17)."""
    from_line = dockerfile_lines[0]
    
    # The new version should be Java 25
    assert "25-" in from_line or ":25" in from_line, \
        "Base image should be using Java 25"
    
    # Should NOT be Java 17
    assert "17.0.12" not in from_line, \
        "Base image should not be using Java 17.0.12 (old version)"
```

### Testing SHA256 Digest
```python
def test_sha256_digest_is_updated(self, dockerfile_lines):
    """Verify that SHA256 digest was updated (not using old Java 17 digest)."""
    from_line = dockerfile_lines[0]
    
    # Old Java 17 SHA256 digest that should NOT be present
    old_sha256 = "29cb2ee552c7c7a924b6a1b59802508dc5123e7edad1d65d575bbf07cd05fa6d"
    assert old_sha256 not in from_line, \
        "Should not be using the old Java 17 SHA256 digest"
    
    # New Java 25 SHA256 digest that should be present
    new_sha256 = "218ff7542fc2e54b984cab13eac969f447365b55b053e9ec91f5a90415451f1a"
    assert new_sha256 in from_line, \
        "Should be using the new Java 25 SHA256 digest"
```

## Adding New Tests

When adding new tests:
1. Follow the existing test class organization
2. Use descriptive test names: `test_<what_is_being_tested>`
3. Add docstrings explaining the test purpose
4. Use parametrize for testing multiple scenarios
5. Keep tests focused and atomic

Example:
```python
class TestNewFeature:
    """Test suite for new feature."""
    
    def test_feature_enabled(self, dockerfile_content):
        """Verify that the new feature is enabled."""
        assert "NEW_FEATURE=enabled" in dockerfile_content, \
            "New feature should be enabled"
```

## CI/CD Integration

These tests should be integrated into the CI/CD pipeline to:
- Validate Dockerfile changes before merge
- Ensure base image updates don't break functionality
- Maintain security and best practices compliance

### GitHub Actions Example
```yaml
name: Test Dockerfile

on:
  pull_request:
    paths:
      - 'docker-jans-configurator/Dockerfile'
      - 'docker-jans-configurator/requirements.txt'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install pytest
      - name: Run tests
        run: |
          cd docker-jans-configurator
          pytest tests/ -v
```

## Continuous Improvement

This test suite should be updated when:
- New Dockerfile instructions are added
- Base image versions change
- Security requirements evolve
- New best practices emerge
- Dependencies are updated

## Contributing

When contributing tests:
1. Ensure all tests pass before submitting PR
2. Add tests for any new Dockerfile changes
3. Update this README if adding new test categories
4. Follow existing code style and conventions
5. Write clear, descriptive test names and docstrings

## Troubleshooting

### Tests fail after Dockerfile change
- Review the specific test failure message
- Verify the Dockerfile change is intentional
- Update tests if the change is valid
- Fix the Dockerfile if the test caught an issue

### Import errors
```bash
# Install pytest if not already installed
pip install pytest

# Verify Python path
cd docker-jans-configurator
pytest tests/ -v
```

### Fixture errors
- Ensure conftest.py is in the tests directory
- Verify all fixtures are properly defined
- Check that file paths in fixtures are correct

## Test Statistics

Current test coverage:
- **Total test files**: 5
- **Total test classes**: 20+
- **Total test methods**: 100+
- **Lines of test code**: 800+

## License

These tests are part of the Janssen Project and are licensed under the Apache License 2.0.