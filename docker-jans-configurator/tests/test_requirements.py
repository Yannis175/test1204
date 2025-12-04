"""Tests for requirements.txt file."""
import re
import pytest


class TestRequirementsFile:
    """Test requirements.txt content and format."""

    def test_requirements_file_readable(self, requirements_content):
        """Verify requirements.txt is readable."""
        assert len(requirements_content) > 0, \
            "requirements.txt should not be empty"

    def test_grpcio_version_pinned(self, requirements_content):
        """Verify grpcio version is pinned."""
        assert "grpcio==" in requirements_content, \
            "grpcio should be pinned with =="
        
        # Extract version
        version_match = re.search(r'grpcio==(\d+\.\d+\.\d+)', requirements_content)
        assert version_match is not None, \
            "grpcio should have semantic version"

    def test_click_version_pinned(self, requirements_content):
        """Verify click version is pinned."""
        assert "click==" in requirements_content, \
            "click should be pinned with =="

    def test_pycloudlib_path(self, requirements_content):
        """Verify pycloudlib is referenced from correct path."""
        assert "/tmp/jans/jans-pycloudlib" in requirements_content, \
            "Should reference pycloudlib from /tmp/jans/jans-pycloudlib"

    def test_no_duplicate_packages(self, requirements_content):
        """Verify no duplicate package entries."""
        lines = [line.strip() for line in requirements_content.splitlines() 
                 if line.strip() and not line.strip().startswith('#')]
        
        # Extract package names (before == or other operators)
        packages = []
        for line in lines:
            if '==' in line:
                pkg = line.split('==')[0].strip()
            elif '>=' in line:
                pkg = line.split('>=')[0].strip()
            elif '<=' in line:
                pkg = line.split('<=')[0].strip()
            else:
                pkg = line.strip()
            packages.append(pkg.lower())
        
        assert len(packages) == len(set(packages)), \
            "requirements.txt should not have duplicate packages"

    def test_comments_for_pinned_versions(self, requirements_content):
        """Verify pinned versions have explanatory comments."""
        lines = requirements_content.splitlines()
        
        # Check if grpcio has a comment explaining the pin
        grpcio_idx = None
        for i, line in enumerate(lines):
            if 'grpcio==' in line:
                grpcio_idx = i
                break
        
        if grpcio_idx is not None:
            # Check if there's a comment nearby
            has_comment = False
            for i in range(max(0, grpcio_idx - 2), min(len(lines), grpcio_idx + 2)):
                if '#' in lines[i]:
                    has_comment = True
                    break
            
            assert has_comment, \
                "Pinned grpcio version should have explanatory comment"

    def test_requirements_format_valid(self, requirements_content):
        """Verify requirements file has valid format."""
        lines = [line.strip() for line in requirements_content.splitlines() 
                 if line.strip() and not line.strip().startswith('#')]
        
        # Each line should be either a package spec or a file path
        for line in lines:
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Check if it's a valid package specification or path
            is_valid = (
                '==' in line or 
                '>=' in line or 
                '<=' in line or 
                line.startswith('/') or 
                line.startswith('./')
            )
            assert is_valid, f"Line should be valid package spec or path: {line}"