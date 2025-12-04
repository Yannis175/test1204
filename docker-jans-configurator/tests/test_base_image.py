"""Tests for Docker base image validation and integrity."""
import re
import pytest


class TestBaseImage:
    """Test suite for validating the Docker base image."""

    def test_base_image_uses_liberica_jre_alpine(self, dockerfile_lines):
        """Verify that the base image uses Bellsoft Liberica OpenJRE Alpine."""
        from_line = dockerfile_lines[0]
        assert from_line.startswith("FROM"), "First line should be a FROM instruction"
        assert "bellsoft/liberica-openjre-alpine" in from_line, \
            "Base image should be bellsoft/liberica-openjre-alpine"

    def test_base_image_has_sha256_digest(self, dockerfile_lines):
        """Verify that the base image is pinned with SHA256 digest."""
        from_line = dockerfile_lines[0]
        assert "@sha256:" in from_line, \
            "Base image should be pinned with SHA256 digest for security"
        
        # Extract and validate SHA256 format
        sha_match = re.search(r'@sha256:([a-f0-9]{64})', from_line)
        assert sha_match is not None, \
            "SHA256 digest should be 64 hexadecimal characters"
        
        sha_digest = sha_match.group(1)
        assert len(sha_digest) == 64, "SHA256 digest should be exactly 64 characters"
        assert sha_digest.islower() or sha_digest.isdigit(), \
            "SHA256 digest should contain only lowercase hex characters"

    def test_base_image_version_format(self, dockerfile_lines):
        """Verify that the base image version follows expected format."""
        from_line = dockerfile_lines[0]
        
        # Check for version tag (e.g., 25-37 or 17.0.12)
        version_match = re.search(r'bellsoft/liberica-openjre-alpine:([^@]+)', from_line)
        assert version_match is not None, "Base image should have a version tag"
        
        version = version_match.group(1)
        assert len(version) > 0, "Version tag should not be empty"
        assert version not in ["latest", "edge"], \
            "Should use specific version, not 'latest' or 'edge'"

    def test_base_image_is_java_25(self, dockerfile_lines):
        """Verify that the base image is using Java 25 (not Java 17)."""
        from_line = dockerfile_lines[0]
        
        # The new version should be Java 25
        assert "25-" in from_line or ":25" in from_line, \
            "Base image should be using Java 25"
        
        # Should NOT be Java 17
        assert "17.0.12" not in from_line, \
            "Base image should not be using Java 17.0.12 (old version)"

    def test_base_image_alpine_variant(self, dockerfile_lines):
        """Verify that Alpine Linux variant is being used for smaller image size."""
        from_line = dockerfile_lines[0]
        assert "alpine" in from_line.lower(), \
            "Should use Alpine variant for minimal image size"

    @pytest.mark.parametrize("invalid_pattern", [
        "FROM.*:latest",
        "FROM.*:edge",
        "FROM [^@]*$",  # No SHA digest
    ])
    def test_base_image_does_not_match_invalid_patterns(
        self, dockerfile_lines, invalid_pattern
    ):
        """Verify base image doesn't match insecure or ambiguous patterns."""
        from_line = dockerfile_lines[0]
        assert not re.match(invalid_pattern, from_line), \
            f"Base image should not match pattern: {invalid_pattern}"

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

    def test_base_image_single_from_instruction(self, dockerfile_content):
        """Verify there is only one FROM instruction (single-stage build)."""
        from_instructions = re.findall(r'^FROM\s+', dockerfile_content, re.MULTILINE)
        assert len(from_instructions) == 1, \
            "Dockerfile should have exactly one FROM instruction"


class TestBaseImageSecurity:
    """Security-focused tests for the base image."""

    def test_base_image_from_trusted_registry(self, dockerfile_lines):
        """Verify base image comes from a trusted registry."""
        from_line = dockerfile_lines[0]
        
        # Check it's not from an untrusted source
        assert "docker.io" not in from_line or "bellsoft" in from_line, \
            "Should use official Bellsoft images"
        
        # Verify it's from Bellsoft
        assert "bellsoft" in from_line, \
            "Base image should be from Bellsoft (trusted vendor)"

    def test_no_generic_tags(self, dockerfile_lines):
        """Verify no generic tags like 'latest' are used."""
        from_line = dockerfile_lines[0]
        generic_tags = ["latest", "stable", "edge", "master", "main"]
        
        for tag in generic_tags:
            assert f":{tag}@" not in from_line and not from_line.endswith(f":{tag}"), \
                f"Should not use generic tag '{tag}'"

    def test_image_has_proper_digest_format(self, dockerfile_lines):
        """Verify the image digest follows proper format."""
        from_line = dockerfile_lines[0]
        
        # Should have format: image:tag@sha256:digest
        pattern = r'^FROM\s+[\w\-./]+:[\w\-./]+@sha256:[a-f0-9]{64}$'
        assert re.match(pattern, from_line), \
            "Base image should follow format: FROM image:tag@sha256:digest"


class TestJavaVersion:
    """Tests specific to Java version requirements."""

    def test_java_major_version_25(self, dockerfile_lines):
        """Verify Java 25 is explicitly specified."""
        from_line = dockerfile_lines[0]
        assert "25" in from_line, "Should explicitly use Java 25"

    def test_jre_not_jdk(self, dockerfile_lines):
        """Verify using JRE (not full JDK) for smaller image."""
        from_line = dockerfile_lines[0]
        assert "jre" in from_line.lower(), "Should use JRE for smaller footprint"
        assert "jdk" not in from_line.lower() or "openjre" in from_line.lower(), \
            "Should not use full JDK unless necessary"

    def test_java_home_symlink_exists(self, dockerfile_content):
        """Verify Java home symlink is created."""
        assert "ln -sf /usr/lib/jvm/jre /opt/java" in dockerfile_content, \
            "Should create symlink to Java installation"

    def test_cacerts_permissions(self, dockerfile_content):
        """Verify cacerts file has proper permissions."""
        assert "chmod 664 /opt/java/lib/security/cacerts" in dockerfile_content, \
            "Should set proper permissions on cacerts file"