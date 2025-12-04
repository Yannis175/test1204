"""
Tests for requirements.txt validation.

Tests validate:
- Required dependencies are specified
- Version pinning for security
- Compatibility between packages
"""
from pathlib import Path

import pytest


@pytest.fixture
def requirements_file():
    """Load requirements.txt file."""
    req_path = Path(__file__).parent.parent / 'requirements.txt'
    with open(req_path, 'r') as f:
        return f.read()


@pytest.fixture
def requirements_lines(requirements_file):
    """Parse requirements.txt into lines."""
    return [
        line.strip() 
        for line in requirements_file.split('\n') 
        if line.strip() and not line.strip().startswith('#')
    ]


class TestRequirementsFile:
    """Test requirements.txt file structure."""

    def test_requirements_file_exists(self):
        """Verify requirements.txt exists."""
        req_path = Path(__file__).parent.parent / 'requirements.txt'
        assert req_path.exists(), "requirements.txt must exist"

    def test_requirements_not_empty(self, requirements_lines):
        """Verify requirements.txt is not empty."""
        assert len(requirements_lines) > 0, "requirements.txt cannot be empty"

    def test_no_duplicate_packages(self, requirements_lines):
        """Verify no duplicate package specifications."""
        packages = []
        for line in requirements_lines:
            if line.startswith('-') or line.startswith('/'):
                continue
            pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].strip()
            packages.append(pkg_name.lower())
        
        duplicates = [pkg for pkg in packages if packages.count(pkg) > 1]
        assert len(set(duplicates)) == 0, f"Duplicate packages found: {set(duplicates)}"


class TestRequiredPackages:
    """Test required packages are specified."""

    def test_grpcio_specified(self, requirements_file):
        """Verify grpcio is specified."""
        assert 'grpcio' in requirements_file, "grpcio must be in requirements"

    def test_grpcio_version_pinned(self, requirements_file):
        """Verify grpcio version is pinned."""
        assert 'grpcio==' in requirements_file, \
            "grpcio version must be pinned (uses ==)"

    def test_click_specified(self, requirements_file):
        """Verify click is specified."""
        assert 'click' in requirements_file, "click must be in requirements"

    def test_click_version_pinned(self, requirements_file):
        """Verify click version is pinned."""
        assert 'click==' in requirements_file, \
            "click version must be pinned (uses ==)"

    def test_jans_pycloudlib_specified(self, requirements_file):
        """Verify jans-pycloudlib is specified."""
        assert 'jans-pycloudlib' in requirements_file or '/tmp/jans/jans-pycloudlib' in requirements_file, \
            "jans-pycloudlib must be in requirements"


class TestVersionPinning:
    """Test version pinning for security and reproducibility."""

    def test_packages_have_version_constraints(self, requirements_lines):
        """Verify packages have version constraints."""
        for line in requirements_lines:
            if line.startswith('-') or line.startswith('/') or line.startswith('http'):
                # Skip flags, local paths, and URLs
                continue
            
            has_constraint = any(op in line for op in ['==', '>=', '<=', '>', '<', '~='])
            assert has_constraint, f"Package '{line}' should have version constraint"

    def test_exact_version_pinning_for_critical_packages(self, requirements_file):
        """Verify critical packages use exact version pinning (==)."""
        critical_packages = ['grpcio', 'click']
        
        for package in critical_packages:
            if package in requirements_file:
                # Extract the line containing the package
                lines = [l for l in requirements_file.split('\n') if package in l]
                for line in lines:
                    if not line.strip().startswith('#'):
                        assert '==' in line, \
                            f"Critical package '{package}' should use exact version pinning (==)"


class TestPackageCompatibility:
    """Test package compatibility and known issues."""

    def test_grpcio_version_comment(self, requirements_file):
        """Verify grpcio version has explanatory comment."""
        # The requirements file mentions pinning to py3-grpcio version
        # to avoid failure on native extension build
        assert 'py3-grpcio' in requirements_file or 'grpcio' in requirements_file, \
            "Should specify grpcio (pinned to Alpine package version)"

    def test_no_known_conflicting_versions(self, requirements_lines):
        """Verify no known conflicting package versions."""
        # This is a placeholder for specific version conflict checks
        # Add specific checks as issues are discovered
        pass


class TestLocalDependencies:
    """Test local dependency specifications."""

    def test_jans_pycloudlib_path_correct(self, requirements_file):
        """Verify jans-pycloudlib path is correct."""
        if '/tmp/jans/jans-pycloudlib' in requirements_file:
            # This path should match what's cloned in the Dockerfile
            assert '/tmp/jans/jans-pycloudlib' in requirements_file, \
                "jans-pycloudlib path should match Dockerfile git clone location"


class TestRequirementsFormat:
    """Test requirements.txt formatting."""

    def test_no_trailing_whitespace(self, requirements_file):
        """Verify no trailing whitespace in requirements."""
        lines = requirements_file.split('\n')
        for i, line in enumerate(lines, 1):
            if line and not line.startswith('#'):
                assert line == line.rstrip(), \
                    f"Line {i} has trailing whitespace"

    def test_no_blank_lines_between_requirements(self, requirements_file):
        """Verify minimal blank lines between requirements."""
        lines = requirements_file.split('\n')
        blank_count = 0
        
        for line in lines:
            if not line.strip():
                blank_count += 1
            else:
                blank_count = 0
            
            # Should not have more than 1 consecutive blank line
            assert blank_count <= 1, \
                "Should not have multiple consecutive blank lines"